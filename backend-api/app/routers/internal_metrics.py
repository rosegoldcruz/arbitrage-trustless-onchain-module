from fastapi import APIRouter, Depends
from app.auth.clerk_jwt import verify_jwt
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

router = APIRouter(prefix="/api", tags=["metrics"], dependencies=[Depends(verify_jwt)])

@router.get("/metrics")
async def protected_metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST) 