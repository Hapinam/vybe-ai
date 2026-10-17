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
