"""Local Evelyn test: شُبَّاك vs مرمى. No repository edits or deployment.
Requires VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY.
3 short billable Azure TTS requests.
"""
import json, os, re, sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from xml.sax.saxutils import escape

region = os.environ.get('VYBE_AZURE_SPEECH_REGION', '').strip()
key = os.environ.get('VYBE_AZURE_SPEECH_KEY', '').strip()
if not region or not key:
    sys.exit('Missing VYBE_AZURE_SPEECH_REGION or VYBE_AZURE_SPEECH_KEY.')
if not re.fullmatch(r'[a-z0-9-]+', region):
    sys.exit('Invalid Azure region.')

voice = 'en-US-EvelynMultilingualNeural'
cases = [
    ('01_shubbak', 'تسديدة قوية! هدف! يا سلام! هدف رائع في شُبَّاك هاربور United!'),
    ('02_alshubbak', 'تسديدة قوية! هدف! يا سلام! الكرة في الشُّبَّاك! أورورا إِفْ سِي يتقدم!'),
    ('03_marma', 'تسديدة قوية! هدف! يا سلام! هدف رائع في مرمى هاربور United!'),
]
out = Path('vybe_voice_samples') / 'shubbak_final_ab'
out.mkdir(parents=True, exist_ok=True)
manifest = []
for label, phrase in cases:
    ssml = ('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">'
            f'<voice name="{voice}"><prosody rate="+8%">{escape(phrase)}</prosody></voice></speak>')
    req = Request(f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1',
                  data=ssml.encode('utf-8'), method='POST', headers={
                      'Ocp-Apim-Subscription-Key': key,
                      'Content-Type': 'application/ssml+xml',
                      'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
                      'User-Agent': 'VYBE-local-shubbak-test',
                  })
    entry = {'file': f'{label}.mp3', 'text': phrase}
    try:
        with urlopen(req, timeout=35) as response:
            data = response.read(2_000_001)
        if not 0 < len(data) <= 2_000_000:
            raise ValueError('Empty or oversized audio response')
        (out / entry['file']).write_bytes(data)
        entry['status'] = 'ok'
        print('OK:', out / entry['file'])
    except HTTPError as exc:
        entry['status'] = f'HTTP {exc.code}'
        print('FAIL:', label, entry['status'])
    except (URLError, TimeoutError, ValueError) as exc:
        entry['status'] = type(exc).__name__
        print('FAIL:', label, entry['status'])
    manifest.append(entry)
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print('Done:', out)
