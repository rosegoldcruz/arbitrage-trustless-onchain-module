"""
App-level lifecycle hooks to manage shared aiohttp session.
"""
from fastapi import APIRouter
from backend.core.http_client import close_session

router = APIRouter()

@router.on_event("shutdown")
async def shutdown_event():
    await close_session()

