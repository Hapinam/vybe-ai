"""Azure Speech adapter tests: no real Azure calls or secrets required."""
from unittest.mock import patch

from fastapi import HTTPException
import pytest

from vybe.speech import _spoken_text, synthesize


def test_goal_is_a_word_not_an_acronym():
    assert _spoken_text("GOOOAL! GOAL!", "en") == "Goal! Goal!"


def test_arabic_match_minute_includes_seconds_as_spoken_words():
    assert _spoken_text("هدف! Alex في الدقيقة 24:35.", "ar") == (
        "هدف! Alex في الدقيقة أربعة وعشرين وخمسة وتلاتين ثانية."
    )


def test_arabic_exact_minute_does_not_speak_zero_seconds():
    assert _spoken_text("هدف في الدقيقة 24:00.", "ar") == "هدف في الدقيقة أربعة وعشرين."


def test_arabic_early_match_time_is_not_confused_with_another_minute():
    assert _spoken_text("هدف في الدقيقة 12:10.", "ar") == (
        "هدف في الدقيقة اتناشر وعشرة ثواني."
    )


def test_missing_credentials_fail_closed(monkeypatch):
    monkeypatch.delenv("VYBE_AZURE_SPEECH_KEY", raising=False)
    monkeypatch.delenv("VYBE_AZURE_SPEECH_REGION", raising=False)
    with pytest.raises(HTTPException) as exc:
        synthesize("Goal!", "en")
    assert exc.value.status_code == 503


def test_speech_request_uses_ssml_and_returns_mp3(monkeypatch):
    monkeypatch.setenv("VYBE_AZURE_SPEECH_KEY", "test-key")
    monkeypatch.setenv("VYBE_AZURE_SPEECH_REGION", "germanywestcentral")

    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, size): return b"fake-mp3"

    with patch("vybe.speech.urlopen", return_value=FakeResponse()) as mocked:
        result = synthesize("GOAL!", "en")
    assert result == b"fake-mp3"
    request = mocked.call_args.args[0]
    assert b"Goal!" in request.data
    assert b"en-US-GuyNeural" in request.data
    assert b"GOAL!" not in request.data
