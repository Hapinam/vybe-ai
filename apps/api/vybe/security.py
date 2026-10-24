"""ASGI guardrails for public synthetic-match endpoints.

Local per-process peer rate limiting is defense in depth, not a distributed quota.
Only the ASGI peer address is trusted; forwarded headers are ignored.
"""
import asyncio
import time
from collections import defaultdict, deque


class MatchRequestGuard:
    def __init__(self, app, max_bytes=262144, requests_per_minute=240, model_requests_per_minute=30):
        self.app = app
        self.max_bytes = max_bytes
        self.requests_per_minute = requests_per_minute
        self.model_requests_per_minute = model_requests_per_minute
        self._hits = defaultdict(deque)
        self._model_hits = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope.get("path", "").startswith("/v1/matches/"):
            return await self.app(scope, receive, send)

        async def reject(status, message, extra_headers=()):
            body = ('{"detail":"' + message + '"}').encode()
            headers = [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode()), *extra_headers]
            await send({"type": "http.response.start", "status": status, "headers": headers})
            await send({"type": "http.response.body", "body": body})

        peer = scope.get("client")
        ip = peer[0] if peer else "unknown"
        now = time.monotonic()
        path = scope.get("path", "")
        # Only these endpoints can invoke a paid model. Keep a separate,
        # shared per-peer bucket in addition to the overall API limit.
        model_route = path == "/v1/matches/director/ask" or path.startswith("/v1/matches/narrate/") or path == "/v1/matches/speech"
        async with self._lock:
            hits = self._hits[ip]
            while hits and hits[0] <= now - 60:
                hits.popleft()
            if len(hits) >= self.requests_per_minute:
                return await reject(429, "rate limit exceeded", [(b"retry-after", b"60")])
            if model_route:
                model_hits = self._model_hits[ip]
                while model_hits and model_hits[0] <= now - 60:
                    model_hits.popleft()
                if len(model_hits) >= self.model_requests_per_minute:
                    return await reject(429, "model request rate limit exceeded", [(b"retry-after", b"60")])
                model_hits.append(now)
            hits.append(now)
            # Remove inactive peers to avoid unbounded map growth.
            for buckets in (self._hits, self._model_hits):
                if len(buckets) > 1024:
                    for key in list(buckets):
                        if key != ip and (not buckets[key] or buckets[key][-1] <= now - 60):
                            del buckets[key]

        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        if content_length:
            try:
                if int(content_length) > self.max_bytes:
                    return await reject(413, "request body too large")
            except ValueError:
                return await reject(400, "invalid content length")

        received = 0
        async def limited_receive():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    raise _BodyTooLarge()
            return message

        # Buffer the bounded body before passing it to FastAPI so that
        # oversized chunked requests fail cleanly before response starts.
        chunks = []
        try:
            while True:
                message = await limited_receive()
                if message["type"] == "http.disconnect":
                    return
                chunks.append(message.get("body", b""))
                if not message.get("more_body", False):
                    break
        except _BodyTooLarge:
            return await reject(413, "request body too large")
        body = b"".join(chunks)
        delivered = False
        async def replay_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()
        return await self.app(scope, replay_receive, send)


class _BodyTooLarge(Exception):
    pass
