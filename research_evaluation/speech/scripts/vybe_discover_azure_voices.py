"""Discover Azure Speech voices in your resource/region; no audio synthesis.
Saves Arabic voices and multilingual voices advertising ar-EG support.
Do not share Azure keys. Only one GET request; no resources are modified.
"""
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

region = os.getenv("VYBE_AZURE_SPEECH_REGION", "").strip()
key = os.getenv("VYBE_AZURE_SPEECH_KEY", "").strip()
if not region or not key:
    sys.exit("Missing VYBE_AZURE_SPEECH_REGION or VYBE_AZURE_SPEECH_KEY.")
if not re.fullmatch(r"[a-z0-9-]+", region):
    sys.exit("Invalid region.")
url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list"
req = Request(url, headers={"Ocp-Apim-Subscription-Key": key}, method="GET")
try:
    with urlopen(req, timeout=20) as response:
        voices = json.load(response)
except HTTPError as exc:
    sys.exit(f"Azure Speech returned HTTP {exc.code}.")
except (URLError, TimeoutError, ValueError) as exc:
    sys.exit(f"Unable to retrieve voices: {type(exc).__name__}.")
if not isinstance(voices, list):
    sys.exit("Unexpected Azure voices response.")

def is_relevant(v):
    locale = v.get("Locale", "")
    secondaries = v.get("SecondaryLocaleList") or []
    return locale.startswith("ar-") or ("ar-EG" in secondaries and "Multilingual" in v.get("ShortName", ""))

rows = []
for v in voices:
    if not isinstance(v, dict) or not is_relevant(v):
        continue
    rows.append({
        "voice": v.get("ShortName", ""),
        "locale": v.get("Locale", ""),
        "gender": v.get("Gender", ""),
        "style": v.get("StyleList") or [],
        "supports_ar_EG": v.get("Locale") == "ar-EG" or "ar-EG" in (v.get("SecondaryLocaleList") or []),
    })
rows.sort(key=lambda x: (not x["locale"].startswith("ar-EG"), x["locale"], x["voice"]))
out = Path("vybe_voice_candidates.json")
out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Available relevant voices: {len(rows)}. Saved: {out}")
print("No TTS audio generated. No repository or Azure resource changes.")
