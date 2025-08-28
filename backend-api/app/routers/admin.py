from fastapi import APIRouter, Depends
from app.auth.clerk_jwt import verify_jwt

router = APIRouter(prefix="/v1/admin", tags=["admin"], dependencies=[Depends(verify_jwt)])

@router.get("/status")
async def admin_status():
    return {"ok": True, "role": "admin"} 