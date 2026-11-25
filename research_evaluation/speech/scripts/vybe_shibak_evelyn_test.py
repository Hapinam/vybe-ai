"""Local Evelyn TTS pronunciation A/B: شباك vs شِبَاك.
Four short billable Azure Speech calls. No repo/PR/deployment changes.
Requires VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY.
"""
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

region = os.environ.get('VYBE_AZURE_SPEECH_REGION', '').strip()
key = os.environ.get('VYBE_AZURE_SPEECH_KEY', '').strip()
if not region or not key:
    sys.exit('Set VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY first.')
if not re.fullmatch(r'[a-z0-9-]+', region):
    sys.exit('Invalid region')

voice = 'en-US-EvelynMultilingualNeural'
examples = [
    ('01_plain', 'تسديدة قوية! هدف! يا سلام! الكرة في شباك هاربور United!'),
    ('02_shin_kasra', 'تسديدة قوية! هدف! يا سلام! الكرة في شِباك هاربور United!'),
    ('03_full_diacritics', 'تسديدة قوية! هدف! يا سلام! الكرة في شِبَاك هاربور United!'),
    ('04_full_match_context', 'أهلًا بكم في Vibe! أورورا إِفْ سِي يتقدم نحو المرمى. تسديدة قوية! هدف! الكرة في شِبَاك هاربور United!'),
]
output = Path('vybe_voice_samples') / 'shibak_evelyn'
output.mkdir(parents=True, exist_ok=True)
manifest = []
for label, text in examples:
    ssml = (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">'
        f'<voice name="{voice}"><prosody rate="+0%">{escape(text)}</prosody></voice></speak>'
    )
    request = Request(
        f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1',
        data=ssml.encode('utf-8'), method='POST',
        headers={
            'Ocp-Apim-Subscription-Key': key,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
            'User-Agent': 'VYBE-local-shibak-pronunciation-test',
        },
    )
    record = {'file': label + '.mp3', 'text': text, 'voice': voice}
    try:
        with urlopen(request, timeout=35) as response:
            data = response.read(2_000_001)
        if not 0 < len(data) <= 2_000_000:
            raise ValueError('Invalid audio size')
        (output / record['file']).write_bytes(data)
        record['status'] = 'ok'
        print('OK:', record['file'])
    except HTTPError as error:
        record['status'] = f'HTTP {error.code}'
        print('FAILED:', record['file'], record['status'])
    except (URLError, TimeoutError, ValueError) as error:
        record['status'] = type(error).__name__
        print('FAILED:', record['file'], record['status'])
    manifest.append(record)
(output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print('Output:', output)
