"""Test Salma with spoken brand 'Vibe' (not VYBE), no voice switching.
Uses one short Azure Speech request. No GitHub or deployment changes.
"""
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

region = os.getenv("VYBE_AZURE_SPEECH_REGION", "").strip()
key = os.getenv("VYBE_AZURE_SPEECH_KEY", "").strip()
if not region or not key:
    sys.exit("Set VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY in this CMD session.")
if not re.fullmatch(r"[a-z0-9-]+", region):
    sys.exit("Invalid Azure Speech region.")

ssml = (
    '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">'
    '<voice name="ar-EG-SalmaNeural">'
    '<prosody rate="+0%">'
    'أهلًا بكم في Vibe. أورورا إف سي يواجه هاربور يونايتد.'
    '</prosody></voice></speak>'
)
request = Request(
    f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
    data=ssml.encode("utf-8"),
    headers={
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
        "User-Agent": "VYBE-isolated-Salma-test",
    },
    method="POST",
)
try:
    with urlopen(request, timeout=25) as response:
        audio = response.read(2_000_001)
    if not audio or len(audio) > 2_000_000:
        sys.exit("Empty or oversized audio response")
    folder = Path("vybe_voice_samples")
    folder.mkdir(exist_ok=True)
    target = folder / "H_Salma_Vibe.mp3"
    target.write_bytes(audio)
    print(f"OK -> {target}")
    print("Compare H_Salma_Vibe.mp3 with G_Emma_Vibe.mp3: V pronunciation, Egyptian accent, continuity.")
except HTTPError as exc:
    sys.exit(f"Azure Speech HTTP error: {exc.code}")
except (URLError, TimeoutError) as exc:
    sys.exit(f"Azure Speech connection error: {type(exc).__name__}")
