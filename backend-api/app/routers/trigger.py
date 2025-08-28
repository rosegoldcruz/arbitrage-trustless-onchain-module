import os
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.auth.clerk_jwt import verify_jwt
from config.secure_config import SecureConfig
from backend_bots.atom_core import get_redis
from backend_bots.atom_core.rpc_pool import with_w3
from backend_bots.atom_core.gas import dynamic_gas_cap
from bots.profit_calculator import ProfitCalculator
from web3 import Web3

from app.metrics_store import atom_arbitrage_opportunities_detected_total, persist_delta

router = APIRouter(prefix="/api", tags=["trigger"], dependencies=[Depends(verify_jwt)])

_cfg = SecureConfig()

ALLOWED_ROUTER_ABI = [{
    "inputs": [{"internalType": "address", "name": "", "type": "address"}],
    "name": "allowedRouter",
    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
    "stateMutability": "view",
    "type": "function",
}]

async def _allowed_router(addr: str) -> bool:
    fl_addr = _cfg.env.get("ATOM_CONTRACT_ADDRESS", _cfg.env.get("FLASHLOAN_ARB_ADDR", ""))
    if not fl_addr:
        raise HTTPException(status_code=500, detail="contract address not configured")
    async def _job(w3):
        c = w3.eth.contract(address=Web3.to_checksum_address(fl_addr), abi=ALLOWED_ROUTER_ABI)
        return bool(c.functions.allowedRouter(Web3.to_checksum_address(addr)).call())
    return await with_w3(_job)

@router.post("/trigger")
async def trigger(opp: Dict[str, Any]):
    try:
        # Collect router addresses from payload or env mapping
        routers: List[str] = []
        if "routers" in opp and isinstance(opp["routers"], list):
            routers = opp["routers"]
        else:
            dex_keys = [opp.get("dex_a"), opp.get("dex_b"), opp.get("dex_c")]
            key_map = {
                "uniswap_v3": "UNISWAP_V3_ROUTER",
                "sushiswap": "SUSHISWAP_ROUTER",
                "quickswap": "QUICKSWAP_ROUTER",
                "balancer": "BALANCER_VAULT",
                "curve": "CURVE_ROUTER",
            }
            for dex in dex_keys:
                if not dex:
                    continue
                env_key = key_map.get(str(dex).lower())
                if env_key and env_key in _cfg.env:
                    routers.append(_cfg.env[env_key])

        # Router allowlist validation
        for r in routers:
            ok = await _allowed_router(r)
            if not ok:
                raise HTTPException(status_code=400, detail={"code": "router_forbidden", "router": r})

        # Profit validation
        gas_cap_wei = await dynamic_gas_cap()
        gas_gwei = int(gas_cap_wei // 1_000_000_000)
        pc = ProfitCalculator()
        prof = pc.validate_opportunity(opp, gas_gwei=gas_gwei)
        if not prof.get("profitable"):
            raise HTTPException(status_code=400, detail={"code": "profit_below_threshold", "meta": prof})

        # Optional basic slippage sanity (if payload includes min amounts)
        # Here we ensure any provided min_out fields are nonzero
        for key in ("amount_ab", "amount_bc", "amount_out"):
            if key in opp and int(opp.get(key) or 0) <= 0:
                raise HTTPException(status_code=400, detail={"code": "slippage_too_high", "field": key})

        # Queue execution for executor
        queue = _cfg.env.get("ATOM_OPPORTUNITY_QUEUE", "arbitrage_opportunities")
        await get_redis().lpush(queue, os.getenv("JSON_DUMPS", "").join([]) or __import__("json").dumps(opp))

        atom_arbitrage_opportunities_detected_total.inc()
        await persist_delta("opps", 1.0)

        return {"status": "accepted", "gas_gwei": gas_gwei, "profit": prof}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"code": "internal_error", "error": str(e)}) 