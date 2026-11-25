import asyncio
from unittest.mock import patch

import pytest

from vybe.security import MatchRequestGuard


async def application(scope, receive, send):
    await receive()
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [],
    })
    await send({"type": "http.response.body", "body": b"ok"})


async def request(guard, peer, path="/v1/matches/demo"):
    messages = []

    async def receive():
        return {
            "type": "http.request",
            "body": b"",
            "more_body": False,
        }

    async def send(message):
        assert not guard._lock.locked()
        messages.append(message)

    await guard(
        {
            "type": "http",
            "path": path,
            "client": (peer, 12345),
            "headers": [],
        },
        receive,
        send,
    )
    return messages[0]["status"]


def test_default_capacity():
    guard = MatchRequestGuard(application)
    assert guard.max_peers == 1024


@pytest.mark.parametrize("capacity", [0, -1])
def test_invalid_capacity(capacity):
    with pytest.raises(ValueError):
        MatchRequestGuard(application, max_peers=capacity)


def test_peer_capacity():
    async def scenario():
        guard = MatchRequestGuard(application, max_peers=2)
        assert await request(guard, "a") == 200
        assert await request(guard, "b") == 200
        assert await request(guard, "c") == 429
        assert await request(guard, "a") == 200
        assert len(guard._hits) == 2
        assert "c" not in guard._hits

    asyncio.run(scenario())


def test_expired_peer_recovery():
    async def scenario():
        guard = MatchRequestGuard(application, max_peers=1)
        with patch("vybe.security.time.monotonic", return_value=100):
            assert await request(guard, "a") == 200
            assert await request(guard, "b") == 429

        with patch("vybe.security.time.monotonic", return_value=160):
            assert await request(guard, "b") == 200

        assert set(guard._hits) == {"b"}

    asyncio.run(scenario())


def test_model_capacity_independent():
    async def scenario():
        guard = MatchRequestGuard(application, max_peers=2)
        path = "/v1/matches/director/ask"

        with patch("vybe.security.time.monotonic", return_value=100):
            assert await request(guard, "a", path) == 200
            assert await request(guard, "b", path) == 200

        with patch("vybe.security.time.monotonic", return_value=150):
            assert await request(guard, "a") == 200
            assert await request(guard, "b") == 200

        with patch("vybe.security.time.monotonic", return_value=160):
            assert await request(guard, "a", path) == 200

        assert len(guard._hits) <= 2
        assert len(guard._model_hits) <= 2

    asyncio.run(scenario())


def test_model_limit_preserved():
    async def scenario():
        guard = MatchRequestGuard(
            application,
            max_peers=2,
            requests_per_minute=5,
            model_requests_per_minute=1,
        )
        path = "/v1/matches/director/ask"
        assert await request(guard, "a", path) == 200
        assert await request(guard, "a", path) == 429
        assert await request(guard, "a") == 200

    asyncio.run(scenario())


def test_general_limit_preserved():
    async def scenario():
        guard = MatchRequestGuard(
            application, requests_per_minute=1
        )
        assert await request(guard, "a") == 200
        assert await request(guard, "a") == 429

    asyncio.run(scenario())


def test_concurrent_peer_capacity():
    async def scenario():
        guard = MatchRequestGuard(application, max_peers=4)
        statuses = await asyncio.gather(*(
            request(guard, str(i)) for i in range(20)
        ))
        assert statuses.count(200) == 4
        assert statuses.count(429) == 16
        assert len(guard._hits) == 4

    asyncio.run(scenario())

def test_full_model_bucket_rejects_without_growing():
    async def scenario():
        guard = MatchRequestGuard(application, max_peers=2)
        path = "/v1/matches/director/ask"

        # Exercise the model capacity branch independently
        # of the general bucket using controlled state.
        with patch("vybe.security.time.monotonic", return_value=100):
            assert await request(guard, "a", path) == 200
            assert await request(guard, "b", path) == 200
            guard._hits.clear()

            assert await request(guard, "c", path) == 429
            assert set(guard._model_hits) == {"a", "b"}
            assert "c" not in guard._hits

        with patch("vybe.security.time.monotonic", return_value=160):
            assert await request(guard, "c", path) == 200

        assert set(guard._model_hits) == {"c"}
        assert len(guard._hits) <= 2

    asyncio.run(scenario())


def test_general_requests_do_not_allocate_model_peers():
    async def scenario():
        guard = MatchRequestGuard(application, max_peers=2)

        assert await request(guard, "a") == 200
        assert await request(guard, "b") == 200
        assert len(guard._hits) == 2
        assert len(guard._model_hits) == 0

    asyncio.run(scenario())
