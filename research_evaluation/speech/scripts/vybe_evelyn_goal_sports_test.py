"""Isolated VYBE Evelyn goal commentary test: 5 short Azure Speech TTS requests.
No changes to repository, PR, deployment or Azure configuration.
Set VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY beforehand.
"""
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

region = os.getenv('VYBE_AZURE_SPEECH_REGION', '').strip()
key = os.getenv('VYBE_AZURE_SPEECH_KEY', '').strip()
if not region or not key:
    sys.exit('Missing VYBE_AZURE_SPEECH_REGION / VYBE_AZURE_SPEECH_KEY.')
if not re.fullmatch(r'[a-z0-9-]+', region):
    sys.exit('Invalid Azure Speech region.')

voice = 'en-US-EvelynMultilingualNeural'
output = Path('vybe_voice_samples') / 'evelyn_goal_sports'
output.mkdir(parents=True, exist_ok=True)
# All five use the SAME voice and the same simple sports Arabic register.
# Compare naturalness and emotional delivery without voice switches.
cases = [
    ('01_goal_baseline', 'أورورا إف سي يتقدم نحو المرمى. تمريرة رائعة داخل منطقة الجزاء. تسديدة! هَدَف! يا سلام! هدف رائع في شباك هاربور يونايتد!', 0),
    ('02_goal_faster', 'أورورا إف سي يتقدم نحو المرمى. تمريرة رائعة داخل منطقة الجزاء. تسديدة! هَدَف! يا سلام! هدف رائع في شباك هاربور يونايتد!', 12),
    ('03_goal_short_phrases', 'فرصة خطيرة لأورورا! الكرة داخل منطقة الجزاء! تسديدة قوية! هَدَف! هدف رائع! الجمهور يحتفل!', 6),
    ('04_goal_dramatic', 'يا لها من فرصة! المهاجم ينفرد بالمرمى! يسدد الآن! هَدَف! يا له من هدف مذهل! أورورا يتقدم!', 8),
    ('05_full_transition', 'أهلًا بيكم في Vibe! اليوم يواجه أورورا إف سي فريق هاربور يونايتد. انطلقت المباراة، والجمهور متحمس. أورورا يهاجم الآن! تمريرة داخل منطقة الجزاء! تسديدة! هَدَف! هدف رائع! أورورا يتقدم بهدف مقابل لا شيء!', 6),
]

def synthesize(text, rate):
    ssml = (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">'
        f'<voice name="{voice}"><prosody rate="{rate:+d}%">{escape(text)}</prosody></voice>'
        '</speak>'
    )
    request = Request(
        f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1',
        data=ssml.encode('utf-8'), method='POST', headers={
            'Ocp-Apim-Subscription-Key': key,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
            'User-Agent': 'VYBE-Evelyn-local-goal-test',
        },
    )
    with urlopen(request, timeout=35) as response:
        audio = response.read(2_000_001)
    if not 0 < len(audio) <= 2_000_000:
        raise ValueError('Empty or oversized audio.')
    return audio

print('Evelyn goal test: up to 5 short billable Azure TTS requests; no deployment.')
manifest = []
for name, text, rate in cases:
    entry = {'name': name, 'voice': voice, 'text': text, 'rate_percent': rate}
    try:
        (output / f'{name}.mp3').write_bytes(synthesize(text, rate))
        entry['status'] = 'ok'
        print('OK:', name)
    except HTTPError as error:
        entry['status'] = f'HTTP {error.code}'
        print('FAILED:', name, entry['status'])
    except (URLError, TimeoutError, ValueError) as error:
        entry['status'] = type(error).__name__
        print('FAILED:', name, entry['status'])
    manifest.append(entry)
(output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print('Audio folder:', output)
