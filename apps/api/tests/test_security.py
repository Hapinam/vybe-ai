"""Guardrail regression tests isolated from application-wide rate counters."""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from vybe.security import MatchRequestGuard


def guarded_client(max_bytes=128, requests_per_minute=2):
    app = FastAPI()
    app.add_middleware(MatchRequestGuard, max_bytes=max_bytes, requests_per_minute=requests_per_minute)

    @app.post("/v1/matches/replay")
    async def replay():
        return {"ok": True}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return TestClient(app)


def test_reject_content_length_over_limit():
    with guarded_client() as client:
        response = client.post("/v1/matches/replay", content=b"x" * 129)
        assert response.status_code == 413


def test_accept_body_at_limit():
    with guarded_client() as client:
        assert client.post("/v1/matches/replay", content=b"x" * 128).status_code == 200


def test_rate_limit_and_health_exemption():
    with guarded_client() as client:
        assert client.post("/v1/matches/replay", content=b"{}").status_code == 200
        assert client.post("/v1/matches/replay", content=b"{}").status_code == 200
        response = client.post("/v1/matches/replay", content=b"{}")
        assert response.status_code == 429
        assert response.headers["retry-after"] == "60"
        assert client.get("/health").status_code == 200


def test_forwarded_for_does_not_bypass_limit():
    with guarded_client(requests_per_minute=1) as client:
        assert client.post("/v1/matches/replay", content=b"{}", headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 200
        assert client.post("/v1/matches/replay", content=b"{}", headers={"X-Forwarded-For": "2.2.2.2"}).status_code == 429


def test_streamed_body_over_limit_without_content_length():
    """Reject an oversized streamed body even when no length header is supplied."""
    import asyncio

    async def run():
        async def downstream(scope, receive, send):
            # Must never be reached for an oversized body.
            raise AssertionError("oversized request reached downstream application")

        guard = MatchRequestGuard(downstream, max_bytes=8, requests_per_minute=10)
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/v1/matches/replay",
            "headers": [(b"content-type", b"application/json")],
            "client": ("127.0.0.1", 1234),
        }
        messages = iter([
            {"type": "http.request", "body": b"12345", "more_body": True},
            {"type": "http.request", "body": b"6789", "more_body": False},
        ])
        sent = []

        async def receive():
            return next(messages)

        async def send(message):
            sent.append(message)

        await guard(scope, receive, send)
        assert sent[0]["type"] == "http.response.start"
        assert sent[0]["status"] == 413
        assert b"request body too large" in sent[1]["body"]

    asyncio.run(run())


def test_streamed_body_at_limit_without_content_length():
    """Allow a streamed body exactly at the configured limit."""
    import asyncio

    async def run():
        async def downstream(scope, receive, send):
            message = await receive()
            assert message["body"] == b"12345678"
            assert message["more_body"] is False
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"ok"})

        guard = MatchRequestGuard(downstream, max_bytes=8, requests_per_minute=10)
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/v1/matches/replay",
            "headers": [],
            "client": ("127.0.0.1", 1234),
        }
        messages = iter([
            {"type": "http.request", "body": b"123", "more_body": True},
            {"type": "http.request", "body": b"45678", "more_body": False},
        ])
        sent = []

        async def receive():
            return next(messages)

        async def send(message):
            sent.append(message)

        await guard(scope, receive, send)
        assert sent[0]["status"] == 200

    asyncio.run(run())
