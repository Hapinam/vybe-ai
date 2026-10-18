"""Produce a narrated MP4 from the locally recorded VYBE Playwright demo.

Windows: Python 3.10+, FFmpeg/ffprobe on PATH, built-in SAPI English voice.
No paid services or Python dependencies. Run from apps/web:
    python demo/produce_video.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "demo-output/record-demo-record-VYBE-feature-walkthrough/video.webm"
DEST = ROOT / "demo-output/VYBE-Every-Fan-Belongs.mp4"

# Narration is timed to the approximate sections in the 39.2-second walkthrough.
# Each cue is synthesized separately so it can start at the specified second.
CUES = [
    (0.5, "VYBE. Every fan belongs."),
    (4.0, "One football match. Three experiences, designed for every kind of fan."),
    (9.0, "Young fans celebrate the goals and test their football knowledge."),
    (17.0, "Accessible mode offers high contrast, larger text, and step by step navigation."),
    (28.0, "Analysts explore match statistics, momentum, insights, and the event timeline."),
    (36.0, "VYBE. Every fan belongs."),
]


def run(*args: str) -> str:
    p = subprocess.run(args, check=True, capture_output=True, text=True)
    return p.stdout


def synthesize(text: str, target: Path) -> None:
    # PowerShell's .NET System.Speech uses an installed Windows English voice.
    # Pass narration via base64 to avoid shell quoting issues.
    import base64
    payload = base64.b64encode(text.encode("utf-8")).decode("ascii")
    output_path = base64.b64encode(str(target).encode("utf-8")).decode("ascii")
    # Embed base64 values in the script rather than passing positional args
    # after -Command (which PowerShell does not bind as expected).
    ps = (
        "Add-Type -AssemblyName System.Speech; "
        f"$path = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{output_path}')); "
        f"$words = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{payload}')); "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "try { $s.Rate = 1; $s.SetOutputToWaveFile($path); $s.Speak($words) } "
        "finally { $s.Dispose() }"
    )
    # EncodedCommand also avoids Windows shell escaping problems.
    encoded = base64.b64encode(ps.encode("utf-16-le")).decode("ascii")
    run("powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded)


def main() -> None:
    if not SOURCE.is_file():
        sys.exit(f"Missing recording: {SOURCE}. Run the Playwright demo recorder first.")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        sys.exit("FFmpeg and ffprobe must be on PATH.")
    meta = json.loads(run("ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "json", str(SOURCE)))
    duration = float(meta["format"]["duration"])
    if not 35 <= duration <= 65:
        sys.exit(f"Unexpected recording duration ({duration:.1f}s); review narration timing.")

    DEST.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vybe-video-") as td:
        folder = Path(td)
        tracks = []
        for i, (start, text) in enumerate(CUES):
            wav = folder / f"voice_{i}.wav"
            synthesize(text, wav)
            voice_meta = json.loads(run("ffprobe", "-v", "error", "-show_entries",
                                        "format=duration", "-of", "json", str(wav)))
            voice_duration = float(voice_meta["format"]["duration"])
            next_start = CUES[i + 1][0] if i + 1 < len(CUES) else duration
            if start + voice_duration > next_start + 0.25:
                print(f"Warning: cue {i + 1} overlaps next scene; review the result.")
            tracks.append((start, wav))

        args = ["ffmpeg", "-y", "-i", str(SOURCE)]
        for _, wav in tracks:
            args.extend(["-i", str(wav)])
        filters = []
        for i, (start, _) in enumerate(tracks):
            ms = round(start * 1000)
            filters.append(f"[{i + 1}:a]adelay={ms}|{ms},volume=1.3[a{i}]")
        inputs = "".join(f"[a{i}]" for i in range(len(tracks)))
        filters.append(f"{inputs}amix=inputs={len(tracks)}:duration=longest:normalize=0,alimiter=limit=0.95[aout]")
        args.extend([
            "-filter_complex", ";".join(filters),
            "-map", "0:v:0", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-t", str(duration), "-movflags", "+faststart",
            str(DEST),
        ])
        print(f"Rendering {duration:.1f}s narrated MP4...", flush=True)
        subprocess.run(args, check=True)
    print(f"Finished: {DEST}")


if __name__ == "__main__":
    main()
