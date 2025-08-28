from redis.asyncio import Redis, ConnectionPool
import os

REDIS_URL = os.environ["REDIS_URL"]
POOL = ConnectionPool.from_url(
    REDIS_URL,
    max_connections=int(os.getenv("REDIS_MAX_CONN", "50")),
    socket_connect_timeout=5,
    socket_timeout=5,
    health_check_interval=30,
    retry_on_timeout=True,
)

def get_redis() -> Redis:
    return Redis(connection_pool=POOL, decode_responses=True) 