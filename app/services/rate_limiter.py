from fastapi import HTTPException, Request
import time

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60

attempt_store = {}

def check_rate_limit(request: Request):
    client = request.client
    ip = client.host if client else "unknown"

    now = time.time()

    if ip not in attempt_store:
        attempt_store[ip] = []

    attempt_store[ip] = [
        t for t in attempt_store[ip]
        if now - t < WINDOW_SECONDS
    ]

    if len(attempt_store[ip]) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Try again later."
        )

    attempt_store[ip].append(now)