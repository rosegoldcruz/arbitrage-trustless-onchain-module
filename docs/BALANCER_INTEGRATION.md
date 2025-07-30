# 🏊 Balancer GraphQL Integration Guide

## Overview

The ATOM arbitrage system now includes comprehensive integration with Balancer's v3 GraphQL API, providing real-time access to:

- **Pool Data**: Live TVL, balances, weights, and fees
- **Smart Order Router**: Optimal swap paths and price impact
- **Arbitrage Opportunities**: Cross-pool spread detection
- **Pool Events**: Swap, add/remove liquidity tracking
- **High-Volume Monitoring**: MEV opportunity identification

## 🚀 Quick Start

### 1. Test the Integration

```bash
# Test all Balancer queries
python backend/test_balancer_integration.py

# Start the backend server
python backend/main.py

# Test API endpoints
curl http://localhost:8000/api/arbitrage/balancer/pools
```

### 2. Run ATOM Bot with Balancer

```bash
# ATOM bot now automatically scans Balancer opportunities
python backend/bots/working/ATOM.py
```

## 📊 Available Endpoints

### Get Balancer Pools
```bash
GET /api/arbitrage/balancer/pools
```
Returns high-TVL pools from Base network with real-time data.

### Find Arbitrage Opportunities
```bash
GET /api/arbitrage/balancer/opportunities?min_spread_bps=23&chains=BASE
```
Discovers cross-pool arbitrage opportunities using live data.

### Monitor High-Volume Pools
```bash
GET /api/arbitrage/balancer/high-volume-pools?chains=BASE
```
Identifies pools with high trading activity for MEV opportunities.

### Get Pool Details
```bash
GET /api/arbitrage/balancer/pool/{pool_id}?chain=BASE
```
Retrieves detailed information for a specific pool.

### Smart Order Router Quote
```bash
POST /api/arbitrage/balancer/swap-quote
{
  "token_in": "0x4200000000000000000000000000000000000006",
  "token_out": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "amount": "1000000000000000000",
  "chain": "BASE"
}
```

## 🔧 Integration Architecture

### BalancerClient Class

Located in `backend/integrations/balancer_client.py`:

```python
from backend.integrations.balancer_client import balancer_client

async with balancer_client as client:
    pools = await client.get_high_tvl_pools(chains=["BASE"])
    opportunities = await client.find_arbitrage_opportunities()
```

### Key Methods

1. **`get_high_tvl_pools()`** - Fetch pools by TVL threshold
2. **`find_arbitrage_opportunities()`** - Detect profitable spreads
3. **`get_smart_order_router_paths()`** - Get optimal swap routes
4. **`monitor_high_volume_pools()`** - Track high-activity pools
5. **`get_pool_events()`** - Analyze swap/liquidity events

### ATOM Bot Integration

The ATOM bot (`backend/bots/working/ATOM.py`) now includes:

```python
async def _scan_balancer_opportunities(self):
    """Scan real Balancer pools for arbitrage opportunities"""
    async with balancer_client as client:
        balancer_opps = await client.find_arbitrage_opportunities(
            chains=["BASE"],
            min_spread_bps=self.config.min_spread_bps
        )
```

## 📈 Data Structures

### BalancerPool
```python
@dataclass
class BalancerPool:
    id: str
    address: str
    name: str
    chain: str
    pool_type: str
    version: int
    tokens: List[Dict[str, Any]]
    total_liquidity: float
    swap_fee: float
    apr_items: List[Dict[str, Any]]
    balances: List[str]
    weights: List[float]
```

### SwapPath
```python
@dataclass
class SwapPath:
    swap_amount_raw: str
    return_amount_raw: str
    price_impact: float
    route: List[Dict[str, Any]]
```

## 🎯 Arbitrage Strategy

### Opportunity Detection

1. **Pool Scanning**: Query high-TVL pools on Base network
2. **Price Analysis**: Compare SOR prices with external feeds
3. **Spread Calculation**: Identify spreads > 23 bps
4. **Risk Assessment**: Factor in gas costs and slippage
5. **Execution**: Route through optimal DEX paths

### Example Opportunity

```json
{
  "pool_id": "0x...",
  "token_in": {"symbol": "WETH", "address": "0x..."},
  "token_out": {"symbol": "USDC", "address": "0x..."},
  "spread_bps": 45,
  "price_impact": 0.0045,
  "tvl": 1250000,
  "swap_fee": 0.003,
  "chain": "BASE"
}
```

## 🔍 Monitoring & Analytics

### Real-Time Metrics

- **Pool TVL Changes**: Track liquidity additions/removals
- **Swap Volume**: Monitor trading activity
- **Price Impact**: Analyze market depth
- **APR Tracking**: Yield farming opportunities

### Event Analysis

```python
events = await client.get_pool_events(
    pool_ids=["0x..."],
    event_types=["SWAP", "ADD", "REMOVE"],
    limit=1000
)
```

## ⚡ Performance Optimizations

### Async Operations
All queries use `aiohttp` for non-blocking I/O:

```python
async with balancer_client as client:
    # Multiple concurrent queries
    pools_task = client.get_high_tvl_pools()
    events_task = client.get_pool_events()
    
    pools, events = await asyncio.gather(pools_task, events_task)
```

### Error Handling
Robust fallback mechanisms:

```python
try:
    real_data = await client.get_balancer_pools()
except Exception as e:
    logger.error(f"Balancer API failed: {e}")
    # Fallback to cached/mock data
```

## 🛠️ Configuration

### Environment Variables
```bash
# Optional: Custom GraphQL endpoint
BALANCER_GRAPHQL_URL=https://api-v3.balancer.fi/graphql

# Chain configuration
DEFAULT_CHAIN=BASE
MIN_SPREAD_BPS=23
```

### Orchestrator Config
```json
{
  "dex_endpoints": {
    "balancer_graphql": "https://api-v3.balancer.fi/graphql"
  },
  "thresholds": {
    "min_spread_bps": 23,
    "min_tvl": 10000
  }
}
```

## 🚨 Error Handling

### Common Issues

1. **GraphQL Errors**: Check query syntax and field availability
2. **Network Timeouts**: Implement retry logic with exponential backoff
3. **Rate Limits**: Respect API limits (no key required for Balancer)
4. **Chain Mismatches**: Ensure correct chain parameter (BASE, MAINNET, etc.)

### Debugging

```python
# Enable debug logging
logging.getLogger("backend.integrations.balancer_client").setLevel(logging.DEBUG)

# Test individual queries
python backend/test_balancer_integration.py
```

## 🔮 Future Enhancements

1. **Multi-Chain Support**: Expand beyond Base to Ethereum, Arbitrum
2. **Advanced Routing**: Multi-hop arbitrage paths
3. **MEV Protection**: Flashloan integration
4. **Yield Optimization**: LP position management
5. **Real-Time Alerts**: WebSocket notifications

## 📚 Resources

- [Balancer v3 GraphQL API](https://api-v3.balancer.fi/graphql)
- [Balancer Documentation](https://docs.balancer.fi/)
- [Base Network Tokens](https://basescan.org/tokens)
- [ATOM Bot Architecture](./complete_breakdown.md)

---

**Status**: ✅ Production Ready  
**Last Updated**: 2025-07-29  
**Maintainer**: ATOM Development Team
