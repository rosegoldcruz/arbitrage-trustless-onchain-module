from fastapi import APIRouter
from backend_bots.atom_core import get_redis

router = APIRouter(prefix="/v1", tags=["health"])

@router.get("/healthz")
async def healthz():
    try:
        await get_redis().ping()
        return {"ok": True}
    except Exception:
        return {"ok": False} 