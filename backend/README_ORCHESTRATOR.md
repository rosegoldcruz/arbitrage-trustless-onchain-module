# REAL ARBITRAGE ORCHESTRATOR

**NO FAKE QUANTUM BULLSHIT - JUST WORKING BOT COORDINATION**

This orchestrator actually manages your ATOM.py and ADOM.js bots with real DEX APIs, actual process management, and functional communication.

## What It Actually Does

### 1. OPPORTUNITY DETECTION
- **Real HTTP requests** to DEX APIs (Uniswap V3, Curve, Balancer, 1inch)
- **Actual price difference calculation** using real market data
- **Minimum 0.5% spread filtering** with configurable thresholds
- **No fake price feeds** - uses live subgraph and API data

### 2. STRATEGY ROUTING
- **Clear if/else logic** (no fake AI routing):
  - High MEV risk → ADOM.js (MEV protection)
  - Profit > $100 → ADOM.js (flash loan)
  - High gas cost → ATOM.py (optimization)
  - Default → ATOM.py (simple arbitrage)

### 3. BOT PROCESS MANAGEMENT
- **Real subprocess.Popen()** to start/stop bots
- **Actual PID checking** with psutil
- **Automatic restart** on crashes (max 5 attempts)
- **Process monitoring** every 10 seconds

### 4. COMMUNICATION
- **File-based JSON communication** (no fake IPC libraries)
- Commands: `comm/commands/{bot}_command.json`
- Results: `comm/results/{bot}_result.json`
- Heartbeats: `comm/heartbeats/{bot}_heartbeat.json`

### 5. FAILSAFE MECHANISMS
- **Real exception handling** with try/catch blocks
- **Circuit breaker** stops after 10 failures
- **Heartbeat timeout** detection (120 seconds)
- **Automatic bot restart** on crashes

### 6. PERFORMANCE TRACKING
- **SQLite database** with real metrics
- **CSV reports** with timestamps
- **Actual success rates** and profit tracking
- **No fake quantum analytics**

## File Structure

```
backend/
├── real_orchestrator.py          # Main orchestrator
├── orchestrator_config.json      # Configuration
├── start_orchestrator.py         # Startup script
├── run_orchestrator.sh          # Shell startup script
├── bot_communication_example.py  # Communication interface
├── comm/                         # Bot communication
│   ├── commands/                 # Commands to bots
│   ├── results/                  # Results from bots
│   └── heartbeats/              # Bot status updates
├── logs/                        # Log files
└── orchestrator_performance.db  # Performance database
```

## Quick Start

### 1. Install Dependencies
```bash
pip install requests psutil
cd bots && npm install
```

### 2. Configure
Edit `orchestrator_config.json`:
- Set correct bot paths
- Configure DEX endpoints
- Set risk thresholds

### 3. Run
```bash
# Option 1: Shell script
chmod +x run_orchestrator.sh
./run_orchestrator.sh

# Option 2: Python directly
python3 start_orchestrator.py
```

## Configuration

### Bot Paths
```json
{
  "bot_paths": {
    "atom": "backend/bots/ATOM.py",
    "adom": "backend/bots/ADOM.js"
  }
}
```

### DEX Endpoints (REAL APIs)
```json
{
  "dex_endpoints": {
    "uniswap_v3": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
    "curve": "https://api.curve.fi/api",
    "balancer": "https://api.balancer.fi",
    "1inch": "https://api.1inch.io/v5.0/8453"
  }
}
```

### Risk Management
```json
{
  "thresholds": {
    "min_spread_bps": 23,
    "min_profit_usd": 10.0,
    "flash_loan_threshold": 100.0
  },
  "risk_management": {
    "max_restarts": 5,
    "heartbeat_timeout": 120,
    "circuit_breaker": {
      "max_failures": 10
    }
  }
}
```

## Bot Integration

Your bots need to implement the communication interface:

### 1. Send Heartbeats
```python
# Every 30 seconds
heartbeat_data = {
    "bot_name": "ATOM",
    "status": "running",
    "timestamp": time.time(),
    "pid": os.getpid()
}
with open("comm/heartbeats/atom_heartbeat.json", "w") as f:
    json.dump(heartbeat_data, f)
```

### 2. Check for Commands
```python
# Check every 5 seconds
if os.path.exists("comm/commands/atom_command.json"):
    with open("comm/commands/atom_command.json", "r") as f:
        command = json.load(f)
    os.remove("comm/commands/atom_command.json")
    
    if command["command"] == "execute_arbitrage":
        # Execute the opportunity
        execute_arbitrage(command["opportunity"])
```

### 3. Send Results
```python
# After execution
result = {
    "bot_name": "ATOM",
    "success": True,
    "timestamp": time.time(),
    "data": {
        "profit": 25.50,
        "tx_hash": "0x123..."
    }
}
with open("comm/results/atom_result.json", "w") as f:
    json.dump(result, f)
```

## Monitoring

### Real-time Logs
```bash
tail -f orchestrator.log
```

### Performance Database
```sql
-- Check opportunities
SELECT * FROM opportunities ORDER BY detected_at DESC LIMIT 10;

-- Check bot performance
SELECT * FROM bot_performance ORDER BY timestamp DESC LIMIT 10;

-- Check executions
SELECT * FROM executions ORDER BY execution_time DESC LIMIT 10;
```

### CSV Reports
Performance reports are automatically generated in `performance_report_YYYYMMDD_HHMMSS.csv`

## Troubleshooting

### Bot Won't Start
1. Check bot file exists and is executable
2. Check Python/Node.js dependencies
3. Check environment variables
4. Check logs in `orchestrator.log`

### No Opportunities Found
1. Check DEX API endpoints are responding
2. Verify network connectivity
3. Check minimum spread threshold
4. Monitor logs for API errors

### Circuit Breaker Activated
1. Check bot error logs
2. Verify network conditions
3. Reset by restarting orchestrator
4. Adjust failure thresholds if needed

## What Makes This REAL

- ✅ **Actual subprocess management** (not fake process simulation)
- ✅ **Real HTTP requests** to live DEX APIs
- ✅ **File-based communication** (no fake IPC libraries)
- ✅ **SQLite database** for real metrics
- ✅ **Exception handling** with try/catch blocks
- ✅ **Process monitoring** with actual PID checking
- ✅ **Clear routing logic** (no fake AI decisions)
- ✅ **Working startup scripts** you can run immediately

No quantum depth, no price tensors, no fake WebSocket streams, no Redis dependencies, no consensus engines - just functional code that coordinates your bots and finds real arbitrage opportunities.
