"""Isolated multilingual VYBE pronunciation test. Does not change the application.
Two short Azure Speech requests may incur usage charges. The original app is unchanged.
Requires VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY.
"""
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

region = os.environ.get("VYBE_AZURE_SPEECH_REGION", "").strip()
key = os.environ.get("VYBE_AZURE_SPEECH_KEY", "").strip()
if not region or not key:
    sys.exit("Missing Azure Speech environment variables. Do not share your key.")
if not re.fullmatch(r"[a-z0-9-]+", region):
    sys.exit("Invalid region.")

voices = {
    "F_Ava_Vibe": "en-US-AvaMultilingualNeural",
    "G_Emma_Vibe": "en-US-EmmaMultilingualNeural",
}
sentence = "أهلًا بكم في Vibe. أورورا إف سي يواجه هاربور يونايتد."
folder = Path("vybe_voice_samples")
folder.mkdir(exist_ok=True)
for label, voice in voices.items():
    ssml = (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">'
        f'<voice name="{voice}"><prosody rate="+0%">{sentence}</prosody></voice>'
        '</speak>'
    )
    req = Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": "VYBE-multilingual-isolated-test",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=25) as res:
            audio = res.read(2_000_001)
        if not audio or len(audio) > 2_000_000:
            raise ValueError("Empty or oversized audio")
        path = folder / f"{label}.mp3"
        path.write_bytes(audio)
        print(f"{label}: OK -> {path}")
    except HTTPError as exc:
        print(f"{label}: HTTP {exc.code} from Azure Speech")
    except (URLError, TimeoutError, ValueError) as exc:
        print(f"{label}: Failed ({type(exc).__name__})")
print("Listen for Vibe as one word, a V (not F), and continuous natural Arabic.")
