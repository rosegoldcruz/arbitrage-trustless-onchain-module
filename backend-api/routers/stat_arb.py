from backend_api.utils.stream_router import build_stream_router
import os
router = build_stream_router(
    name="stat_arb",
    env_key="STAT_ARB_STREAM_KEY",
    fallback_stream=os.getenv("STREAM_NAMESPACE", "atom") + ":stat_arb",
)