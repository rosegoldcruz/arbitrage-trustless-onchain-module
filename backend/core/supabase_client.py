from typing import Any, Dict
import os
import httpx

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

class Supabase:
    def __init__(self) -> None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError("Supabase env not configured")
        self.base_url = SUPABASE_URL.rstrip("/")
        self.headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    async def insert_trade(self, record: Dict[str, Any]) -> None:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(f"{self.base_url}/rest/v1/trades", headers=self.headers, json=record)
            resp.raise_for_status()

