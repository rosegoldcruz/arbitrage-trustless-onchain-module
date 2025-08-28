from fastapi import APIRouter, Depends
from app.auth.clerk_jwt import verify_jwt
from backend_bots.atom_core import get_redis

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"], dependencies=[Depends(verify_jwt)])

@router.get("/stats")
async def dashboard_stats():
    r = get_redis()
    keys = ["trade_history", "trade_failures", "revert_analysis"]
    stats = {}
    for k in keys:
        try:
            stats[k] = await r.llen(k)
        except Exception:
            stats[k] = 0
    return {"ok": True, "stats": stats}

@router.get("/signals")
async def dashboard_signals(limit: int = 25):
    r = get_redis()
    stream = "atom:signals"
    try:
        entries = await r.xrevrange(stream, "+", "-", count=limit)
        out = [fields for _id, fields in entries]
    except Exception:
        out = []
    return {"ok": True, "signals": out, "count": len(out)} 