"""
🚀 0x.org API Integration Router for ATOM Backend
Provides swap quotes, gasless transactions, and DEX aggregation endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import httpx
import os
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration
THEATOM_API_KEY = os.getenv("THEATOM_API_KEY")
ZRX_API_URL = os.getenv("ZRX_API_URL", "https://api.0x.org")
ZRX_GASLESS_API_URL = os.getenv("ZRX_GASLESS_API_URL", "https://gasless.api.0x.org")

# Request/Response Models
class SwapQuoteRequest(BaseModel):
    sellToken: str = Field(..., description="Token to sell (address or symbol)")
    buyToken: str = Field(..., description="Token to buy (address or symbol)")
    sellAmount: Optional[str] = Field(None, description="Amount to sell in wei")
    buyAmount: Optional[str] = Field(None, description="Amount to buy in wei")
    slippagePercentage: Optional[float] = Field(0.01, description="Slippage tolerance (0.01 = 1%)")
    gasPrice: Optional[str] = Field(None, description="Gas price in wei")
    takerAddress: Optional[str] = Field(None, description="Address that will execute the trade")
    excludedSources: Optional[List[str]] = Field(None, description="DEX sources to exclude")
    includedSources: Optional[List[str]] = Field(None, description="DEX sources to include")
    skipValidation: Optional[bool] = Field(False, description="Skip validation checks")

class GaslessQuoteRequest(BaseModel):
    sellToken: str = Field(..., description="Token to sell (address or symbol)")
    buyToken: str = Field(..., description="Token to buy (address or symbol)")
    sellAmount: Optional[str] = Field(None, description="Amount to sell in wei")
    buyAmount: Optional[str] = Field(None, description="Amount to buy in wei")
    takerAddress: str = Field(..., description="Address that will execute the trade")
    slippagePercentage: Optional[float] = Field(0.01, description="Slippage tolerance")

class SwapQuoteResponse(BaseModel):
    sellToken: str
    buyToken: str
    sellAmount: str
    buyAmount: str
    price: str
    guaranteedPrice: str
    to: str
    data: str
    value: str
    gas: str
    gasPrice: str
    protocolFee: str
    allowanceTarget: str
    sources: List[Dict[str, str]]
    sellTokenToEthRate: str
    buyTokenToEthRate: str

class TokenInfo(BaseModel):
    address: str
    symbol: str
    name: str
    decimals: int
    logoURI: Optional[str] = None

class ArbitrageOpportunity(BaseModel):
    dex_a: str
    dex_b: str
    token_pair: str
    price_difference: float
    potential_profit: float
    gas_cost: float
    net_profit: float
    confidence_score: float

# Utility functions
def get_headers():
    """Get headers for 0x.org API requests"""
    if not THEATOM_API_KEY:
        raise HTTPException(status_code=500, detail="0x.org API key not configured")
    
    return {
        "Content-Type": "application/json",
        "0x-api-key": THEATOM_API_KEY,
        "User-Agent": "ATOM-Platform/1.0"
    }

async def make_0x_request(url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make a request to 0x.org API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers=get_headers(),
                timeout=30.0
            )
            
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"0x API Error: {error_data.get('reason', response.text)}"
                )
            
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request to 0x.org API timed out")
    except Exception as e:
        logger.error(f"Error making 0x.org API request: {e}")
        raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")

# API Endpoints
@router.get("/quote", response_model=SwapQuoteResponse)
async def get_swap_quote(
    sellToken: str = Query(..., description="Token to sell"),
    buyToken: str = Query(..., description="Token to buy"),
    sellAmount: Optional[str] = Query(None, description="Amount to sell in wei"),
    buyAmount: Optional[str] = Query(None, description="Amount to buy in wei"),
    slippagePercentage: Optional[float] = Query(0.01, description="Slippage tolerance"),
    gasPrice: Optional[str] = Query(None, description="Gas price in wei"),
    takerAddress: Optional[str] = Query(None, description="Taker address"),
    excludedSources: Optional[str] = Query(None, description="Comma-separated excluded sources"),
    includedSources: Optional[str] = Query(None, description="Comma-separated included sources"),
    skipValidation: Optional[bool] = Query(False, description="Skip validation")
):
    """Get a swap quote from 0x.org"""
    
    params = {
        "sellToken": sellToken,
        "buyToken": buyToken,
        "slippagePercentage": slippagePercentage
    }
    
    if sellAmount:
        params["sellAmount"] = sellAmount
    if buyAmount:
        params["buyAmount"] = buyAmount
    if gasPrice:
        params["gasPrice"] = gasPrice
    if takerAddress:
        params["takerAddress"] = takerAddress
    if excludedSources:
        params["excludedSources"] = excludedSources
    if includedSources:
        params["includedSources"] = includedSources
    if skipValidation:
        params["skipValidation"] = "true"
    
    url = f"{ZRX_API_URL}/swap/v1/quote"
    data = await make_0x_request(url, params)
    
    return SwapQuoteResponse(**data)

@router.get("/gasless/quote")
async def get_gasless_quote(
    sellToken: str = Query(..., description="Token to sell"),
    buyToken: str = Query(..., description="Token to buy"),
    takerAddress: str = Query(..., description="Taker address"),
    sellAmount: Optional[str] = Query(None, description="Amount to sell in wei"),
    buyAmount: Optional[str] = Query(None, description="Amount to buy in wei"),
    slippagePercentage: Optional[float] = Query(0.01, description="Slippage tolerance")
):
    """Get a gasless quote from 0x.org"""
    
    params = {
        "sellToken": sellToken,
        "buyToken": buyToken,
        "takerAddress": takerAddress,
        "slippagePercentage": slippagePercentage
    }
    
    if sellAmount:
        params["sellAmount"] = sellAmount
    if buyAmount:
        params["buyAmount"] = buyAmount
    
    url = f"{ZRX_GASLESS_API_URL}/gasless/quote"
    data = await make_0x_request(url, params)
    
    return data

@router.get("/tokens", response_model=List[TokenInfo])
async def get_supported_tokens(
    chainId: int = Query(1, description="Chain ID (1 for Ethereum mainnet)")
):
    """Get supported tokens for a specific chain"""
    
    url = f"{ZRX_API_URL}/swap/v1/tokens"
    params = {"chainId": chainId}
    
    data = await make_0x_request(url, params)
    
    tokens = []
    for token_data in data.get("records", []):
        tokens.append(TokenInfo(**token_data))
    
    return tokens

@router.get("/sources")
async def get_liquidity_sources(
    chainId: int = Query(1, description="Chain ID")
):
    """Get available liquidity sources"""
    
    url = f"{ZRX_API_URL}/swap/v1/sources"
    params = {"chainId": chainId}
    
    data = await make_0x_request(url, params)
    
    return {
        "sources": data.get("sources", []),
        "chainId": chainId
    }

@router.get("/price")
async def get_token_price(
    sellToken: str = Query(..., description="Token to sell"),
    buyToken: str = Query(..., description="Token to buy"),
    sellAmount: Optional[str] = Query(None, description="Amount to sell in wei"),
    buyAmount: Optional[str] = Query(None, description="Amount to buy in wei")
):
    """Get price for a token pair"""
    
    params = {
        "sellToken": sellToken,
        "buyToken": buyToken
    }
    
    if sellAmount:
        params["sellAmount"] = sellAmount
    if buyAmount:
        params["buyAmount"] = buyAmount
    
    url = f"{ZRX_API_URL}/swap/v1/price"
    data = await make_0x_request(url, params)
    
    return {
        "price": data.get("price"),
        "estimatedGas": data.get("estimatedGas"),
        "sellToken": sellToken,
        "buyToken": buyToken,
        "sellAmount": data.get("sellAmount"),
        "buyAmount": data.get("buyAmount")
    }

@router.get("/arbitrage/opportunities", response_model=List[ArbitrageOpportunity])
async def find_arbitrage_opportunities(
    token_pairs: str = Query("ETH/USDC,ETH/USDT,WBTC/ETH", description="Comma-separated token pairs"),
    min_profit_threshold: float = Query(0.01, description="Minimum profit threshold in ETH"),
    max_gas_price: int = Query(50, description="Maximum gas price in gwei")
):
    """Find arbitrage opportunities using 0x.org price data"""
    
    opportunities = []
    pairs = token_pairs.split(",")
    
    for pair in pairs:
        try:
            tokens = pair.strip().split("/")
            if len(tokens) != 2:
                continue
                
            sell_token, buy_token = tokens
            
            # Get prices from different sources (simplified example)
            # In reality, you'd compare prices across multiple DEXes
            price_data = await get_token_price(
                sellToken=sell_token,
                buyToken=buy_token,
                sellAmount="1000000000000000000"  # 1 ETH in wei
            )
            
            if price_data and price_data.get("price"):
                # Simulate arbitrage opportunity detection
                # This is a simplified example - real implementation would be more complex
                price = float(price_data["price"])
                estimated_gas = int(price_data.get("estimatedGas", "21000"))
                gas_cost = (estimated_gas * max_gas_price * 1e-9)  # Convert to ETH
                
                # Simulate price difference (in real implementation, compare across DEXes)
                price_difference = price * 0.005  # 0.5% difference simulation
                potential_profit = price_difference - gas_cost
                
                if potential_profit > min_profit_threshold:
                    opportunities.append(ArbitrageOpportunity(
                        dex_a="0x Protocol",
                        dex_b="Simulated DEX",
                        token_pair=pair.strip(),
                        price_difference=price_difference,
                        potential_profit=potential_profit,
                        gas_cost=gas_cost,
                        net_profit=potential_profit,
                        confidence_score=0.85
                    ))
                    
        except Exception as e:
            logger.error(f"Error processing pair {pair}: {e}")
            continue
    
    return opportunities

@router.get("/health")
async def health_check():
    """Health check for 0x.org API integration"""
    
    try:
        # Test API connectivity
        url = f"{ZRX_API_URL}/swap/v1/sources"
        await make_0x_request(url, {"chainId": 1})
        
        return {
            "status": "healthy",
            "api_key_configured": bool(THEATOM_API_KEY),
            "base_url": ZRX_API_URL,
            "gasless_url": ZRX_GASLESS_API_URL
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "api_key_configured": bool(THEATOM_API_KEY)
        }
