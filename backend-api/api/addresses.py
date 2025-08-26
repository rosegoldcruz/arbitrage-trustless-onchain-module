#!/usr/bin/env python3
"""
Addresses API Router
- Serves canonical deployment records to the frontend/backend.
"""

import json
import logging
import os
from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

logger = logging.getLogger("api.addresses")
router = APIRouter(prefix="/api/addresses", tags=["addresses"])

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

@router.get("/{chain_id}/mev-guard-flashloan-arb.json", response_class=JSONResponse)
async def get_addresses(chain_id: int):
    rel = os.path.join(BASE_DIR, "addresses", str(chain_id), "mev-guard-flashloan-arb.json")
    static_rel = os.path.join(BASE_DIR, "backend-api", "static", "addresses", str(chain_id), "mev-guard-flashloan-arb.json")

    path = rel if os.path.exists(rel) else static_rel if os.path.exists(static_rel) else None
    if not path:
        raise HTTPException(status_code=404, detail="deployment record not found")

    try:
        with open(path, "r") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception as e:
        logger.exception("Failed to read addresses JSON: %s", e)
        raise HTTPException(status_code=500, detail="failed to read addresses") 