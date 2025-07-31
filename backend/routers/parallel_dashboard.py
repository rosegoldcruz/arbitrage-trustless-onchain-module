"""
🚀 PARALLEL DASHBOARD API
FastAPI router for live Balancer & 0x data feeds
BASE SEPOLIA TESTNET FOCUSED - NO MOCK DATA
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import asyncio
import json
import logging
from datetime import datetime
import traceback

# 🔐 PERMANENT IMPORT FIX - Use relative imports since we're inside backend/
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our production services
from integrations.balancer_client import balancer_client
from integrations.zrx_service import ZrxService, ZrxChain
from integrations.thegraph_service import thegraph_service
from core.parallel_orchestrator import orchestrator, ArbitrageOpportunity

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/parallel", tags=["Parallel Dashboard"])

# Initialize services for Base Sepolia
zrx_service = ZrxService()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# Base Sepolia token addresses for testing
BASE_SEPOLIA_TOKENS = {
    "WETH": "0x4200000000000000000000000000000000000006",
    "USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e", 
    "DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
    "GHO": "0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f"
}

@router.get("/health")
async def health_check():
    """Health check for parallel services"""
    try:
        # Test both services
        balancer_status = "healthy"
        zrx_status = "healthy"
        
        try:
            # Quick Balancer test
            async with balancer_client as client:
                await client.get_high_tvl_pools(chains=["BASE"], first=1)
        except Exception as e:
            balancer_status = f"error: {str(e)[:100]}"
        
        try:
            # Quick 0x test
            await zrx_service.getTokenPrices(
                tokens=list(BASE_SEPOLIA_TOKENS.values())[:1],
                chainId=ZrxChain.BASE_SEPOLIA
            )
        except Exception as e:
            zrx_status = f"error: {str(e)[:100]}"

        # Test The Graph service
        thegraph_status = "healthy"
        try:
            async with thegraph_service as client:
                await client.get_top_pools(first=1)
        except Exception as e:
            thegraph_status = f"error: {str(e)[:100]}"
        
        all_healthy = all("healthy" in status for status in [balancer_status, zrx_status, thegraph_status])

        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "balancer": balancer_status,
                "zrx": zrx_status,
                "thegraph": thegraph_status,
                "orchestrator": "running" if orchestrator.isRunning else "stopped"
            },
            "network": "Base Sepolia Testnet",
            "chain_id": 84532
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/balancer/pools")
async def get_balancer_pools(
    min_tvl: float = 1000,
    limit: int = 20
):
    """Get live Balancer pools data for Base Sepolia"""
    try:
        logger.info(f"Fetching Balancer pools with min_tvl={min_tvl}, limit={limit}")
        
        pools = await balancer_service.getPoolsByTVL(
            chains=[BalancerChain.BASE],  # Use BASE for now, will add BASE_SEPOLIA when available
            minTvl=min_tvl,
            first=limit
        )
        
        # Transform for frontend
        formatted_pools = []
        for pool in pools:
            formatted_pools.append({
                "id": pool.get("id"),
                "address": pool.get("address"),
                "name": pool.get("name"),
                "chain": pool.get("chain"),
                "type": pool.get("type"),
                "tvl": float(pool.get("dynamicData", {}).get("totalLiquidity", 0)),
                "apr": pool.get("dynamicData", {}).get("aprItems", [{}])[0].get("apr", 0),
                "tokens": [
                    {
                        "address": token.get("address"),
                        "symbol": token.get("symbol"),
                        "balance": token.get("balance", "0")
                    }
                    for token in pool.get("poolTokens", [])
                ],
                "timestamp": datetime.utcnow().isoformat()
            })
        
        logger.info(f"Successfully fetched {len(formatted_pools)} Balancer pools")
        return {
            "success": True,
            "data": formatted_pools,
            "count": len(formatted_pools),
            "network": "Base Sepolia",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch Balancer pools: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to fetch Balancer pools: {str(e)}")

@router.get("/zrx/prices")
async def get_zrx_prices(
    tokens: Optional[str] = None
):
    """Get live 0x price data for Base Sepolia tokens"""
    try:
        token_list = tokens.split(",") if tokens else list(BASE_SEPOLIA_TOKENS.values())
        logger.info(f"Fetching 0x prices for {len(token_list)} tokens")
        
        market_data = await zrx_service.getMarketData(
            tokens=token_list,
            chainId=ZrxChain.BASE_SEPOLIA
        )
        
        # Format for frontend
        formatted_prices = []
        for data in market_data:
            # Find token symbol
            symbol = "UNKNOWN"
            for sym, addr in BASE_SEPOLIA_TOKENS.items():
                if addr.lower() == data["token"].lower():
                    symbol = sym
                    break
            
            formatted_prices.append({
                "token": data["token"],
                "symbol": symbol,
                "priceUsd": data["priceUsd"],
                "volume24h": data.get("volume24h"),
                "priceChange24h": data.get("priceChange24h"),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        logger.info(f"Successfully fetched {len(formatted_prices)} 0x prices")
        return {
            "success": True,
            "data": formatted_prices,
            "count": len(formatted_prices),
            "network": "Base Sepolia",
            "chainId": 84532,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch 0x prices: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to fetch 0x prices: {str(e)}")

@router.get("/arbitrage/opportunities")
async def get_arbitrage_opportunities(
    min_spread_bps: int = 23,
    min_profit_usd: float = 10.0
):
    """Get live arbitrage opportunities between Balancer and 0x"""
    try:
        logger.info(f"Scanning for arbitrage opportunities with min_spread_bps={min_spread_bps}")
        
        # Get latest snapshot from orchestrator
        snapshot = orchestrator.getLatestSnapshot()
        
        if not snapshot:
            # If no snapshot, return empty but valid response
            return {
                "success": True,
                "data": [],
                "count": 0,
                "message": "No opportunities found - orchestrator may be starting up",
                "network": "Base Sepolia",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Filter opportunities by criteria
        filtered_opportunities = [
            opp for opp in snapshot.arbitrageOpportunities
            if opp.spread >= (min_spread_bps / 100) and opp.netProfitUsd >= min_profit_usd
        ]
        
        # Format for frontend
        formatted_opportunities = []
        for opp in filtered_opportunities:
            formatted_opportunities.append({
                "id": opp.id,
                "tokenA": opp.tokenA,
                "tokenB": opp.tokenB,
                "spread": opp.spread,
                "spreadBps": int(opp.spread * 100),
                "profitUsd": opp.profitUsd,
                "netProfitUsd": opp.netProfitUsd,
                "gasEstimate": opp.gasEstimate,
                "confidence": opp.confidence,
                "source": opp.source,
                "balancerPrice": opp.balancerPrice,
                "zrxPrice": opp.zrxPrice,
                "executionPath": opp.executionPath,
                "timestamp": opp.timestamp
            })
        
        logger.info(f"Found {len(formatted_opportunities)} arbitrage opportunities")
        return {
            "success": True,
            "data": formatted_opportunities,
            "count": len(formatted_opportunities),
            "network": "Base Sepolia",
            "systemHealth": snapshot.systemHealth,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get arbitrage opportunities: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get arbitrage opportunities: {str(e)}")

@router.post("/zrx/quote")
async def get_zrx_quote(
    sellToken: str,
    buyToken: str,
    sellAmount: str,
    slippagePercentage: float = 0.01
):
    """Get executable quote from 0x for Base Sepolia"""
    try:
        logger.info(f"Getting 0x quote: {sellToken} -> {buyToken}, amount: {sellAmount}")
        
        quote = await zrx_service.getQuote({
            "chainId": ZrxChain.BASE_SEPOLIA,
            "sellToken": sellToken,
            "buyToken": buyToken,
            "sellAmount": sellAmount,
            "slippagePercentage": slippagePercentage
        })
        
        return {
            "success": True,
            "data": {
                "price": quote.price,
                "guaranteedPrice": quote.guaranteedPrice,
                "buyAmount": quote.buyAmount,
                "sellAmount": quote.sellAmount,
                "estimatedGas": quote.estimatedGas,
                "gasPrice": quote.gasPrice,
                "estimatedPriceImpact": quote.estimatedPriceImpact,
                "sources": quote.sources,
                "to": quote.to,
                "data": quote.data,
                "value": quote.value
            },
            "network": "Base Sepolia",
            "chainId": 84532,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get 0x quote: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get 0x quote: {str(e)}")

@router.get("/thegraph/pools")
async def get_thegraph_pools(
    min_tvl: float = 1000,
    limit: int = 20
):
    """Get live pool data from The Graph Protocol"""
    try:
        logger.info(f"Fetching The Graph pools with min_tvl={min_tvl}, limit={limit}")

        async with thegraph_service as client:
            pools = await client.get_top_pools(first=limit)

            # Filter by TVL and format for frontend
            formatted_pools = []
            for pool in pools:
                tvl = float(pool.total_value_locked_usd)
                if tvl >= min_tvl:
                    formatted_pools.append({
                        "id": pool.id,
                        "token0": {
                            "address": pool.token0.id,
                            "symbol": pool.token0.symbol,
                            "name": pool.token0.name
                        },
                        "token1": {
                            "address": pool.token1.id,
                            "symbol": pool.token1.symbol,
                            "name": pool.token1.name
                        },
                        "tvl": tvl,
                        "volume24h": float(pool.volume_usd),
                        "txCount": int(pool.tx_count),
                        "liquidity": pool.liquidity,
                        "timestamp": datetime.utcnow().isoformat()
                    })

            logger.info(f"Successfully fetched {len(formatted_pools)} The Graph pools")
            return {
                "success": True,
                "data": formatted_pools,
                "count": len(formatted_pools),
                "source": "The Graph Protocol",
                "network": "Base Sepolia",
                "timestamp": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"Failed to fetch The Graph pools: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to fetch The Graph pools: {str(e)}")

@router.get("/thegraph/opportunities")
async def get_thegraph_opportunities(
    min_spread_bps: int = 23,
    min_tvl: float = 1000
):
    """Get arbitrage opportunities from The Graph Protocol"""
    try:
        logger.info(f"Fetching The Graph opportunities with min_spread_bps={min_spread_bps}")

        async with thegraph_service as client:
            opportunities = await client.find_arbitrage_opportunities(
                min_spread_bps=min_spread_bps,
                min_tvl=min_tvl
            )

            # Format for frontend
            formatted_opportunities = []
            for opp in opportunities:
                formatted_opportunities.append({
                    "id": opp.id,
                    "tokenPair": opp.token_pair,
                    "pool1": {
                        "id": opp.pool1_id,
                        "price": opp.pool1_price,
                        "tvl": opp.pool1_tvl
                    },
                    "pool2": {
                        "id": opp.pool2_id,
                        "price": opp.pool2_price,
                        "tvl": opp.pool2_tvl
                    },
                    "spreadBps": opp.spread_bps,
                    "estimatedProfitUsd": opp.estimated_profit_usd,
                    "source": "The Graph Protocol",
                    "timestamp": opp.timestamp
                })

            logger.info(f"Found {len(formatted_opportunities)} The Graph opportunities")
            return {
                "success": True,
                "data": formatted_opportunities,
                "count": len(formatted_opportunities),
                "source": "The Graph Protocol",
                "network": "Base Sepolia",
                "timestamp": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"Failed to get The Graph opportunities: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get The Graph opportunities: {str(e)}")

@router.websocket("/ws/live-feed")
async def websocket_live_feed(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial data
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "Connected to ATOM live feed",
            "network": "Base Sepolia",
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                # Send market snapshot every 10 seconds
                snapshot = orchestrator.getLatestSnapshot()
                if snapshot:
                    await websocket.send_text(json.dumps({
                        "type": "market_update",
                        "data": {
                            "balancerTvl": snapshot.balancerData.get("totalTvl", 0),
                            "opportunitiesCount": len(snapshot.arbitrageOpportunities),
                            "systemHealth": snapshot.systemHealth,
                            "timestamp": snapshot.timestamp
                        }
                    }))
                
                await asyncio.sleep(10)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }))
                await asyncio.sleep(5)
                
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
