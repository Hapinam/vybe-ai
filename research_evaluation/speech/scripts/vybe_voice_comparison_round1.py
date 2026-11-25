"""VYBE voice comparison — local audio only, no PR or deployment.
Uses the actual Azure voice inventory in vybe_voice_candidates.json.
Up to 24 short billable Azure TTS requests. No secrets logged.
"""
import json, os, re, sys, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from xml.sax.saxutils import escape

REGION=os.getenv("VYBE_AZURE_SPEECH_REGION","").strip()
KEY=os.getenv("VYBE_AZURE_SPEECH_KEY","").strip()
if not REGION or not KEY: sys.exit("Set VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY.")
if not re.fullmatch(r"[a-z0-9-]+", REGION): sys.exit("Invalid Azure region.")
inventory=Path("vybe_voice_candidates.json")
if not inventory.is_file(): sys.exit("Put vybe_voice_candidates.json beside this script.")
available={v["voice"]:v for v in json.loads(inventory.read_text(encoding="utf-8"))}
# 12 voices, including Egyptian baseline, Arabic female alternatives, and multilingual expressive candidates.
shortlist=[
"ar-EG-SalmaNeural","ar-EG-ShakirNeural",
"ar-LB-LaylaNeural","ar-JO-SanaNeural","ar-SA-ZariyahNeural",
"en-US-NancyMultilingualNeural","en-US-SerenaMultilingualNeural",
"zh-CN-XiaoxiaoMultilingualNeural",
"en-US-AvaMultilingualNeural","en-US-EmmaMultilingualNeural",
"en-US-AmandaMultilingualNeural","en-US-EvelynMultilingualNeural",
]
# Use Vibe for multilingual voices; Arabic voices get a phonetic approximation.
# Salma previously said F, and this is explicitly a baseline, not a solution.
welcome="أهلًا بكم في {brand}. أورورا إف سي يواجه هاربور يونايتد. يلا نبدأ الماتش!"
goal="جووول! يا سلام على الهدف! تسديدة صاروخية في الشباك! أورورا إف سي يتقدم بهدف مقابل لا شيء!"
out=Path("vybe_voice_samples")/"comparison_round1"
out.mkdir(parents=True,exist_ok=True)
manifest=[]
def render(voice, phrase, excited=False):
    v=available[voice]
    styles=v.get("style") or []
    body=escape(phrase)
    # Only request styles advertised in Azure inventory.
    if excited and "excited" in styles:
        body=f'<mstts:express-as style="excited">{body}</mstts:express-as>'
    # Avoid rate/pitch changes: test natural voice and supported style first.
    return ('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="ar-EG">'
            f'<voice name="{voice}">{body}</voice></speak>')
def synth(ssml):
    req=Request(f"https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),method="POST",headers={
        "Ocp-Apim-Subscription-Key":KEY,
        "Content-Type":"application/ssml+xml",
        "X-Microsoft-OutputFormat":"audio-24khz-48kbitrate-mono-mp3",
        "User-Agent":"VYBE-local-voice-comparison"})
    with urlopen(req,timeout=35) as resp: data=resp.read(2_000_001)
    if not 0<len(data)<=2_000_000: raise ValueError("Empty or oversized audio")
    return data
print("Voice comparison: up to 24 short billable TTS requests; no Azure configuration changes.")
for i,voice in enumerate(shortlist,1):
    if voice not in available:
        print("SKIP unavailable:",voice)
        continue
    v=available[voice]
    multilingual="Multilingual" in voice
    brand="Vibe" if multilingual else "فايب"
    for scenario,phrase,excited in [
        ("welcome",welcome.format(brand=brand),False),
        ("goal",goal,True),
    ]:
        label=f"{i:02d}_{voice}_{scenario}"
        record={"file":label+".mp3","voice":voice,"scenario":scenario,
                "style":"excited" if excited and "excited" in (v.get("style") or []) else "default",
                "brand_spoken":brand}
        try:
            data=synth(render(voice,phrase,excited))
            (out/record["file"]).write_bytes(data)
            record["status"]="ok"
            print("OK",label,record["style"])
        except HTTPError as e:
            record["status"]=f"HTTP {e.code}"
            print("FAIL",label,record["status"])
        except (URLError,TimeoutError,ValueError) as e:
            record["status"]=type(e).__name__
            print("FAIL",label,record["status"])
        manifest.append(record)
        time.sleep(0.15)
(out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("Done:",out)
print("Compare goal energy, Egyptian naturalness, brand V vs F, and continuity.")
