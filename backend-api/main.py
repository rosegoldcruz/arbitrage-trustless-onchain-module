from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from api.metrics import router as metrics
import os
import redis
import time

app = FastAPI(title="ATOM Arbitrage API", version="2.0.0")

# Redis for rate limiting
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"))

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aeoninvestmentstechnologies.com",
        "https://dashboard.aeoninvestmentstechnologies.com",
        "https://api.aeoninvestmentstechnologies.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "aeoninvestmentstechnologies.com",
        "*.aeoninvestmentstechnologies.com",
        "localhost",
        "127.0.0.1"
    ]
)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"

    try:
        current_requests = redis_client.incr(key)
        if current_requests == 1:
            redis_client.expire(key, 60)  # 60 seconds window

        if current_requests > 100:  # 100 requests per minute
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    except redis.RedisError:
        # If Redis is down, allow the request but log the error
        pass

    response = await call_next(request)
    return response

app.include_router(metrics)
