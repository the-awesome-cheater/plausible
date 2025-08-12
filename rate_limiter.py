from __future__ import annotations

import threading
import time


class RateLimiter:
    """
    Simple token-bucket rate limiter.

    capacity: max tokens per window
    refill_window_s: seconds to fully refill the bucket from 0 to capacity

    acquire() blocks until a token is available, then consumes one token.
    Thread-safe for simple SDK usage.
    """

    def __init__(self, *, capacity: int, refill_window_s: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        if refill_window_s <= 0:
            raise ValueError("refill_window_s must be > 0")
        self.capacity = float(capacity)
        self.refill_window_s = float(refill_window_s)

        self._tokens = float(capacity)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        if elapsed <= 0:
            return
        rate_per_sec = self.capacity / self.refill_window_s
        self._tokens = min(self.capacity, self._tokens + elapsed * rate_per_sec)
        self._last_refill = now

    def acquire(self) -> None:
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                # time until next token
                rate_per_sec = self.capacity / self.refill_window_s
                needed = 1.0 - self._tokens
                wait_s = max(needed / rate_per_sec, 0.01)
            time.sleep(min(wait_s, 1.0))
