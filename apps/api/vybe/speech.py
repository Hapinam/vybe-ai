"""Server-side Azure Speech synthesis: consistent audio across browsers and devices.

The Speech resource key is server-only. No text or credentials are logged.
"""
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

from fastapi import HTTPException

VOICES = {
    "en": ("en-US", "en-US-GuyNeural"),
    "ar": ("ar-EG", "ar-EG-SalmaNeural"),
    "cs": ("cs-CZ", "cs-CZ-AntoninNeural"),
}
MAX_TEXT = 1200
MAX_AUDIO = 2_000_000

_ARABIC_NUMBERS = {
    0: "صفر", 1: "واحد", 2: "اتنين", 3: "تلاتة", 4: "أربعة",
    5: "خمسة", 6: "ستة", 7: "سبعة", 8: "تمانية", 9: "تسعة",
    10: "عشرة", 11: "حداشر", 12: "اتناشر", 13: "تلتاشر",
    14: "أربعتاشر", 15: "خمستاشر", 16: "ستاشر", 17: "سبعتاشر",
    18: "تمنتاشر", 19: "تسعتاشر", 20: "عشرين", 30: "تلاتين",
    40: "أربعين", 50: "خمسين", 60: "ستين", 70: "سبعين",
    80: "تمانين", 90: "تسعين",
}


def _arabic_cardinal(value: int) -> str:
    """Render a football-clock number as words for Egyptian Arabic TTS."""
    if value in _ARABIC_NUMBERS:
        return _ARABIC_NUMBERS[value]
    if 21 <= value <= 99:
        units, tens = value % 10, (value // 10) * 10
        return f"{_ARABIC_NUMBERS[units]} و{_ARABIC_NUMBERS[tens]}"
    if 100 <= value <= 120:
        return "مية" if value == 100 else f"مية و{_arabic_cardinal(value - 100)}"
    # Keep unexpected but valid numeric text readable rather than failing synthesis.
    return str(value)


def _spoken_text(text: str, language: str) -> str:
    # Convert football-clock timestamps to spoken language, not colon-separated
    # digits. Arabic commentary retains seconds and spells both numbers out.
    if language == "ar":
        def arabic_time(match: re.Match[str]) -> str:
            minute, second = int(match.group(1)), int(match.group(2))
            spoken_minute = _arabic_cardinal(minute)
            if second == 0:
                return f"في الدقيقة {spoken_minute}"
            seconds_unit = "ثواني" if 3 <= second <= 10 else "ثانية"
            if second == 1:
                seconds_unit = "ثانية"
            elif second == 2:
                seconds_unit = "ثانيتين"
            return f"في الدقيقة {spoken_minute} و{_arabic_cardinal(second)} {seconds_unit}"

        text = re.sub(r"في الدقيقة\s+(\d{1,3}):(\d{2})", arabic_time, text)
    else:
        text = re.sub(r"\bGOOO+A+L\b|\bGOAL\b", "Goal", text, flags=re.I)
    return text


def synthesize(text: str, language: str, rate: float = 1.0) -> bytes:
    region = os.environ.get("VYBE_AZURE_SPEECH_REGION", "").strip()
    key = os.environ.get("VYBE_AZURE_SPEECH_KEY", "").strip()
    if not region or not key:
        raise HTTPException(503, "Cloud speech is not configured")
    if language not in VOICES:
        raise HTTPException(422, "Unsupported speech language")
    if not text.strip() or len(text) > MAX_TEXT:
        raise HTTPException(422, "Invalid speech text length")
    if not (0.5 <= rate <= 2.0):
        raise HTTPException(422, "Invalid speech rate")
    if not re.fullmatch(r"[a-z0-9-]+", region):
        raise HTTPException(503, "Invalid speech region configuration")

    locale, voice = VOICES[language]
    spoken = escape(_spoken_text(text, language))
    percentage = round((rate - 1) * 100)
    ssml = (
        f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        f'xml:lang="{locale}"><voice name="{voice}">'
        f'<prosody rate="{percentage:+d}%">{spoken}</prosody>'
        '</voice></speak>'
    )
    request = Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": "VYBE",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=12) as response:
            audio = response.read(MAX_AUDIO + 1)
            if len(audio) > MAX_AUDIO:
                raise HTTPException(502, "Speech response too large")
            return audio
    except (HTTPError, URLError, TimeoutError) as exc:
        raise HTTPException(502, "Speech service unavailable") from exc
