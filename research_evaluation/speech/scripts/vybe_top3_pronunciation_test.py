"""VYBE isolated Azure Speech A/B test: Evelyn, Amanda, Emma.
Tests match pronunciation, goal calls, emotion and brand V.
Up to 30 short billable Azure Speech calls; no PR, merge or deployment.
Requires VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY.
"""
import os, re, json, sys, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from xml.sax.saxutils import escape

REGION=os.getenv("VYBE_AZURE_SPEECH_REGION","").strip()
KEY=os.getenv("VYBE_AZURE_SPEECH_KEY","").strip()
if not REGION or not KEY: sys.exit("Missing VYBE_AZURE_SPEECH_REGION / VYBE_AZURE_SPEECH_KEY.")
if not re.fullmatch(r"[a-z0-9-]+",REGION): sys.exit("Invalid region")
VOICES=[
    "en-US-EvelynMultilingualNeural",
    "en-US-AmandaMultilingualNeural",
    "en-US-EmmaMultilingualNeural",
]
# Keep only one voice throughout every utterance. Never add male voice or switch.
# The tests are deliberately independent to isolate pronunciation changes.
CASES=[
    ("01_match_mubara", "المباراة لسه فيها كتير، والنتيجة واحد لواحد.", 0, "Default pronunciation of مباراة"),
    ("02_match_diacritics", "المُبَارَاة لِسَّه فِيهَا كْتِير، والنَّتِيجَة وَاحِد لِوَاحِد.", 0, "Diacritics to guide مباراة"),
    ("03_match_almatch", "الماتش لسه فيه كتير، والنتيجة واحد لواحد.", 0, "Egyptian alternative الماتش"),
    ("04_goal_jool", "جوووول! يا سلام على الهدف! تسديدة في الشباك!", 0, "Extended جول baseline"),
    ("05_goal_gol", "جول! جول! يا سلام على الهدف!", 0, "Short جول"),
    ("06_goal_goon", "جووون! يا سلام على الهدف! تسديدة في الشباك!", 0, "Egyptian جوون"),
    ("07_goal_hadaf", "هدف! يا سلام! هدف عالمي! تسديدة صاروخية في الشباك!", 0, "Arabic هدف"),
    ("08_excited_fast", "يا نهار أبيض! إيه التسديدة دي! هدف عالمي! أورورا إف سي يتقدم!", 12, "Higher pace, no unsupported expressive style"),
    ("09_excited_punct", "يا سلام!!! يا سلام على الهدف!!! أورورا سجل! الجمهور مولّع الدنيا!", 0, "Expressive punctuation"),
    ("10_full_brand", "أهلًا بيكم في Vibe! الماتش مولّع! فرصة خطيرة، تسديدة، هدف! يا سلام على الجمال!", 6, "Realistic one-voice sample, V sound and energy"),
]
OUT=Path("vybe_voice_samples")/"top3_pronunciation"
OUT.mkdir(parents=True,exist_ok=True)
manifest=[]
def synth(voice, text, rate):
    # Escaping is essential for any future dynamic text.
    ssml=(
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">'
        f'<voice name="{voice}"><prosody rate="{rate:+d}%">{escape(text)}</prosody></voice>'
        '</speak>'
    )
    req=Request(f"https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),method="POST",headers={
        "Ocp-Apim-Subscription-Key":KEY,
        "Content-Type":"application/ssml+xml",
        "X-Microsoft-OutputFormat":"audio-24khz-48kbitrate-mono-mp3",
        "User-Agent":"VYBE-local-pronunciation-test",
    })
    with urlopen(req,timeout=35) as resp:
        data=resp.read(2_000_001)
    if not 0<len(data)<=2_000_000: raise ValueError("Empty or oversized audio")
    return data
print("TOP 3: Evelyn, Amanda, Emma | 10 tests each = up to 30 Azure Speech calls.")
print("No application, GitHub, or Azure resource configuration changes.")
for voice in VOICES:
    for label,phrase,rate,objective in CASES:
        filename=f"{voice}_{label}.mp3"
        entry={"file":filename,"voice":voice,"case":label,"text":phrase,
               "rate_percent":rate,"objective":objective}
        try:
            (OUT/filename).write_bytes(synth(voice,phrase,rate))
            entry["status"]="ok"
            print("OK",filename)
        except HTTPError as exc:
            entry["status"]=f"HTTP {exc.code}"
            print("FAIL",filename,entry["status"])
        except (URLError,TimeoutError,ValueError) as exc:
            entry["status"]=type(exc).__name__
            print("FAIL",filename,entry["status"])
        manifest.append(entry)
        time.sleep(0.15)
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("Results:",OUT)
print("Compare each voice's files 01-03, 04-07, 08-09, then 10.")
