#!/usr/bin/env python3
"""Rate limiter CLI.

Token bucket and sliding window rate limiting.
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass


@dataclass
class TokenBucket:
    """Token bucket rate limiter."""

    capacity: int
    refill_rate: float  # tokens per second
    tokens: float
    last_refill: float

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()

    def refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens. Returns True if successful."""
        self.refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def wait_time(self, tokens: int = 1) -> float:
        """Calculate wait time until tokens available."""
        self.refill()
        if self.tokens >= tokens:
            return 0.0
        needed = tokens - self.tokens
        return needed / self.refill_rate

    def to_dict(self) -> dict:
        return {
            "capacity": self.capacity,
            "refill_rate": self.refill_rate,
            "tokens": self.tokens,
            "last_refill": self.last_refill,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TokenBucket":
        bucket = cls(data["capacity"], data["refill_rate"])
        bucket.tokens = data["tokens"]
        bucket.last_refill = data["last_refill"]
        return bucket


@dataclass
class SlidingWindow:
    """Sliding window rate limiter."""

    window_size: float  # seconds
    max_requests: int
    requests: list[float]  # timestamps

    def __init__(self, window_size: float, max_requests: int):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = []

    def cleanup(self) -> None:
        """Remove expired timestamps."""
        cutoff = time.time() - self.window_size
        self.requests = [t for t in self.requests if t > cutoff]

    def try_acquire(self) -> bool:
        """Try to make a request. Returns True if allowed."""
        self.cleanup()
        if len(self.requests) < self.max_requests:
            self.requests.append(time.time())
            return True
        return False

    def remaining(self) -> int:
        """Get remaining requests in current window."""
        self.cleanup()
        return max(0, self.max_requests - len(self.requests))

    def reset_time(self) -> float:
        """Get time until next slot available."""
        self.cleanup()
        if len(self.requests) < self.max_requests:
            return 0.0
        oldest = min(self.requests)
        return max(0.0, oldest + self.window_size - time.time())

    def to_dict(self) -> dict:
        return {
            "window_size": self.window_size,
            "max_requests": self.max_requests,
            "requests": self.requests,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SlidingWindow":
        window = cls(data["window_size"], data["max_requests"])
        window.requests = data.get("requests", [])
        return window


def create_rate_limiter(
    limiter_type: str,
    capacity: int,
    rate: float,
) -> TokenBucket | SlidingWindow:
    """Create a rate limiter."""
    if limiter_type == "token":
        return TokenBucket(capacity, rate)
    elif limiter_type == "window":
        return SlidingWindow(rate, capacity)
    raise ValueError(f"Unknown limiter type: {limiter_type}")


def check_rate_limit(limiter: TokenBucket | SlidingWindow) -> dict:
    """Check rate limit status without acquiring."""
    if isinstance(limiter, TokenBucket):
        limiter.refill()
        return {
            "type": "token_bucket",
            "allowed": limiter.tokens >= 1,
            "tokens": limiter.tokens,
            "capacity": limiter.capacity,
            "wait_time": limiter.wait_time(),
        }
    else:
        limiter.cleanup()
        return {
            "type": "sliding_window",
            "allowed": limiter.remaining() > 0,
            "remaining": limiter.remaining(),
            "max_requests": limiter.max_requests,
            "reset_time": limiter.reset_time(),
        }


def acquire_rate_limit(limiter: TokenBucket | SlidingWindow) -> dict:
    """Try to acquire rate limit."""
    allowed = limiter.try_acquire()
    status = check_rate_limit(limiter)
    status["acquired"] = allowed
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description="Rate limiting tool")
    parser.add_argument(
        "--type", choices=["token", "window"], default="token", help="Rate limiter type"
    )
    parser.add_argument("--capacity", type=int, default=10, help="Bucket capacity or max requests")
    parser.add_argument(
        "--rate", type=float, default=1.0, help="Refill rate (tokens/sec) or window size (seconds)"
    )
    parser.add_argument("-f", "--file", default="ratelimit.json", help="State file")
    parser.add_argument("--check", action="store_true", help="Check status without acquiring")
    parser.add_argument("--acquire", action="store_true", help="Try to acquire")
    parser.add_argument("--reset", action="store_true", help="Reset rate limiter")
    parser.add_argument("--wait", action="store_true", help="Wait until available (with --acquire)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Load or create limiter
    try:
        with open(args.file) as f:
            data = json.load(f)
            if data.get("type") == "token_bucket":
                limiter = TokenBucket.from_dict(data)
            else:
                limiter = SlidingWindow.from_dict(data)
    except FileNotFoundError:
        limiter = create_rate_limiter(args.type, args.capacity, args.rate)

    def save():
        with open(args.file, "w") as f:
            d = limiter.to_dict()
            d["type"] = "token_bucket" if isinstance(limiter, TokenBucket) else "sliding_window"
            json.dump(d, f, indent=2)

    # Commands
    if args.reset:
        limiter = create_rate_limiter(args.type, args.capacity, args.rate)
        save()
        print("Rate limiter reset")
        return 0

    if args.acquire:
        if args.wait:
            while not limiter.try_acquire():
                status = check_rate_limit(limiter)
                wait = status.get("wait_time") or status.get("reset_time") or 0.1
                time.sleep(wait)
            save()
            if args.json:
                print(json.dumps({"acquired": True}))
            else:
                print("Acquired")
            return 0
        else:
            result = acquire_rate_limit(limiter)
            save()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result["acquired"]:
                    print("Acquired")
                else:
                    wait = result.get("wait_time") or result.get("reset_time") or 0
                    print(f"Rate limited. Wait {wait:.2f}s")
                    return 1
            return 0 if result["acquired"] else 1

    # Default: check status
    status = check_rate_limit(limiter)
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(f"Type: {status['type']}")
        print(f"Allowed: {status['allowed']}")
        if "tokens" in status:
            print(f"Tokens: {status['tokens']:.2f}/{status['capacity']}")
        else:
            print(f"Remaining: {status['remaining']}/{status['max_requests']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
