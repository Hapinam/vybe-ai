"""VYBE: isolated full acceptance test for Emma Multilingual Azure Speech.
No application, GitHub, or Azure resource changes. Makes six short billable TTS requests.
Environment: VYBE_AZURE_SPEECH_REGION, VYBE_AZURE_SPEECH_KEY.
"""
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

REGION = os.getenv("VYBE_AZURE_SPEECH_REGION", "").strip()
KEY = os.getenv("VYBE_AZURE_SPEECH_KEY", "").strip()
if not REGION or not KEY:
    sys.exit("Missing VYBE_AZURE_SPEECH_REGION / VYBE_AZURE_SPEECH_KEY in this CMD session.")
if not re.fullmatch(r"[a-z0-9-]+", REGION):
    sys.exit("Invalid Azure Speech region.")

VOICE = "en-US-EmmaMultilingualNeural"
OUT = Path("vybe_voice_samples") / "emma_full"
OUT.mkdir(parents=True, exist_ok=True)
# Text is the *spoken* variant; app captions can still display VYBE.
# Avoid SSML voice switching and special pronunciation tags.
SCENARIOS = [
    ("01_welcome", "أهلًا بكم في Vibe. أورورا إف سي يواجه هاربور يونايتد. يلا نبدأ الماتش!", 1.00),
    ("02_build_up", "أورورا بيضغط بقوة! تمريرة في العمق، والمهاجم داخل منطقة الجزاء، يا ترى هيسدد؟", 1.06),
    ("03_goal_excited", "جوووول! يا سلام على الهدف! تسديدة رائعة في الشباك! أورورا إف سي يتقدم بهدف مقابل لا شيء!", 1.18),
    ("04_clock_score", "في الدقيقة خمسة وأربعين وثلاثين ثانية، النتيجة واحد لواحد، والمباراة لسه فيها كتير!", 1.00),
    ("05_names_english", "هاربور يونايتد بيهاجم، وأورورا إف سي بيرد بسرعة. Vibe معاكم لحظة بلحظة!", 1.00),
    ("06_brand_twice", "أهلًا بكم في Vibe. هنا Vibe، والتعليق مستمر من غير تغيير في صوت المعلّقة.", 1.00),
]

def synthesize(label, sentence, rate):
    percentage = round((rate - 1.0) * 100)
    ssml = (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">'
        f'<voice name="{VOICE}"><prosody rate="{percentage:+d}%">'
        f'{escape(sentence)}'
        '</prosody></voice></speak>'
    )
    request = Request(
        f"https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        headers={
            "Ocp-Apim-Subscription-Key": KEY,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": "VYBE-Emma-full-acceptance-test",
        },
        method="POST",
    )
    with urlopen(request, timeout=25) as response:
        audio = response.read(2_000_001)
    if not audio or len(audio) > 2_000_000:
        raise ValueError("Empty or oversized audio")
    path = OUT / f"{label}.mp3"
    path.write_bytes(audio)
    return path

print(f"Testing {VOICE}: {len(SCENARIOS)} short Azure Speech requests.")
print("This may incur usage charges. No deployment or repository changes.")
for label, sentence, rate in SCENARIOS:
    try:
        path = synthesize(label, sentence, rate)
        print(f"{label}: OK -> {path}")
    except HTTPError as error:
        print(f"{label}: HTTP {error.code} (details withheld)")
    except (URLError, TimeoutError, ValueError) as error:
        print(f"{label}: FAILED ({type(error).__name__})")
    time.sleep(0.2)
print(f"Done. Listen to files in: {OUT}")
print("Judge: V sound, Egyptian accent, player/team names, excitement, pace, and continuity.")
