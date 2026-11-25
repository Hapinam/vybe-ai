"""Isolated VYBE Azure Speech pronunciation test. No PR, merge, deployment or resource changes.
Requires VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY in environment.
Generates 5 short billable audio clips with Evelyn only.
"""
import os
import re
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from xml.sax.saxutils import escape

region = os.getenv('VYBE_AZURE_SPEECH_REGION', '').strip()
key = os.getenv('VYBE_AZURE_SPEECH_KEY', '').strip()
if not region or not key:
    sys.exit('Missing VYBE_AZURE_SPEECH_REGION or VYBE_AZURE_SPEECH_KEY.')
if not re.fullmatch(r'[a-z0-9-]+', region):
    sys.exit('Invalid Azure Speech region.')

voice = 'en-US-EvelynMultilingualNeural'
output = Path('vybe_voice_samples') / 'final_pronunciation_ab'
output.mkdir(parents=True, exist_ok=True)

# All changes are to speech text only; the UI/data can retain Aurora FC and VYBE.
scenarios = [
    ('01_fc_plain', 'أورورا إف سي يتقدم نحو المرمى. تمريرة رائعة داخل منطقة الجزاء. تسديدة! هدف! يا سلام! هدف رائع في مرمى هاربور يونايتد!', 0),
    ('02_fc_full_diacritics', 'أورورا إِفْ سِي يتقدم نحو المرمى. تمريرة رائعة داخل منطقة الجزاء. تسديدة! هدف! يا سلام! هدف رائع في مرمى هاربور يونايتد!', 0),
    ('03_fc_light_diacritics', 'أورورا إفْ سي يتقدم نحو المرمى. تمريرة رائعة داخل منطقة الجزاء. تسديدة! هدف! يا سلام! هدف رائع في مرمى هاربور يونايتد!', 0),
    ('04_fc_english_letters', 'أورورا F C يتقدم نحو المرمى. تمريرة رائعة داخل منطقة الجزاء. تسديدة! هدف! يا سلام! هدف رائع في مرمى هاربور يونايتد!', 0),
    ('05_full_context', 'أهلًا بيكم في Vibe! اليوم يواجه أورورا إِفْ سِي فريق هاربور يونايتد. انطلقت المباراة! أورورا يتقدم نحو المرمى. تمريرة رائعة داخل منطقة الجزاء. تسديدة! هدف! يا سلام! هدف رائع في مرمى هاربور يونايتد!', 0),
]

results = []
print('Evelyn: 5 short Azure TTS requests. No repository or production changes.')
for label, spoken, rate in scenarios:
    ssml = (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">'
        f'<voice name="{voice}"><prosody rate="{rate:+d}%">{escape(spoken)}</prosody></voice></speak>'
    )
    request = Request(
        f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1',
        data=ssml.encode('utf-8'),
        headers={
            'Ocp-Apim-Subscription-Key': key,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
            'User-Agent': 'VYBE-local-pronunciation-ab',
        },
        method='POST',
    )
    result = {'scenario': label, 'spoken_text': spoken, 'voice': voice}
    try:
        with urlopen(request, timeout=35) as response:
            data = response.read(2_000_001)
        if not 0 < len(data) <= 2_000_000:
            raise ValueError('Empty or oversized response')
        filename = f'{label}.mp3'
        (output / filename).write_bytes(data)
        result.update(status='ok', file=filename)
        print('OK', filename)
    except HTTPError as exc:
        result['status'] = f'HTTP {exc.code}'
        print('FAILED', label, result['status'])
    except (URLError, TimeoutError, ValueError) as exc:
        result['status'] = type(exc).__name__
        print('FAILED', label, result['status'])
    results.append(result)
(output / 'manifest.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print('Finished:', output)
