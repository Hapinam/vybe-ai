"""Prepare VYBE Evelyn speech backend locally. No GitHub writes, commits, or deployment."""
from pathlib import Path
import subprocess, sys
root=Path.cwd()
p=root/'apps/api/vybe/speech.py'
if not p.is_file(): sys.exit('Run from the vybe-ai repository root.')
if subprocess.run(['git','status','--porcelain','--','apps/api/vybe/speech.py'],capture_output=True,text=True,check=True).stdout.strip():
    sys.exit('speech.py has local changes; refusing to overwrite.')
s=p.read_text(encoding='utf-8')
def once(old,new):
    global s
    if s.count(old)!=1: sys.exit('Source differs from reviewed revision; no files changed: '+repr(old[:70]))
    s=s.replace(old,new,1)
once('"ar": ("ar-EG", "ar-EG-SalmaNeural")','"ar": ("ar-EG", "en-US-EvelynMultilingualNeural")')
once('"ڤايب" if language == "ar" else "Vibe"','"Vibe"')
once('''        text = re.sub(r"(?<![\\w])فايب(?![\\w])", "ڤايب", text)''','''        text = re.sub(r"(?<![\\w])(?:فايب|ڤايب)(?![\\w])", "Vibe", text)
        # Known demo-team names only. Preserve all unknown teams unchanged.
        text = re.sub(r"\\bAurora\\s+FC\\b", "أورورا إِفْ سِي", text, flags=re.I)
        text = re.sub(r"\\bHarbor\\s+United\\b", "هاربور United", text, flags=re.I)
        text = re.sub(r"(?<![\\w])أورورا\\s+إف\\s+سي(?![\\w])", "أورورا إِفْ سِي", text)
        text = re.sub(r"(?<![\\w])هاربور\\s+يونايتد(?![\\w])", "هاربور United", text)
        text = text.replace("هدف رائع في شباك", "هدف رائع في مرمى")
        text = re.sub(r"(?<![\\w])(?:جوووول|جووول|جوول|جول|جوون)(?![\\w])", "هدف", text)''')
start=s.index('    if language == "ar":\n        # <lang> within an Arabic voice')
end=s.index('    ssml = (',start)
s=s[:start]+'''    # Keep the same female voice across the entire utterance.
    voice_body = (
        f'<voice name="{voice}">'
        f'<prosody rate="{percentage:+d}%">{spoken}</prosody>'
        '</voice>'
    )
'''+s[end:]
compile(s,str(p),'exec')
p.write_text(s,encoding='utf-8')
print('Updated backend speech.py locally. NO commit/PR/merge/deployment.')
print('IMPORTANT: existing test_speech.py expects the old voices and must be updated before tests pass.')
print('Review: git diff -- apps/api/vybe/speech.py')
