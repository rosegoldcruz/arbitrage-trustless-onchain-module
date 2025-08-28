from backend_api.utils.stream_router import build_stream_router
import os
router = build_stream_router(
    name="mev",
    env_key="MEV_STREAM_KEY",
    fallback_stream=os.getenv("STREAM_NAMESPACE", "atom") + ":mev",
)