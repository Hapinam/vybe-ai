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
    ("00:15", "ve 0. minutě a 15. sekundě"),
    ("12:10", "ve 12. minutě a 10. sekundě"),
    ("24:35", "ve 24. minutě a 35. sekundě"),
    ("45:00", "ve 45. minutě"),
    ("87:24", "ve 87. minutě a 24. sekundě"),
])
def test_czech_match_clock_has_explicit_minutes_and_seconds(time, expected):
    assert _spoken_text(f"Gól, čas {time}.", "cs") == f"Gól, {expected}."


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


@pytest.mark.parametrize("clock,expected", [
    ("24:01", "في الدقيقة أربعة وعشرين وثانية واحدة"),
    ("24:02", "في الدقيقة أربعة وعشرين وثانيتين"),
    ("24:03", "في الدقيقة أربعة وعشرين وتلاتة ثواني"),
    ("24:11", "في الدقيقة أربعة وعشرين وحداشر ثانية"),
    ("87:24", "في الدقيقة سبعة وتمانين وأربعة وعشرين ثانية"),
])
def test_arabic_seconds_agreement(clock, expected):
    assert _spoken_text(f"هدف في الدقيقة {clock}", "ar") == f"هدف {expected}"


def test_czech_goal_caption_not_clock_time():
    assert _spoken_text("Gól! Alex, čas 24:35.", "cs") == (
        "Gól! Alex, ve 24. minutě a 35. sekundě."
    )


def test_invalid_seconds_not_treated_as_match_clock():
    assert _spoken_text("Goal at 24:75.", "en") == "Goal at 24:75."


def test_xml_escape_and_english_clock(monkeypatch):
    monkeypatch.setenv("VYBE_AZURE_SPEECH_KEY", "test-key")
    monkeypatch.setenv("VYBE_AZURE_SPEECH_REGION", "germanywestcentral")
    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, size): return b"fake-mp3"
    with patch("vybe.speech.urlopen", return_value=FakeResponse()) as mocked:
        synthesize("VYBE & Goal at 24:35.", "en")
    body = mocked.call_args.args[0].data.decode("utf-8")
    assert "Vibe &amp; Goal at twenty-four minutes and thirty-five seconds" in body
    assert "24:35" not in body


@pytest.mark.parametrize("clock,expected", [
    ("24:12", "في الدقيقة أربعة وعشرين واتناشر ثانية"),
    ("24:35", "في الدقيقة أربعة وعشرين وخمسة وتلاتين ثانية"),
    ("45:00", "في الدقيقة خمسة وأربعين"),
])
def test_egyptian_match_clock_natural_conjunction(clock, expected):
    assert _spoken_text(f"هدف في الدقيقة {clock}", "ar") == f"هدف {expected}"


def test_egyptian_brand_uses_v_not_f():
    assert _spoken_text("VYBE! vybe.", "ar") == "ڤايب! ڤايب."
