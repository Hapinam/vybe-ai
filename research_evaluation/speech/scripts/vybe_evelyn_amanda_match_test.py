"""VYBE: isolated full-match narration A/B, Evelyn vs Amanda.
6 short Azure Speech requests (3 per voice). No GitHub, PR or deployment.
Set VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY in CMD.
"""
import os, re, sys, json, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from xml.sax.saxutils import escape

region=os.getenv("VYBE_AZURE_SPEECH_REGION","").strip()
key=os.getenv("VYBE_AZURE_SPEECH_KEY","").strip()
if not region or not key:
    sys.exit("Missing VYBE_AZURE_SPEECH_REGION / VYBE_AZURE_SPEECH_KEY.")
if not re.fullmatch(r"[a-z0-9-]+",region):
    sys.exit("Invalid region.")
voices=["en-US-EvelynMultilingualNeural","en-US-AmandaMultilingualNeural"]
# 02_match_diacritics inspired the diacritized match term. No "الماتش" or "جول".
# The same complete script is used for both voices. Only speech text uses "Vibe".
scenes=[
 ("01_kickoff", """أهلًا بيكم في Vibe! النهارده أورورا إف سي بيواجه هاربور يونايتد. المُبَارَاة بدأت، والجمهور متحمس. يلا نشوف مين هيفوز!""", 0),
 ("02_attack_goal", """أورورا بيضغط بقوة. تمريرة سريعة في العمق! المهاجم داخل منطقة الجزاء. بيسدد! هَدَف! يا سلام! هدف عالمي! تسديدة صاروخية في الشباك! أورورا إف سي بيتقدم بهدف مقابل لا شيء!""", 8),
 ("03_score_finish", """وصلنا للدقيقة خمسة وأربعين. هاربور يونايتد رجع في النتيجة، وبقت واحد لواحد. المُبَارَاة لسه فيها فرص كتير. فرصة أخيرة لأورورا! تسديدة! الحارس يتصدى! يا لها من نهاية مثيرة!""", 0),
]
out=Path("vybe_voice_samples")/"finalists_match"
out.mkdir(parents=True,exist_ok=True)
manifest=[]
def get_audio(voice,text,rate):
    ssml=('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">'
          f'<voice name="{voice}"><prosody rate="{rate:+d}%">{escape(text)}</prosody></voice></speak>')
    req=Request(f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),method="POST",headers={
        "Ocp-Apim-Subscription-Key":key,
        "Content-Type":"application/ssml+xml",
        "X-Microsoft-OutputFormat":"audio-24khz-48kbitrate-mono-mp3",
        "User-Agent":"VYBE-local-match-comparison"})
    with urlopen(req,timeout=35) as response:
        data=response.read(2_000_001)
    if not 0<len(data)<=2_000_000:
        raise ValueError("Empty or oversized audio")
    return data

print("Evelyn vs Amanda: 6 short billable Azure TTS calls. No PR/deployment.")
for voice in voices:
    for scene,text,rate in scenes:
        name=f"{voice}_{scene}.mp3"
        row={"voice":voice,"scene":scene,"file":name,"rate_percent":rate,"text":text}
        try:
            (out/name).write_bytes(get_audio(voice,text,rate))
            row["status"]="ok"
            print("OK:",name)
        except HTTPError as exc:
            row["status"]=f"HTTP {exc.code}"
            print("FAILED:",name,row["status"])
        except (URLError,TimeoutError,ValueError) as exc:
            row["status"]=type(exc).__name__
            print("FAILED:",name,row["status"])
        manifest.append(row)
        time.sleep(0.15)
(out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("Finished. Listen in:",out)
print("Check pronunciation of Vibe, المُبَارَاة, هَدَف, names, and emotional delivery.")
