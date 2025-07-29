"""
🚀 REAL 0x.org API Integration - Complete Working Implementation
Provides actual swap quotes, price comparisons, and arbitrage detection for Base network
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
import httpx
import os
import logging
import asyncio
import json
from decimal import Decimal
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)
router = APIRouter()

# Real Configuration for Base Network
THEATOM_API_KEY = os.getenv("THEATOM_API_KEY", "7324a2b4-3b05-4288-b353-68322f49a283")
# Use Base mainnet (8453) since it's supported by 0x API
BASE_CHAIN_ID = 8453

# Import our real 0x client
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.zeroex_client import ZeroXClient, ZeroXAPIError

# Initialize real 0x client for Base mainnet
zx_client = ZeroXClient(
    api_key=THEATOM_API_KEY,
    chain_id=BASE_CHAIN_ID,
    use_testnet=False  # Use mainnet since it's supported
)

# Pydantic Models for API responses
class RealSwapQuoteResponse(BaseModel):
    sell_token: str
    buy_token: str
    sell_amount: str
    buy_amount: str
    price: str
    guaranteed_price: str
    gas_estimate: str
    gas_price: str
    protocol_fee: str
    allowance_target: str
    to: str
    data: str
    value: str
    sources: List[Dict[str, Any]]

class TokenPriceResponse(BaseModel):
    price: float
    estimated_gas: int
    sell_amount: str
    buy_amount: str
    sources: List[Dict[str, Any]]

class ArbitrageOpportunityResponse(BaseModel):
    token_a: str
    token_b: str
    profit_wei: str
    profit_percentage: float
    is_profitable: bool
    estimated_gas: int
    gas_cost_wei: str
    gas_cost_eth: float
    net_profit_wei: str
    sources_a_to_b: List[Dict[str, Any]]
    sources_b_to_a: List[Dict[str, Any]]

class TriangularArbitrageResponse(BaseModel):
    path: List[str]
    amounts: List[str]
    profit_wei: str
    profit_percentage: float
    is_profitable: bool
    estimated_gas: int
    gas_cost_wei: str
    gas_cost_eth: float
    net_profit_wei: str
    steps: List[Dict[str, str]]

class TokenInfoResponse(BaseModel):
    address: str
    symbol: str
    name: str
    decimals: int
    chain_id: int

# Real API Endpoints using our ZeroXClient

@router.get("/health")
async def health_check():
    """Check 0x API health and validate API key"""
    try:
        health_data = await zx_client.health_check()
        return health_data
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "api_key_configured": bool(THEATOM_API_KEY),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/quote", response_model=RealSwapQuoteResponse)
async def get_real_swap_quote(
    sell_token: str = Query(..., description="Token to sell (symbol or address)"),
    buy_token: str = Query(..., description="Token to buy (symbol or address)"),
    sell_amount: Optional[str] = Query(None, description="Amount to sell in wei"),
    buy_amount: Optional[str] = Query(None, description="Amount to buy in wei"),
    slippage_percentage: float = Query(0.01, description="Slippage tolerance (0.01 = 1%)"),
    taker_address: Optional[str] = Query(None, description="Address that will execute the trade")
):
    """Get real swap quote from 0x API for Base network tokens"""
    try:
        if not sell_amount and not buy_amount:
            raise HTTPException(status_code=400, detail="Either sell_amount or buy_amount must be specified")

        quote = await zx_client.get_swap_quote(
            sell_token=sell_token,
            buy_token=buy_token,
            sell_amount=sell_amount,
            buy_amount=buy_amount,
            slippage_percentage=slippage_percentage,
            taker_address=taker_address
        )

        return RealSwapQuoteResponse(
            sell_token=quote.sell_token,
            buy_token=quote.buy_token,
            sell_amount=quote.sell_amount,
            buy_amount=quote.buy_amount,
            price=quote.price,
            guaranteed_price=quote.guaranteed_price,
            gas_estimate=quote.gas_estimate,
            gas_price=quote.gas_price,
            protocol_fee=quote.protocol_fee,
            allowance_target=quote.allowance_target,
            to=quote.to,
            data=quote.data,
            value=quote.value,
            sources=quote.sources
        )

    except ZeroXAPIError as e:
        logger.error(f"0x API error: {e.message}")
        raise HTTPException(status_code=e.status_code or 500, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_swap_quote: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/price", response_model=TokenPriceResponse)
async def get_real_token_price(
    sell_token: str = Query(..., description="Token to sell (symbol or address)"),
    buy_token: str = Query(..., description="Token to buy (symbol or address)"),
    sell_amount: str = Query("1000000000000000000", description="Amount to sell in wei (default: 1 token)")
):
    """Get real token price from 0x API"""
    try:
        price_data = await zx_client.get_token_price(
            sell_token=sell_token,
            buy_token=buy_token,
            sell_amount=sell_amount
        )

        return TokenPriceResponse(**price_data)

    except ZeroXAPIError as e:
        logger.error(f"0x API error: {e.message}")
        raise HTTPException(status_code=e.status_code or 500, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_token_price: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/arbitrage/compare", response_model=ArbitrageOpportunityResponse)
async def compare_prices_for_arbitrage(
    token_a: str = Query(..., description="First token (symbol or address)"),
    token_b: str = Query(..., description="Second token (symbol or address)"),
    amount: str = Query("1000000000000000000", description="Amount to trade in wei")
):
    """Compare prices between tokens for arbitrage opportunities"""
    try:
        arbitrage_data = await zx_client.compare_prices_for_arbitrage(
            token_a=token_a,
            token_b=token_b,
            amount=amount
        )

        return ArbitrageOpportunityResponse(**arbitrage_data)

    except ZeroXAPIError as e:
        logger.error(f"0x API error in arbitrage comparison: {e.message}")
        raise HTTPException(status_code=e.status_code or 500, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in compare_prices_for_arbitrage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/arbitrage/triangular", response_model=TriangularArbitrageResponse)
async def find_triangular_arbitrage(
    token_a: str = Query(..., description="First token (symbol or address)"),
    token_b: str = Query(..., description="Second token (symbol or address)"),
    token_c: str = Query(..., description="Third token (symbol or address)"),
    amount: str = Query("1000000000000000000", description="Amount to start with in wei")
):
    """Find triangular arbitrage opportunities A -> B -> C -> A"""
    try:
        triangular_data = await zx_client.find_triangular_arbitrage(
            token_a=token_a,
            token_b=token_b,
            token_c=token_c,
            amount=amount
        )

        return TriangularArbitrageResponse(**triangular_data)

    except ZeroXAPIError as e:
        logger.error(f"0x API error in triangular arbitrage: {e.message}")
        raise HTTPException(status_code=e.status_code or 500, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in find_triangular_arbitrage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/tokens", response_model=List[TokenInfoResponse])
async def get_supported_tokens():
    """Get list of supported tokens on Base network"""
    try:
        tokens = await zx_client.get_supported_tokens()

        return [
            TokenInfoResponse(
                address=token.address,
                symbol=token.symbol,
                name=token.name,
                decimals=token.decimals,
                chain_id=token.chain_id
            )
            for token in tokens
        ]

    except ZeroXAPIError as e:
        logger.error(f"0x API error getting tokens: {e.message}")
        raise HTTPException(status_code=e.status_code or 500, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in get_supported_tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/sources")
async def get_liquidity_sources():
    """Get available DEX liquidity sources on Base network"""
    try:
        sources = await zx_client.get_liquidity_sources()

        return {
            "sources": sources,
            "chain_id": BASE_CHAIN_ID,
            "network": "Base Sepolia" if USE_TESTNET else "Base Mainnet",
            "timestamp": datetime.utcnow().isoformat()
        }

    except ZeroXAPIError as e:
        logger.error(f"0x API error getting sources: {e.message}")
        raise HTTPException(status_code=e.status_code or 500, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in get_liquidity_sources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/batch-prices")
async def get_batch_prices(
    token_pairs: List[str] = Query(..., description="List of token pairs like ['WETH/USDC', 'DAI/USDC']"),
    amount: str = Query("1000000000000000000", description="Amount to price in wei")
):
    """Get prices for multiple token pairs efficiently"""
    try:
        # Parse token pairs
        parsed_pairs = []
        for pair in token_pairs:
            if "/" not in pair:
                raise ValueError(f"Invalid pair format: {pair}. Use format 'TOKEN1/TOKEN2'")
            token_a, token_b = pair.split("/", 1)
            parsed_pairs.append((token_a.strip(), token_b.strip()))

        batch_results = await zx_client.batch_price_check(parsed_pairs, amount)

        return {
            "results": batch_results,
            "total_pairs": len(parsed_pairs),
            "successful_pairs": len([r for r in batch_results.values() if r is not None]),
            "timestamp": datetime.utcnow().isoformat()
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_batch_prices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/validate-api-key")
async def validate_api_key():
    """Validate the configured 0x API key"""
    try:
        is_valid = await zx_client.validate_api_key()

        return {
            "api_key_valid": is_valid,
            "api_key_configured": bool(THEATOM_API_KEY),
            "chain_id": BASE_CHAIN_ID,
            "network": "Base Sepolia" if USE_TESTNET else "Base Mainnet",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error validating API key: {str(e)}")
        return {
            "api_key_valid": False,
            "api_key_configured": bool(THEATOM_API_KEY),
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }




