from backend_api.utils.stream_router import build_stream_router
import os
router = build_stream_router(
    name="liquidity",
    env_key="LIQUIDITY_STREAM_KEY",
    fallback_stream=os.getenv("STREAM_NAMESPACE", "atom") + ":liquidity",
)