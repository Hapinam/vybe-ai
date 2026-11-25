"""Prepare VYBE Evelyn changes locally, guarded, no git/cloud writes."""
from pathlib import Path
import subprocess,sys
root=Path.cwd()
paths=['apps/api/vybe/speech.py','apps/api/tests/test_speech.py','apps/web/src/speechText.ts','apps/web/tests/speech-fallback.spec.ts']
for name in paths:
    if not (root/name).is_file(): sys.exit('Missing '+name+'; run from repo root')
if subprocess.run(['git','branch','--show-current'],capture_output=True,text=True,check=True).stdout.strip()!='fix/evelyn-arabic-commentary':
    sys.exit('Wrong branch. Nothing changed.')
if subprocess.run(['git','status','--porcelain','--',*paths],capture_output=True,text=True,check=True).stdout.strip():
    sys.exit('Target files are not clean. Nothing changed.')
data={name:(root/name).read_text(encoding='utf-8') for name in paths}
def change(name,old,new):
    s=data[name]
    if s.count(old)!=1: sys.exit(f'Unexpected {name} pattern {old[:75]!r}. Nothing changed.')
    data[name]=s.replace(old,new,1)
api,tests,web,wt=paths
change(api,'"ar": ("ar-EG", "ar-EG-SalmaNeural")','"ar": ("ar-EG", "en-US-EvelynMultilingualNeural")')
change(api,'"ڤايب" if language == "ar" else "Vibe"','"Vibe"')
change(api,'        text = re.sub(r"(?<![\\w])فايب(?![\\w])", "ڤايب", text)', '''        text = re.sub(r"(?<![\\w])(?:فايب|ڤايب)(?![\\w])", "Vibe", text)
        # Exact, tested demo names only; unknown names stay unchanged.
        text = re.sub(r"\\bAurora\\s+FC\\b", "أورورا إِفْ سِي", text, flags=re.I)
        text = re.sub(r"\\bHarbor\\s+United\\b", "هاربور United", text, flags=re.I)
        text = re.sub(r"(?<![\\w])أورورا\\s+إف\\s+سي(?![\\w])", "أورورا إِفْ سِي", text)
        text = re.sub(r"(?<![\\w])هاربور\\s+يونايتد(?![\\w])", "هاربور United", text)
        text = text.replace("هدف رائع في شباك", "هدف رائع في مرمى")
        text = re.sub(r"(?<![\\w])(?:جوووول|جووول|جوول|جول|جوون)(?![\\w])", "هدف", text)''')
s=data[api]; start=s.find('    if language == "ar":\n        # <lang> within an Arabic voice');end=s.find('    ssml = (',start)
if start<0 or end<0:sys.exit('SSML source changed. Nothing changed.')
data[api]=s[:start]+'''    # One continuous voice: no male voice inserts.
    voice_body = (
        f'<voice name="{voice}">'
        f'<prosody rate="{percentage:+d}%">{spoken}</prosody>'
        '</voice>'
    )
'''+s[end:]
change(tests,'("ar", "ڤايب")','("ar", "Vibe")')
s=data[tests];start=s.find('def test_egyptian_brand_uses_v_not_f(')
if start<0:sys.exit('Tests source changed. Nothing changed.')
data[tests]=s[:start]+'''def test_egyptian_brand_uses_v_not_f():
    assert _spoken_text("VYBE! vybe.", "ar") == "Vibe! Vibe."


def test_legacy_arabic_brand_is_normalized():
    assert _spoken_text("أهلًا بكم في فايب.", "ar") == "أهلًا بكم في Vibe."


def test_arabic_single_voice_and_escaping(monkeypatch):
    monkeypatch.setenv("VYBE_AZURE_SPEECH_KEY", "test-key")
    monkeypatch.setenv("VYBE_AZURE_SPEECH_REGION", "germanywestcentral")
    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, size): return b"fake-mp3"
    with patch("vybe.speech.urlopen", return_value=FakeResponse()) as mocked:
        assert synthesize("VYBE < & > فايب", "ar", 1.5) == b"fake-mp3"
    body = mocked.call_args.args[0].data.decode("utf-8")
    assert body.count("<voice ") == 1
    assert 'name="en-US-EvelynMultilingualNeural"' in body
    assert "GuyNeural" not in body and "SalmaNeural" not in body
    assert body.count('rate="+50%"') == 1
    assert "Vibe" in body and "&lt; &amp; &gt;" in body
    import xml.etree.ElementTree as ET
    ET.fromstring(body)


def test_tested_names_and_wording_are_audio_only():
    source = "Aurora FC ضد Harbor United، ثم Chelsea United. جوووول! هدف رائع في شباك هاربور يونايتد."
    result = _spoken_text(source, "ar")
    assert result == "أورورا إِفْ سِي ضد هاربور United، ثم Chelsea United. هدف! هدف رائع في مرمى هاربور United."
    assert "Aurora FC" in source and "Harbor United" in source
    assert _spoken_text("هز الشباك", "ar") == "هز الشباك"
'''
change(web,'language === "ar" ? "ڤايب" : "Vibe"','"Vibe"')
change(web,'  if (language === "ar") text = text.replace(/(^|[^\\p{L}\\p{N}_])فايب(?=$|[^\\p{L}\\p{N}_])/gu, "$1ڤايب");', '''  if (language === "ar") {
    text = text.replace(/(^|[^\\p{L}\\p{N}_])(?:فايب|ڤايب)(?=$|[^\\p{L}\\p{N}_])/gu, "$1Vibe");
    text = text.replace(/\\bAurora\\s+FC\\b/gi, "أورورا إِفْ سِي");
    text = text.replace(/\\bHarbor\\s+United\\b/gi, "هاربور United");
    text = text.replace(/(^|[^\\p{L}\\p{N}_])أورورا\\s+إف\\s+سي(?=$|[^\\p{L}\\p{N}_])/gu, "$1أورورا إِفْ سِي");
    text = text.replace(/(^|[^\\p{L}\\p{N}_])هاربور\\s+يونايتد(?=$|[^\\p{L}\\p{N}_])/gu, "$1هاربور United");
    text = text.replace(/هدف رائع في شباك/g, "هدف رائع في مرمى");
    text = text.replace(/(^|[^\\p{L}\\p{N}_])(?:جوووول|جووول|جوول|جول|جوون)(?=$|[^\\p{L}\\p{N}_])/gu, "$1هدف");
  }''')
change(wt,'expect(actual.brand).toBe("ڤايب! ڤايب.");','expect(actual.brand).toBe("Vibe! Vibe.");')
change(wt,'expect(actual.legacyBrand).toBe("أهلًا بكم في ڤايب.");','expect(actual.legacyBrand).toBe("أهلًا بكم في Vibe.");')
data[wt]+='''

test("Arabic fallback keeps unknown teams and normalizes demo names", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { browserSpeechText } = await import("/src/speechText.ts");
    return browserSpeechText("VYBE: Aurora FC ضد Harbor United، وChelsea United. جوووول! هدف رائع في شباك هاربور يونايتد.", "ar");
  });
  expect(result).toBe("Vibe: أورورا إِفْ سِي ضد هاربور United، وChelsea United. هدف! هدف رائع في مرمى هاربور United.");
});
'''
for name in [api,tests]:compile(data[name],name,'exec')
for name in paths:(root/name).write_text(data[name],encoding='utf-8')
print('Four files prepared locally. No commit, push, PR, merge or deployment.')
print('Review: git diff --check && git diff --stat && git diff')
