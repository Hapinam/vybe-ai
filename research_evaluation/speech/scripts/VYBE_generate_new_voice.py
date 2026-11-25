"""Generate VYBE cinematic narration using your existing Azure Speech F0 resource.
Read-only Azure resource lookup; synthesizes speech against your Speech resource.
Run from Windows CMD with Azure CLI logged in. Never prints or stores the key.
"""
import json, subprocess, urllib.request, urllib.parse, xml.sax.saxutils, pathlib, sys
GROUP = "rg-vybe-hackathon"
NAME = "vybe-speech"
VOICE = "en-US-EvelynMultilingualNeural"
SEGMENTS = [
    ("01_opening", "Football brings us together. But every fan experiences the game differently. Meet Vibe: one match, three ways to feel every moment."),
    ("02_young", "For young fans, Vibe makes football playful and easy to understand, with celebrations, simple explanations, and interactive moments."),
    ("03_accessible", "For accessible experiences, Vibe offers clear captions, high contrast, keyboard-friendly controls, and spoken commentary."),
    ("04_analyst", "For analysts, Vibe turns recorded match events into transparent, evidence-grounded insights, without inventing tactical explanations."),
    ("05_foundry", "Microsoft Foundry powers grounded match questions. Every supported answer points back to specific synthetic events, with clear evidence and no unsupported claims."),
    ("06_speech", "Azure Speech brings the match to life in multiple languages, including expressive Arabic commentary. Vibe makes every moment easier to follow."),
    ("07_closing", "One fictional match. Three inclusive experiences. Vibe. Every fan belongs. Every moment matters."),
]
def az(*args):
    return subprocess.check_output(["az.cmd", *args, "-o", "json"], text=True)
def main():
    info=json.loads(az("cognitiveservices","account","show","-g",GROUP,"-n",NAME))
    region=info["location"]
    keys=json.loads(az("cognitiveservices","account","keys","list","-g",GROUP,"-n",NAME))
    key=keys["key1"]
    out=pathlib.Path("VYBE_new_voice")
    out.mkdir(exist_ok=True)
    for label, line in SEGMENTS:
        ssml=(f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
              f'<voice name="{VOICE}"><prosody rate="0%">{xml.sax.saxutils.escape(line)}</prosody></voice></speak>')
        req=urllib.request.Request(f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",data=ssml.encode("utf-8"),headers={"Ocp-Apim-Subscription-Key":key,"Content-Type":"application/ssml+xml","X-Microsoft-OutputFormat":"audio-24khz-96kbitrate-mono-mp3","User-Agent":"VYBE-Hackathon-Demo"},method="POST")
        with urllib.request.urlopen(req, timeout=35) as response:
            (out/(label+".mp3")).write_bytes(response.read())
        print(f"Created {label}.mp3")
    print("DONE: Upload the 7 MP3 files from VYBE_new_voice (ZIP is fine).")
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("ERROR:",type(exc).__name__,str(exc)[:400]);sys.exit(1)
