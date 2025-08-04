from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tokens", tags=["tokens"])

# Base Sepolia token addresses
BASE_SEPOLIA_TOKENS = {
    "WETH": "0x4200000000000000000000000000000000000006",
    "USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    "DAI": "0x174956bDf96C89F96B5d3d42F3C6d7E8E8F8F8F8",
    "GHO": "0x5d00fab5f2F97C4D682C1053cDCAA59c2c37900D"
}

@router.get("/")
async def get_supported_tokens():
    """Get list of supported tokens"""
    return {
        "tokens": BASE_SEPOLIA_TOKENS,
        "network": "Base Sepolia",
        "chain_id": 84532
    }

@router.get("/{token_symbol}")
async def get_token_info(token_symbol: str):
    """Get information about a specific token"""
    token_symbol = token_symbol.upper()
    
    if token_symbol not in BASE_SEPOLIA_TOKENS:
        raise HTTPException(status_code=404, detail=f"Token {token_symbol} not supported")
    
    return {
        "symbol": token_symbol,
        "address": BASE_SEPOLIA_TOKENS[token_symbol],
        "network": "Base Sepolia",
        "chain_id": 84532
    }
