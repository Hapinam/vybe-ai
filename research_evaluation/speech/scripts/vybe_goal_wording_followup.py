"""Apply the agreed narrow Arabic football wording changes to an existing Evelyn branch.
No git operations, commits, cloud calls, or deployments.
"""
from pathlib import Path
import subprocess
import sys

root = Path.cwd()
branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True).stdout.strip()
if branch != "fix/evelyn-arabic-commentary":
    sys.exit(f"Wrong branch: {branch!r}. Nothing changed.")

paths = {
    "api": root / "apps/api/vybe/speech.py",
    "api_test": root / "apps/api/tests/test_speech.py",
    "web": root / "apps/web/src/speechText.ts",
    "web_test": root / "apps/web/tests/speech-fallback.spec.ts",
}
for name, path in paths.items():
    if not path.is_file():
        sys.exit(f"Missing {path}. Nothing changed.")
original = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
updated = dict(original)

def replace_once(name, old, new):
    n = updated[name].count(old)
    if n != 1:
        raise ValueError(f"{name}: expected 1 occurrence, found {n}: {old!r}. Nothing changed.")
    updated[name] = updated[name].replace(old, new, 1)

try:
    replace_once(
        "api",
        '        text = text.replace("هدف رائع في شباك", "هدف رائع في مرمى")',
        '        text = text.replace("هدف رائع في شباك", "هدف رائع في مرمى")\n'
        '        text = text.replace("هز الشباك", "سجّل هدفًا")',
    )
    replace_once(
        "web",
        '    text = text.replace(/هدف رائع في شباك/g, "هدف رائع في مرمى");',
        '    text = text.replace(/هدف رائع في شباك/g, "هدف رائع في مرمى");\n'
        '    text = text.replace(/هز الشباك/g, "سجّل هدفًا");',
    )
    replace_once(
        "api_test",
        '    assert _spoken_text("هز الشباك", "ar") == "هز الشباك"',
        '    assert _spoken_text("هز الشباك", "ar") == "سجّل هدفًا"\n'
        '    assert _spoken_text("هز الشباك", "en") == "هز الشباك"\n'
        '    assert _spoken_text("هز الشباك", "cs") == "هز الشباك"',
    )
    if "browser fallback rewrites football net idiom" in updated["web_test"]:
        raise ValueError("Web test already exists. Nothing changed.")
    updated["web_test"] += """
test("browser fallback rewrites football net idiom only for Arabic", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { browserSpeechText } = await import("/src/speechText.ts");
    return {
      arabic: browserSpeechText("هز الشباك! هدف رائع في شباك هاربور يونايتد.", "ar"),
      english: browserSpeechText("هز الشباك", "en"),
      czech: browserSpeechText("هز الشباك", "cs"),
    };
  });
  expect(result.arabic).toBe("سجّل هدفًا! هدف رائع في مرمى هاربور United.");
  expect(result.english).toBe("هز الشباك");
  expect(result.czech).toBe("هز الشباك");
});
"""
    compile(updated["api"], str(paths["api"]), "exec")
    compile(updated["api_test"], str(paths["api_test"]), "exec")
except (ValueError, SyntaxError) as exc:
    sys.exit(str(exc))

for name, path in paths.items():
    if updated[name] != original[name]:
        path.write_text(updated[name], encoding="utf-8")
        print("Updated", path.relative_to(root))
print("Done. No commit, push, PR, merge, or deployment.")
