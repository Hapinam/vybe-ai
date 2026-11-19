"""Offline contract and security tests for the native Ollama adapter."""

import io
import json
from unittest.mock import patch

import pytest

from vybe.director_ollama import _configuration, _select_tool


def reply(calls):
    return io.BytesIO(
        json.dumps({"message": {"tool_calls": calls}}).encode("utf-8")
    )


def tool(name, arguments=None):
    return {
        "function": {
            "name": name,
            "arguments": {} if arguments is None else arguments,
        }
    }


def test_valid_tool_call():
    with patch(
        "vybe.director_ollama.urllib.request.OpenerDirector.open",
        return_value=reply([tool("get_match_state")]),
    ) as mocked:
        assert _select_tool("What is the score?") == "get_match_state"

    request = mocked.call_args.args[0]
    payload = json.loads(request.data)

    assert request.full_url == "http://127.0.0.1:11434/api/chat"
    assert payload["model"] == "qwen3-coder:30b"
    assert payload["stream"] is False
    assert payload["think"] is False
    assert len(payload["tools"]) == 4
    assert mocked.call_args.kwargs["timeout"] == 30


@pytest.mark.parametrize(
    "calls",
    [
        [],
        [tool("get_match_state"), tool("get_key_moments")],
        [tool("run_shell")],
        [tool("get_match_state", {"command": "delete"})],
        [tool("get_match_state", "not-json")],
    ],
)
def test_invalid_tool_calls_rejected(calls):
    with patch(
        "vybe.director_ollama.urllib.request.OpenerDirector.open",
        return_value=reply(calls),
    ):
        with pytest.raises((ValueError, json.JSONDecodeError)):
            _select_tool("What happened?")


def test_timeout_propagates_to_caller():
    with patch(
        "vybe.director_ollama.urllib.request.OpenerDirector.open",
        side_effect=TimeoutError("timeout"),
    ):
        with pytest.raises(TimeoutError):
            _select_tool("Who scored?")


def test_oversized_response_rejected():
    oversized = io.BytesIO(b"x" * 32769)

    with patch(
        "vybe.director_ollama.urllib.request.OpenerDirector.open",
        return_value=oversized,
    ):
        with pytest.raises(ValueError, match="Oversized"):
            _select_tool("Who scored?")


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://example.com:11434",
        "http://127.0.0.1:11434/evil",
        "https://127.0.0.1:11434",
        "http://user:pass@127.0.0.1:11434",
    ],
)
def test_unsafe_endpoints_rejected(monkeypatch, endpoint):
    monkeypatch.setenv("VYBE_OLLAMA_BASE_URL", endpoint)

    with pytest.raises(ValueError, match="Invalid local"):
        _configuration()


def test_direct_configuration_override_rejected():
    with pytest.raises(ValueError, match="override"):
        _select_tool("test", ("http://example.com:11434", "model"))



@pytest.mark.parametrize(
    "payload",
    [
        b"not-json",
        b"{}",
        b"[]",
        b"null",
        b'{"message": null}',
        b'{"message": {}}',
        b'{"message": {"tool_calls": null}}',
        b'{"message": {"tool_calls": "invalid"}}',
        b'{"message": {"tool_calls": [null]}}',
        b'{"message": {"tool_calls": [{"function": null}]}}',
    ],
)
def test_malformed_ollama_response_rejected(payload):
    with patch(
        "vybe.director_ollama.urllib.request.OpenerDirector.open",
        return_value=io.BytesIO(payload),
    ):
        with pytest.raises(ValueError):
            _select_tool("What is the score?")




def test_ollama_redirect_rejected():
    import urllib.error
    import urllib.request

    requested_urls = []

    class FakeHTTPHandler(urllib.request.BaseHandler):
        handler_order = 400

        def http_open(self, request):
            requested_urls.append(request.full_url)
            if request.full_url != "http://127.0.0.1:11434/api/chat":
                raise AssertionError("Unexpected outbound request")

            from email.message import Message
            from urllib.response import addinfourl

            headers = Message()
            headers["Location"] = "https://example.com/redirected"

            response = addinfourl(
                io.BytesIO(b""),
                headers,
                request.full_url,
                code=302,
            )
            response.msg = "Found"
            return response

    real_build_opener = urllib.request.build_opener

    def offline_build_opener(*handlers):
        return real_build_opener(FakeHTTPHandler(), *handlers)

    with patch(
        "vybe.director_ollama.urllib.request.build_opener",
        side_effect=offline_build_opener,
    ):
        with pytest.raises(urllib.error.HTTPError) as exc:
            _select_tool("What is the score?")

    assert exc.value.code == 302
    assert requested_urls == ["http://127.0.0.1:11434/api/chat"]



def test_ollama_ignores_proxy_environment(monkeypatch):
    import urllib.request

    monkeypatch.setenv("HTTP_PROXY", "http://example.com:8080")
    monkeypatch.setenv("HTTPS_PROXY", "http://example.com:8080")

    captured_handlers = []

    def fake_build_opener(*handlers):
        captured_handlers.extend(handlers)

        class FakeOpener:
            def open(self, request, timeout):
                return reply([tool("get_match_state")])

        return FakeOpener()

    with patch(
        "vybe.director_ollama.urllib.request.build_opener",
        side_effect=fake_build_opener,
    ):
        assert _select_tool("What is the score?") == "get_match_state"

    proxy_handlers = [
        handler for handler in captured_handlers
        if isinstance(handler, urllib.request.ProxyHandler)
    ]

    assert len(proxy_handlers) == 1
    assert proxy_handlers[0].proxies == {}
