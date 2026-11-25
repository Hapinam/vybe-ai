"""Offline regression tests for Foundry Director transport security."""

import io
import json
import logging
import urllib.error
import urllib.request
from unittest.mock import Mock, patch

import pytest

from vybe import director_agent
from vybe.models import MatchDefinition
from vybe.secure_http import build_secure_opener


CONFIG = (
    "https://example.openai.azure.com",
    "synthetic-test-key",
    "test-model",
)

MATCH = MatchDefinition.model_validate({
    "match_id": "foundry-security",
    "home_team": "Aurora",
    "away_team": "Harbor",
    "events": [
        {
            "id": "g1",
            "minute": 10,
            "team": "Aurora",
            "type": "goal",
        },
    ],
})


@pytest.fixture(autouse=True)
def foundry_environment(monkeypatch):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", "foundry")
    monkeypatch.setenv("VYBE_FOUNDRY_MODEL_ENDPOINT", CONFIG[0])
    monkeypatch.setenv("VYBE_FOUNDRY_MODEL_KEY", CONFIG[1])
    monkeypatch.setenv("VYBE_FOUNDRY_MODEL_DEPLOYMENT", CONFIG[2])


@pytest.mark.parametrize("port", ["", ":443"])
def test_valid_https_ports(monkeypatch, port):
    endpoint = CONFIG[0] + port
    monkeypatch.setenv("VYBE_FOUNDRY_MODEL_ENDPOINT", endpoint)
    assert director_agent._configuration()[0] == endpoint


@pytest.mark.parametrize("port", [":80", ":8443", ":invalid", ":65536"])
def test_invalid_https_ports(monkeypatch, port):
    monkeypatch.setenv(
        "VYBE_FOUNDRY_MODEL_ENDPOINT",
        CONFIG[0] + port,
    )
    with pytest.raises(ValueError):
        director_agent._configuration()


def test_transport_uses_shared_secure_opener():
    opener = Mock()
    request = urllib.request.Request(CONFIG[0])

    with patch(
        "vybe.director_agent.build_secure_opener",
        return_value=opener,
    ) as factory:
        result = director_agent._open_model_response(
            request, timeout=6
        )

    factory.assert_called_once_with()
    opener.open.assert_called_once_with(request, timeout=6)
    assert result is opener.open.return_value


def test_secure_opener_disables_environment_proxy(monkeypatch):
    monkeypatch.setenv(
        "HTTPS_PROXY", "http://proxy.invalid:8080"
    )
    opener = build_secure_opener()

    handlers = [
        h for h in opener.handlers
        if isinstance(h, urllib.request.ProxyHandler)
    ]
    assert all(not h.proxies for h in handlers)


def test_secure_opener_rejects_redirect():
    from email.message import Message
    from urllib.response import addinfourl

    opener = build_secure_opener()

    handler = next(
        h for h in opener.handlers
        if isinstance(h, urllib.request.HTTPSHandler)
    )

    headers = Message()
    headers["Location"] = "https://example.invalid/"

    response = addinfourl(
        io.BytesIO(b""),
        headers,
        CONFIG[0],
        code=302,
    )
    response.msg = "Found"

    request = urllib.request.Request(CONFIG[0])

    with patch.object(
        handler,
        "https_open",
        return_value=response,
    ) as transport:
        with pytest.raises(urllib.error.HTTPError) as error:
            opener.open(request, timeout=6)

        assert error.value.code == 302
        transport.assert_called_once_with(request)


def valid_reply():
    return json.dumps({
        "choices": [{
            "message": {
                "tool_calls": [{
                    "type": "function",
                    "function": {
                        "name": "get_match_state",
                        "arguments": "{}",
                    },
                }],
            },
        }],
    }).encode()


def test_exact_response_limit_accepted():
    payload = valid_reply().ljust(8192, b" ")

    with patch(
        "vybe.director_agent._open_model_response",
        return_value=io.BytesIO(payload),
    ) as transport:
        result = director_agent._select_tool(
            "What is the score?", CONFIG
        )

    assert result == "get_match_state"
    assert transport.call_args.kwargs["timeout"] == 6


def test_oversized_response_rejected():
    payload = valid_reply().ljust(8193, b" ")

    with patch(
        "vybe.director_agent._open_model_response",
        return_value=io.BytesIO(payload),
    ):
        with pytest.raises(ValueError, match="Oversized"):
            director_agent._select_tool(
                "What is the score?", CONFIG
            )


@pytest.mark.parametrize(
    "error",
    [
        ValueError("SYNTHETIC-SENSITIVE-MARKER"),
        TimeoutError("SYNTHETIC-SENSITIVE-MARKER"),
    ],
)
def test_provider_errors_do_not_leak(error, caplog):
    with caplog.at_level(logging.WARNING):
        with patch(
            "vybe.director_agent._select_tool",
            side_effect=error,
        ):
            result = director_agent.director_ask(
                MATCH, "What is the score?"
            )

    assert result["generation_mode"] == "deterministic"
    assert result["selected_tool"] is None
    assert "SYNTHETIC-SENSITIVE-MARKER" not in caplog.text
    assert type(error).__name__ in caplog.text


def test_malformed_provider_json_does_not_leak(caplog):
    payload = json.dumps({
        "choices": [{
            "message": {
                "tool_calls": [{
                    "type": "function",
                    "function": {
                        "name": "get_match_state",
                        "arguments": "SYNTHETIC-SENSITIVE-MARKER",
                    },
                }],
            },
        }],
    }).encode()

    with caplog.at_level(logging.WARNING):
        with patch(
            "vybe.director_agent._open_model_response",
            return_value=io.BytesIO(payload),
        ):
            result = director_agent.director_ask(
                MATCH, "What is the score?"
            )

    assert result["generation_mode"] == "deterministic"
    assert "SYNTHETIC-SENSITIVE-MARKER" not in caplog.text
