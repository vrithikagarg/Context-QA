"""Small in-process sliding-window rate limiter.

Good enough to stop trivial password guessing and cost abuse without adding a
dependency. State is per process: with several workers or Cloud Run instances
each one keeps its own counters, so the effective limit is higher. For a hard
guarantee put Cloud Armor / an API gateway in front, or back this with Redis.
"""
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int, max_keys: int = 10_000):
        self.limit = limit
        self.window = window_seconds
        self.max_keys = max_keys
        self._events: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def _prune(self, key: str, now: float) -> deque:
        q = self._events[key]
        while q and now - q[0] > self.window:
            q.popleft()
        return q

    def retry_after(self, key: str) -> int:
        """Seconds until `key` may try again (0 if not limited)."""
        now = time.monotonic()
        with self._lock:
            q = self._prune(key, now)
            if len(q) < self.limit:
                return 0
            return max(1, int(self.window - (now - q[0])) + 1)

    def record(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            if len(self._events) > self.max_keys:  # bound memory
                for k in [k for k in self._events if not self._prune(k, now)]:
                    del self._events[k]
            self._prune(key, now).append(now)

    def clear(self, key: str) -> None:
        with self._lock:
            self._events.pop(key, None)


def raise_if_limited(limiter: RateLimiter, *keys: str) -> None:
    wait = max(limiter.retry_after(k) for k in keys)
    if wait:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
            headers={"Retry-After": str(wait)},
        )


def client_ip(request: Request) -> str:
    """Best-effort client address.

    Cloud Run appends the real client IP as the LAST X-Forwarded-For entry
    (earlier entries are client-supplied and spoofable), so use that one.
    Outside a trusted proxy this header can be forged; the per-account key in
    the login limiter still applies in that case.
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


# Failed logins: per client address and per account.
login_ip_limiter = RateLimiter(limit=20, window_seconds=300)
login_user_limiter = RateLimiter(limit=5, window_seconds=300)
# Chat (each call costs OpenAI tokens): per authenticated user.
chat_limiter = RateLimiter(limit=20, window_seconds=60)
