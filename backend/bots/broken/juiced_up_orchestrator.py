# orchestrator.py
import asyncio
import aiohttp
import numpy as np
import pandas as pd
from scipy.sparse.csgraph import dijkstra
import time
import hashlib
import json
import matplotlib.pyplot as plt
from web3 import Web3
from flashbots import flashbot
from eth_account.account import Account
from web3.exceptions import TransactionNotFound
import telegram
import failsafe_omega
import flashbots_integration
import strategy_router
import slippage_engine
import chainlink_feeds
import websockets
import threading
import dash
from dash import dcc, html
import plotly.graph_objs as go
from concurrent.futures import ThreadPoolExecutor

# Constants
QUANTUM_DEPTH = 7
CHAINS = ['ethereum', 'arbitrum', 'optimism', 'polygon', 'bsc', 'avalanche', 
          'solana', 'cosmos', 'polkadot', 'near', 'fantom', 'base']
MIN_PROFIT_BPS = 23  # 0.23% threshold
KILL_SWITCH = failsafe_omega.OmegaProtocol()
WEBSOCKET_MAP = {
    'ethereum': "wss://dex.ethereum.com/ws",
    'arbitrum': "wss://dex.arbitrum.com/ws",
    # ... other chains
}

class DEXXenithScanner:
    """🌌 ULTIMATE DEX ARB SCANNER WITH MEV RESISTANCE & RISK MANAGEMENT"""
    
    def __init__(self):
        self.dex_registry = self._load_dex_registry()
        self.token_universe = self._build_token_universe()
        self.price_tensor = np.zeros((len(CHAINS), 500, 500, QUANTUM_DEPTH))
        self.opportunities = []
        self.web3 = Web3(Web3.WebsocketProvider(chainlink_feeds.get_node_url('fallback')))
        self.session = aiohttp.ClientSession()
        self.fb_provider = flashbots_integration.FlashbotsArmor()
        self.telegram = telegram.QuantumNotifier()
        self.slippage_guard = slippage_engine.SlippageSentinel()
        self.execution_strategies = strategy_router.StrategyRouter()
        self.ws_connections = {}
        self.execution_agents = [
            flashbots_integration.FlashbotsExecutor(),
            flashbots_integration.DirectTxExecutor()
        ]
        self.dash_server = threading.Thread(target=self._run_dashboard, daemon=True)
        self.dash_server.start()
        
        # Initialize Flashbots
        self.signer = Account.from_key(open('mev_key.txt').read().strip())
        flashbot(self.web3, self.signer, "https://relay.flashbots.net")
        
        # Start WebSocket streams
        asyncio.create_task(self._init_websocket_streams())
        
        logger.info(f"🌀 DEX ZENITH 3.0 INITIALIZED: WS streams | Trade sim | Dashboard | Agent fallback")

    async def _init_websocket_streams(self):
        """Connect to DEX WebSocket streams for real-time data"""
        for chain, endpoint in WEBSOCKET_MAP.items():
            try:
                self.ws_connections[chain] = await websockets.connect(endpoint)
                asyncio.create_task(self._listen_ws_stream(chain))
            except Exception as e:
                logger.error(f"WS connection failed for {chain}: {str(e)}")

    async def _listen_ws_stream(self, chain: str):
        """Process messages from WebSocket stream"""
        while True:
            try:
                msg = await self.ws_connections[chain].recv()
                data = json.loads(msg)
                self._process_ws_update(chain, data)
            except websockets.ConnectionClosed:
                logger.warning(f"WS connection closed for {chain}, reconnecting...")
                await self._reconnect_ws(chain)

    async def _reconnect_ws(self, chain: str):
        """Reconnect to WebSocket stream"""
        retries = 0
        while retries < 5:
            try:
                self.ws_connections[chain] = await websockets.connect(WEBSOCKET_MAP[chain])
                return
            except Exception:
                retries += 1
                await asyncio.sleep(2 ** retries)

    def _process_ws_update(self, chain: str, data: dict):
        """Update price tensor from WS message"""
        chain_idx = CHAINS.index(chain)
        token_a = self.token_universe[data['token0']]['index']
        token_b = self.token_universe[data['token1']]['index']
        price = float(data['price'])
        
        # Update price tensor
        self.price_tensor[chain_idx, token_a, token_b] = price
        self.price_tensor[chain_idx, token_b, token_a] = 1 / price

    # === TRADE SIMULATION ENGINE === #
    def simulate_trade(self, path: list, amount_in: float, chain: str) -> dict:
        """Simulate trade execution with slippage and gas"""
        gas_price = self.web3.eth.gas_price
        simulation = {
            'input': amount_in,
            'output': amount_in,
            'gas_cost': 0,
            'slippage_loss': 0,
            'net_profit': 0
        }
        
        # Simulate each swap in path
        for i in range(len(path)-1):
            token_in = path[i]
            token_out = path[i+1]
            
            # Get current pool state
            pool_state = self._get_pool_state(token_in, token_out, chain)
            
            # Apply slippage model
            effective_price = slippage_engine.calculate_effective_price(
                amount_in=simulation['output'],
                pool_state=pool_state
            )
            
            # Update simulation
            simulation['slippage_loss'] += simulation['output'] * pool_state['slippage_rate']
            simulation['output'] *= effective_price
            
            # Add gas cost for swap
            simulation['gas_cost'] += gas_price * pool_state['swap_gas']
        
        # Calculate net profit
        simulation['net_profit'] = simulation['output'] - simulation['input'] - simulation['gas_cost']
        return simulation

    # === REDUNDANT EXECUTION FALLBACK === #
    async def _execute_with_fallback(self, tx_bundle: dict, opp: dict):
        """Try multiple execution agents until success"""
        for agent in self.execution_agents:
            try:
                logger.info(f"Trying execution with {agent.name}...")
                result = await agent.execute(opp, tx_bundle)
                return await self._monitor_bundle(result['bundle_hash'])
            except Exception as e:
                logger.warning(f"{agent.name} failed: {str(e)}")
                continue
        raise Exception("All execution agents failed")

    # === DASHBOARD SERVER === #
    def _run_dashboard(self):
        """Run Plotly Dash dashboard in separate thread"""
        app = dash.Dash(__name__)
        
        app.layout = html.Div([
            dcc.Graph(id='arb-map'),
            dcc.Interval(id='refresh', interval=1000),
            html.Div(id='logs-output', style={'whiteSpace': 'pre-line'}),
            html.Div(id='tx-monitor')
        ])
        
        @app.callback(
            [Output('arb-map', 'figure'),
             Output('logs-output', 'children'),
             Output('tx-monitor', 'children')],
            [Input('refresh', 'n_intervals')]
        )
        def update_dashboard(_):
            # Arb opportunity map
            arb_map = go.Figure(go.Scattergeo(
                lon = [chain_data['lon'] for chain in CHAINS],
                lat = [chain_data['lat'] for chain in CHAINS],
                text = [f"{chain}: {len(self.opportunities)} opps" for chain in CHAINS],
                marker = dict(size=[len(opps)*5 for opps in self.opportunities])
            ))
            
            # Logs output
            logs = "\n".join(get_recent_logs(10))
            
            # TX monitor
            txs = [html.Div(f"{tx['hash']}: {tx['status']}") for tx in self.recent_txs]
            
            return arb_map, logs, txs
        
        app.run_server(port=8050, debug=False)

    # ... rest of class remains with modified execution ... 
    
    async def execute_top_opportunity(self):
        """Execute most profitable arb with full protection stack"""
        if not self.opportunities:
            return None
            
        # ... kill switch check ...
        
        # SIMULATE TRADE BEFORE EXECUTION
        sim_result = self.simulate_trade(
            path=opp['path'],
            amount_in=opp['amount_in'],
            chain=opp['chain']
        )
        
        if sim_result['net_profit'] < MIN_PROFIT_BPS/10000:
            logger.warning("Simulation shows unprofitable trade, skipping")
            return None
        
        # Build MEV-protected transaction
        tx_bundle = self._build_mev_protected_tx(opp)
        
        try:
            # EXECUTE WITH FALLBACK
            receipt = await self._execute_with_fallback(tx_bundle, opp)
            self.telegram.send_execution_report(opp, receipt)
            return receipt
            
        except Exception as e:
            logger.error(f"All executions failed: {str(e)}")
            self.telegram.send_alert(f"🔥 CRITICAL EXECUTION FAILURE: {str(e)}")
            KILL_SWITCH.activate()
            return None

# ... rest of file ...