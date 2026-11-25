"""Isolated VYBE welcome wording A/B test. Six short Azure TTS requests.
No repo changes, PR, merge, Azure configuration changes, or deployment.
Requires VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY in environment.
"""
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

region = os.getenv('VYBE_AZURE_SPEECH_REGION', '').strip()
key = os.getenv('VYBE_AZURE_SPEECH_KEY', '').strip()
if not region or not key:
    sys.exit('Set VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY first.')
if not re.fullmatch(r'[a-z0-9-]+', region):
    sys.exit('Invalid Azure Speech region.')

voices = {
    'Evelyn': 'en-US-EvelynMultilingualNeural',
    'Amanda': 'en-US-AmandaMultilingualNeural',
}
phrases = {
    'A_sports_arabic': 'أهلًا بيكم في Vibe! اليوم، يواجه أورورا إف سي فريق هاربور يونايتد. انطلقت المباراة، والجمهور متحمس. خلّونا نشوف مين هيحقق الفوز!',
    'B_natural_arabic': 'أهلًا بيكم في Vibe! أورورا إف سي في مواجهة هاربور يونايتد النهارده. المباراة بدأت، والجمهور متحمس!',
    'C_short_direct': 'أهلًا بيكم في Vibe! أورورا إف سي ضد هاربور يونايتد. المباراة بدأت! مين هيكسب النهارده؟',
}
output = Path('vybe_voice_samples') / 'welcome_wording_ab'
output.mkdir(parents=True, exist_ok=True)
manifest = []

for voice_label, voice_name in voices.items():
    for case_label, spoken_text in phrases.items():
        filename = f'{voice_label}_{case_label}.mp3'
        ssml = (
            '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">'
            f'<voice name="{voice_name}">{escape(spoken_text)}</voice></speak>'
        )
        request = Request(
            f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1',
            data=ssml.encode('utf-8'),
            headers={
                'Ocp-Apim-Subscription-Key': key,
                'Content-Type': 'application/ssml+xml',
                'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
                'User-Agent': 'VYBE-local-wording-test',
            },
            method='POST',
        )
        item = {'voice': voice_label, 'case': case_label, 'file': filename, 'spoken_text': spoken_text}
        try:
            with urlopen(request, timeout=35) as response:
                audio = response.read(2_000_001)
            if not 0 < len(audio) <= 2_000_000:
                raise ValueError('Unexpected audio size')
            (output / filename).write_bytes(audio)
            item['status'] = 'ok'
            print('OK', filename)
        except HTTPError as error:
            item['status'] = f'HTTP {error.code}'
            print('FAILED', filename, item['status'])
        except (URLError, TimeoutError, ValueError) as error:
            item['status'] = type(error).__name__
            print('FAILED', filename, item['status'])
        manifest.append(item)
        time.sleep(0.15)

(output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print('Done:', output)
print('Six short TTS requests may incur small Azure Speech usage charges.')
print('Compare A/B/C pronunciation, clarity, and naturalness. No application changes.')
