"""
Health check router
"""

from fastapi import APIRouter
from datetime import datetime
import psutil
import platform

router = APIRouter()
from backend.real_orchestrator import _async_db
from backend.config.config import FLASH_LOAN_CONTRACT
from datetime import timezone
from time import monotonic

start_time = monotonic()

async def db_health():
    try:
        if _async_db and _async_db.pool:
            async with _async_db.pool.acquire() as conn:
                await conn.fetchval("SELECT 1;")
            return {"ok": True}
        return {"ok": False, "error": "no_pool"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

class FlashloanProbe:
    @staticmethod
    def is_ready():
        return bool(FLASH_LOAN_CONTRACT)

class Uptime:
    @staticmethod
    def seconds_online():
        return int(monotonic() - start_time)


@router.get("/")
async def health_check():
    """Health check endpoint"""
    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "system": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
            },
            "services": {
                "api": "running",
                "arbitrage_engine": "active",
                "ai_agents": "monitoring",
            },
            "checks": {
                "db": await db_health(),
                "flashloan_ready": FlashloanProbe.is_ready(),
                "uptime_seconds": Uptime.seconds_online(),
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }
