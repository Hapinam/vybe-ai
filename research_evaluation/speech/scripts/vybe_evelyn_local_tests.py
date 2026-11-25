"""Update existing backend speech tests for single-voice Evelyn. Run at repo root."""
from pathlib import Path
import subprocess,sys
p=Path('apps/api/tests/test_speech.py')
if not p.is_file():sys.exit('Run at vybe-ai root')
if subprocess.run(['git','status','--porcelain','--',str(p)],capture_output=True,text=True,check=True).stdout.strip():sys.exit('Existing changes in tests; refusing overwrite')
s=p.read_text(encoding='utf-8')
def once(a,b):
 global s
 if s.count(a)!=1:sys.exit('Unexpected test source; no changes: '+repr(a))
 s=s.replace(a,b,1)
once('("ar", "ڤايب")','("ar", "Vibe")')
start=s.index('def test_egyptian_brand_uses_v_not_f():')
s=s[:start]+'''def test_egyptian_brand_uses_v_not_f():
    assert _spoken_text("VYBE! vybe.", "ar") == "Vibe! Vibe."


def test_legacy_arabic_brand_is_normalized():
    assert _spoken_text("أهلًا بكم في فايب وڤايب.", "ar") == "أهلًا بكم في Vibe وVibe."


def test_team_names_only_known_demo_names_are_rewritten():
    text = "Aurora FC ضد Harbor United وChelsea United."
    assert _spoken_text(text, "ar") == "أورورا إِفْ سِي ضد هاربور United وChelsea United."
    assert text == "Aurora FC ضد Harbor United وChelsea United."


def test_goal_phrases_do_not_change_other_contexts():
    assert _spoken_text("جووول! هدف رائع في شباك هاربور يونايتد.", "ar") == (
        "هدف! هدف رائع في مرمى هاربور United."
    )
    assert _spoken_text("هز الشباك", "ar") == "هز الشباك"


def test_arabic_uses_one_evelyn_voice_with_escaping_and_rate(monkeypatch):
    monkeypatch.setenv("VYBE_AZURE_SPEECH_KEY", "test-key")
    monkeypatch.setenv("VYBE_AZURE_SPEECH_REGION", "germanywestcentral")

    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, size): return b"fake-mp3"

    with patch("vybe.speech.urlopen", return_value=FakeResponse()) as mocked:
        assert synthesize("VYBE & Harbor United < Aurora FC", "ar", 1.5) == b"fake-mp3"
    body = mocked.call_args.args[0].data.decode("utf-8")
    assert body.count("<voice ") == 1
    assert 'name="en-US-EvelynMultilingualNeural"' in body
    assert "GuyNeural" not in body and "SalmaNeural" not in body
    assert 'rate="+50%"' in body
    assert "Vibe" in body and "هاربور United" in body
    assert "&amp;" in body and "&lt;" in body
    import xml.etree.ElementTree as ET
    ET.fromstring(body)
'''
compile(s,str(p),'exec')
p.write_text(s,encoding='utf-8')
print('Updated backend tests locally. No commits, PR, merge or deployment.')
