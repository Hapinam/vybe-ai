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


@pytest.mark.parametrize("language,expected", [
    ("en", "Vibe"),
    ("ar", "ڤايب"),
    ("cs", "Vibe"),
])
def test_brand_is_spoken_as_one_word(language, expected):
    assert _spoken_text("Welcome to VYBE!", language) == f"Welcome to {expected}!"


@pytest.mark.parametrize("time,expected", [
    ("00:15", "zero minutes and fifteen seconds"),
    ("12:10", "twelve minutes and ten seconds"),
    ("24:35", "twenty-four minutes and thirty-five seconds"),
    ("45:00", "forty-five minutes"),
    ("87:24", "eighty-seven minutes and twenty-four seconds"),
])
def test_english_match_clock_not_read_as_time_of_day(time, expected):
    assert _spoken_text(f"Goal at {time}.", "en") == f"Goal at {expected}."


@pytest.mark.parametrize("time,expected", [
    ("00:15", "0 minut a 15 sekund"),
    ("12:10", "12 minut a 10 sekund"),
    ("24:35", "24 minut a 35 sekund"),
    ("45:00", "45 minut"),
    ("87:24", "87 minut a 24 sekund"),
])
def test_czech_match_clock_has_explicit_minutes_and_seconds(time, expected):
    assert _spoken_text(f"Gól v {time}.", "cs") == f"Gól v {expected}."


def test_czech_speech_rate_is_reduced(monkeypatch):
    monkeypatch.setenv("VYBE_AZURE_SPEECH_KEY", "test-key")
    monkeypatch.setenv("VYBE_AZURE_SPEECH_REGION", "germanywestcentral")

    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, size): return b"fake-mp3"

    with patch("vybe.speech.urlopen", return_value=FakeResponse()) as mocked:
        synthesize("VYBE", "cs")
    assert b'rate="-10%"' in mocked.call_args.args[0].data
