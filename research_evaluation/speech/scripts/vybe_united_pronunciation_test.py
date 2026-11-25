"""Isolated Evelyn test for pronunciation of United.
Five short, billable Azure Speech calls; no repository/deployment changes.
"""
import os,re,sys,json,time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from xml.sax.saxutils import escape
region=os.getenv("VYBE_AZURE_SPEECH_REGION","").strip()
key=os.getenv("VYBE_AZURE_SPEECH_KEY","").strip()
if not region or not key: sys.exit("Set VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY.")
if not re.fullmatch("[a-z0-9-]+",region): sys.exit("Invalid region.")
voice="en-US-EvelynMultilingualNeural"
variants=[
 ("01_plain","هاربور يونايتد"),
 ("02_diacritics","هاربور يُونَايْتِدْ"),
 ("03_final_d","هاربور يونايتدْ"),
 ("04_latin","هاربور United"),
 ("05_followed_word","هاربور يونايتد اليوم"),
]
out=Path("vybe_voice_samples")/"united_pronunciation"
out.mkdir(parents=True,exist_ok=True)
manifest=[]
for name,team in variants:
    phrase=f"هدف رائع في مرمى {team}! أورورا إِفْ سِي يتقدم!"
    ssml=('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">'
          f'<voice name="{voice}">{escape(phrase)}</voice></speak>')
    req=Request(f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),method="POST",headers={
        "Ocp-Apim-Subscription-Key":key,
        "Content-Type":"application/ssml+xml",
        "X-Microsoft-OutputFormat":"audio-24khz-48kbitrate-mono-mp3",
        "User-Agent":"VYBE-united-local-test"})
    record={"file":name+".mp3","team_spoken":team,"text":phrase}
    try:
        with urlopen(req,timeout=35) as response: data=response.read(2_000_001)
        if not 0<len(data)<=2_000_000: raise ValueError("Empty or oversized audio")
        (out/record["file"]).write_bytes(data)
        record["status"]="ok"
        print("OK",record["file"])
    except HTTPError as exc:
        record["status"]=f"HTTP {exc.code}"
        print("FAIL",name,record["status"])
    except (URLError,TimeoutError,ValueError) as exc:
        record["status"]=type(exc).__name__
        print("FAIL",name,record["status"])
    manifest.append(record)
    time.sleep(.15)
(out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("Done:",out)
print("Check whether the final D in United is audible, without awkward stress.")
