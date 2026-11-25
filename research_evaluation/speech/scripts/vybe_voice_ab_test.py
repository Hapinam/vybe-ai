"""Isolated VYBE pronunciation test. No repo or production changes.

Requires VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY environment variables.
Each test makes one short Azure Speech synthesis request (billable according to your plan).
"""
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REGION = os.getenv('VYBE_AZURE_SPEECH_REGION', '').strip()
KEY = os.getenv('VYBE_AZURE_SPEECH_KEY', '').strip()
if not REGION or not KEY:
    sys.exit('Set VYBE_AZURE_SPEECH_REGION and VYBE_AZURE_SPEECH_KEY locally first. Do not paste your key into chat.')
if not all(c.islower() or c.isdigit() or c == '-' for c in REGION):
    sys.exit('Invalid Azure region.')

prefix = 'أهلًا بكم في '
suffix = '. أورورا إف سي يواجه هاربور يونايتد.'
variants = {
    'A_phoneme': '<phoneme alphabet="ipa" ph="vaɪb">VYBE</phoneme>',
    'B_sub_alias': '<sub alias="ڤايب">VYBE</sub>',
    'C_plain_arabic': 'ڤايب',
}
folder = Path('vybe_voice_samples')
folder.mkdir(exist_ok=True)
for label, brand in variants.items():
    ssml = (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">'
        '<voice name="ar-EG-SalmaNeural"><prosody rate="+0%">'
        f'{prefix}{brand}{suffix}'
        '</prosody></voice></speak>'
    )
    req = Request(
        f'https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1',
        data=ssml.encode('utf-8'),
        headers={
            'Ocp-Apim-Subscription-Key': KEY,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
            'User-Agent': 'VYBE-voice-isolated-test',
        }, method='POST',
    )
    try:
        with urlopen(req, timeout=20) as res:
            audio = res.read(2_000_001)
        if len(audio) > 2_000_000:
            raise ValueError('Unexpected large audio response')
        if not audio:
            raise ValueError('Empty audio response')
        output = folder / f'{label}.mp3'
        output.write_bytes(audio)
        print(f'{label}: OK -> {output}')
    except HTTPError as exc:
        print(f'{label}: Azure returned HTTP {exc.code} (no secret displayed)')
    except (URLError, TimeoutError, ValueError) as exc:
        print(f'{label}: Failed: {type(exc).__name__}')
print('Listen to each file: check V sound, pauses, and continuity of Salma voice.')
