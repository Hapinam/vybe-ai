"""Offline regression tests for outbound HTTP security."""
import io
import json
import logging
import urllib.error
import urllib.request
from email.message import Message
from unittest.mock import patch
from urllib.response import addinfourl

import pytest
from fastapi import HTTPException

from vybe import ai, speech
from vybe.models import MatchDefinition
from vybe.secure_http import build_secure_opener


MARKER = "synthetic-sensitive-regression-marker"

AI_ENV = {
    "VYBE_AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
    "VYBE_AZURE_OPENAI_KEY": MARKER,
    "VYBE_AZURE_OPENAI_DEPLOYMENT": "demo",
}

SPEECH_ENV = {
    "VYBE_AZURE_SPEECH_REGION": "germanywestcentral",
    "VYBE_AZURE_SPEECH_KEY": MARKER,
}


def match():
    return MatchDefinition.model_validate({
        "match_id": "security-test",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "events": [{
            "id": "goal-1",
            "minute": 12,
            "team": "Aurora",
            "type": "goal",
        }],
    })


class TrackingResponse(io.BytesIO):
    def __init__(self, data):
        super().__init__(data)
        self.read_sizes = []

    def read(self, size=-1):
        self.read_sizes.append(size)
        return super().read(size)


def test_ai_accepts_response_at_exact_byte_limit():
    raw = json.dumps({
        "choices": [{"message": {"content": "ok"}}]
    }).encode()
    raw += b" " * (ai.MAX_RESPONSE_BYTES - len(raw))
    response = TrackingResponse(raw)

    with patch.dict("os.environ", AI_ENV, clear=True), patch(
        "urllib.request.OpenerDirector.open",
        return_value=response,
    ):
        assert ai._generate("test") == "ok"

    assert response.read_sizes == [ai.MAX_RESPONSE_BYTES + 1]


def test_ai_rejects_oversized_response_before_json_parsing():
    response = TrackingResponse(
        b"x" * (ai.MAX_RESPONSE_BYTES + 1)
    )

    with patch.dict("os.environ", AI_ENV, clear=True), patch(
        "urllib.request.OpenerDirector.open",
        return_value=response,
    ), patch("vybe.ai.json.loads") as parser:
        with pytest.raises(ai.ModelResponseError, match="Oversized"):
            ai._generate("test")

    parser.assert_not_called()
    assert response.read_sizes == [ai.MAX_RESPONSE_BYTES + 1]


def test_ai_oversized_response_preserves_fallback():
    with patch.dict("os.environ", AI_ENV, clear=True), patch(
        "urllib.request.OpenerDirector.open",
        return_value=io.BytesIO(
            b"x" * (ai.MAX_RESPONSE_BYTES + 1)
        ),
    ):
        result = ai.narrate_goal(match(), "goal-1")

    assert result["generation_mode"] == "deterministic"
    assert result["score"] == {"home": 1, "away": 0}
    assert result["evidence_event_ids"] == ["goal-1"]


@pytest.mark.parametrize("port", [80, 444, 8080, 65535])
def test_ai_rejects_nonstandard_https_ports(port):
    env = {
        **AI_ENV,
        "VYBE_AZURE_OPENAI_ENDPOINT":
            f"https://test.openai.azure.com:{port}",
    }

    with patch.dict("os.environ", env, clear=True), patch(
        "urllib.request.OpenerDirector.open"
    ) as send:
        with pytest.raises(ai.AzureConfigurationError):
            ai._generate("test")

    send.assert_not_called()


def test_ai_accepts_explicit_https_port_443():
    env = {
        **AI_ENV,
        "VYBE_AZURE_OPENAI_ENDPOINT":
            "https://test.openai.azure.com:443",
    }

    raw = b'{"choices":[{"message":{"content":"ok"}}]}'

    with patch.dict("os.environ", env, clear=True), patch(
        "urllib.request.OpenerDirector.open",
        return_value=io.BytesIO(raw),
    ):
        assert ai._generate("test") == "ok"


@pytest.mark.parametrize("code", [301, 302, 303, 307, 308])
@pytest.mark.parametrize("provider", ["ai", "speech"])
def test_azure_redirect_never_reaches_second_destination(
    code, provider
):
    requests = []

    class OfflineHTTPSHandler(urllib.request.BaseHandler):
        handler_order = 400

        def https_open(self, request):
            requests.append(request.full_url)

            if len(requests) != 1:
                raise AssertionError("Unexpected second request")

            headers = Message()
            headers["Location"] = "https://example.invalid/redirect"

            response = addinfourl(
                io.BytesIO(b""),
                headers,
                request.full_url,
                code=code,
            )
            response.msg = "Redirect"
            return response

    real_build = urllib.request.build_opener

    def offline_build(*handlers):
        return real_build(OfflineHTTPSHandler(), *handlers)

    env = AI_ENV if provider == "ai" else SPEECH_ENV

    with patch.dict("os.environ", env, clear=True), patch(
        "urllib.request.build_opener",
        side_effect=offline_build,
    ):
        if provider == "ai":
            with pytest.raises(urllib.error.HTTPError) as exc:
                ai._generate("test")
            assert exc.value.code == code
        else:
            with pytest.raises(HTTPException) as exc:
                speech.synthesize("Goal!", "en")
            assert exc.value.status_code == 502

    assert len(requests) == 1
    assert "example.invalid" not in requests[0]


def test_secure_opener_ignores_proxy_environment():
    proxies = {
        "HTTP_PROXY": "http://example.invalid:8080",
        "HTTPS_PROXY": "http://example.invalid:8080",
        "ALL_PROXY": "http://example.invalid:8080",
        "NO_PROXY": "",
    }

    real_build = urllib.request.build_opener

    with patch.dict("os.environ", proxies, clear=True), patch(
        "urllib.request.build_opener",
        wraps=real_build,
    ) as build:
        build_secure_opener()

    handlers = [
        handler for handler in build.call_args.args
        if isinstance(handler, urllib.request.ProxyHandler)
    ]

    assert len(handlers) == 1
    assert handlers[0].proxies == {}


@pytest.mark.parametrize("failure", [
    ai.AzureConfigurationError(MARKER),
    ai.ModelResponseError(MARKER),
    ValueError(MARKER),
    OSError(MARKER),
    RuntimeError(MARKER),
])
def test_ai_logs_never_include_raw_exception_content(
    failure, caplog
):
    with caplog.at_level(logging.WARNING), patch.dict(
        "os.environ", AI_ENV, clear=True
    ), patch("vybe.ai._generate", side_effect=failure):
        result = ai.narrate_goal(match(), "goal-1")

    assert result["generation_mode"] == "deterministic"
    assert MARKER not in caplog.text
    assert caplog.records
    assert all(not record.exc_info for record in caplog.records)


def test_speech_accepts_exact_audio_limit():
    response = TrackingResponse(b"x" * speech.MAX_AUDIO)

    with patch.dict("os.environ", SPEECH_ENV, clear=True), patch(
        "urllib.request.OpenerDirector.open",
        return_value=response,
    ):
        result = speech.synthesize("Goal!", "en")

    assert len(result) == speech.MAX_AUDIO
    assert response.read_sizes == [speech.MAX_AUDIO + 1]


def test_speech_rejects_oversized_audio():
    response = TrackingResponse(
        b"x" * (speech.MAX_AUDIO + 1)
    )

    with patch.dict("os.environ", SPEECH_ENV, clear=True), patch(
        "urllib.request.OpenerDirector.open",
        return_value=response,
    ):
        with pytest.raises(HTTPException) as exc:
            speech.synthesize("Goal!", "en")

    assert exc.value.status_code == 502
    assert exc.value.detail == "Speech response too large"
    assert response.read_sizes == [speech.MAX_AUDIO + 1]


def test_speech_suppresses_sensitive_provider_exception():
    with patch.dict("os.environ", SPEECH_ENV, clear=True), patch(
        "urllib.request.OpenerDirector.open",
        side_effect=urllib.error.URLError(MARKER),
    ):
        with pytest.raises(HTTPException) as exc:
            speech.synthesize("Goal!", "en")

    assert exc.value.status_code == 502
    assert MARKER not in str(exc.value)
    assert exc.value.__cause__ is None
    assert exc.value.__suppress_context__ is True
