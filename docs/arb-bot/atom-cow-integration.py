#!/usr/bin/env python3
"""
ATOM v2 - CoW Protocol Integration
Batch auction participation and solver capabilities
"""

import asyncio
import json
import time
import hashlib
import sys
import os
from typing import Dict, List, Optional, Tuple, Set

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../agents'))
from agent_mev_calculator import AgentMEVCalculator, ArbitrageOpportunity
from dataclasses import dataclass, field
from decimal import Decimal
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
import aiohttp

@dataclass
class CoWOrder:
    """CoW Protocol order structure"""
    sell_token: str
    buy_token: str
    sell_amount: int
    buy_amount: int
    valid_to: int
    app_data: str
    fee_amount: int
    kind: str  # 'sell' or 'buy'
    partially_fillable: bool
    receiver: str
    signature: str
    from_address: str
    quote_id: Optional[str] = None
    
    @property
    def uid(self) -> str:
        """Calculate order UID"""
        order_digest = Web3.keccak(
            Web3.solidityKeccak(
                ['address', 'address', 'uint256', 'uint256', 'uint32', 'bytes32', 'uint256', 'bytes32', 'address', 'address'],
                [
                    self.sell_token,
                    self.buy_token,
                    self.sell_amount,
                    self.buy_amount,
                    self.valid_to,
                    bytes.fromhex(self.app_data[2:]) if self.app_data.startswith('0x') else bytes.fromhex(self.app_data),
                    self.fee_amount,
                    Web3.keccak(text=self.kind),
                    self.from_address,
                    self.receiver
                ]
            )
        )
        return order_digest.hex()

@dataclass 
class CoWSettlement:
    """Settlement solution for CoW batch"""
    orders: List[CoWOrder]
    clearing_prices: Dict[str, int]
    trades: List[Dict]
    interactions: List[Dict]
    score: Decimal
    
@dataclass
class ArbitrageWithCoW:
    """Arbitrage opportunity using CoW orders"""
    cow_order: CoWOrder
    external_quote: 'RouteQuote'
    profit_wei: int
    execution_type: str  # 'cow_settlement' or 'direct_execution'
    settlement_data: Optional[Dict] = None

class ATOMCoWIntegration:
    """CoW Protocol integration for ATOM"""
    
    def __init__(self, config: Dict, w3: Web3, pathfinder: 'ATOMPathfinder'):
        self.config = config
        self.w3 = w3
        self.pathfinder = pathfinder
        
        # CoW API endpoints
        self.cow_api = {
            'mainnet': 'https://api.cow.fi/mainnet/api/v1',
            'gnosis': 'https://api.cow.fi/xdai/api/v1',
            'goerli': 'https://api.cow.fi/goerli/api/v1'
        }
        
        self.network = config.get('network', 'mainnet')
        self.base_url = self.cow_api[self.network]
        
        # Solver configuration
        self.is_solver = config.get('cow_solver_enabled', False)
        self.solver_account = Account.from_key(config['solver_private_key']) if self.is_solver else None
        
        # Order tracking
        self.monitored_orders: Dict[str, CoWOrder] = {}
        self.executed_orders: Set[str] = set()
        
        # Metrics
        self.metrics = {
            'orders_monitored': 0,
            'arbitrages_found': 0,
            'settlements_submitted': 0,
            'solver_rewards_earned': 0
        }
    
    async def start_monitoring(self):
        """Start monitoring CoW Protocol orders"""
        tasks = [
            self._monitor_open_orders(),
            self._monitor_auctions() if self.is_solver else None
        ]
        
        tasks = [t for t in tasks if t is not None]
        await asyncio.gather(*tasks)
    
    async def _monitor_open_orders(self):
        """Monitor open orders for arbitrage opportunities"""
        while True:
            try:
                # Fetch open orders
                orders = await self._fetch_open_orders()
                
                # Filter relevant orders
                relevant_orders = self._filter_relevant_orders(orders)
                
                # Check each order for arbitrage
                for order in relevant_orders:
                    opportunity = await self._check_arbitrage_opportunity(order)
                    
                    if opportunity:
                        await self._execute_cow_arbitrage(opportunity)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"CoW monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _fetch_open_orders(self) -> List[CoWOrder]:
        """Fetch open orders from CoW API"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/orders") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    orders = []
                    for order_data in data:
                        # Only process unsigned orders (market orders)
                        if order_data.get('signingScheme') == 'presign':
                            continue
                        
                        order = CoWOrder(
                            sell_token=order_data['sellToken'],
                            buy_token=order_data['buyToken'], 
                            sell_amount=int(order_data['sellAmount']),
                            buy_amount=int(order_data['buyAmount']),
                            valid_to=order_data['validTo'],
                            app_data=order_data['appData'],
                            fee_amount=int(order_data['feeAmount']),
                            kind=order_data['kind'],
                            partially_fillable=order_data['partiallyFillable'],
                            receiver=order_data['receiver'],
                            signature=order_data['signature'],
                            from_address=order_data['owner']
                        )
                        
                        orders.append(order)
                        self.metrics['orders_monitored'] += 1
                    
                    return orders
        
        return []
    
    def _filter_relevant_orders(self, orders: List[CoWOrder]) -> List[CoWOrder]:
        """Filter orders based on configured criteria"""
        filtered = []
        
        # Supported tokens
        supported_tokens = set(self.config.get('tokens', []))
        
        # Minimum order size (in USD equivalent)
        min_order_size = self.config.get('min_cow_order_size_usd', 1000)
        
        for order in orders:
            # Check if tokens are supported
            if order.sell_token not in supported_tokens or order.buy_token not in supported_tokens:
                continue
            
            # Check if order is not expired
            if order.valid_to <= int(time.time()):
                continue
            
            # Check if not already executed
            if order.uid in self.executed_orders:
                continue
            
            # Estimate order size in USD
            # In production, use price oracle
            estimated_size = self._estimate_order_size_usd(order)
            if estimated_size < min_order_size:
                continue
            
            filtered.append(order)
            self.monitored_orders[order.uid] = order
        
        return filtered
    
    async def _check_arbitrage_opportunity(self, order: CoWOrder) -> Optional[ArbitrageWithCoW]:
        """Check if CoW order presents arbitrage opportunity"""
        # Get external market quote for the same trade
        external_quote = await self.pathfinder.find_best_route(
            order.sell_token,
            order.buy_token,
            order.sell_amount - order.fee_amount  # Subtract CoW fee
        )
        
        if not external_quote:
            return None
        
        # Check if external markets offer better rate
        if order.kind == 'sell':
            # For sell orders, check if we can get more buy tokens externally
            external_output = external_quote.amount_out
            cow_output = order.buy_amount
            
            if external_output > cow_output:
                # We can fill the CoW order and sell excess on external market
                profit = external_output - cow_output
                
                # Need to check if profit covers gas
                gas_cost = external_quote.gas_estimate * self.w3.eth.gas_price
                
                if profit > gas_cost + self.config.get('min_profit_wei', Web3.toWei(0.01, 'ether')):
                    return ArbitrageWithCoW(
                        cow_order=order,
                        external_quote=external_quote,
                        profit_wei=profit - gas_cost,
                        execution_type='direct_execution'
                    )
        
        else:  # buy order
            # For buy orders, check if we can provide tokens cheaper
            external_input = await self._calculate_input_for_exact_output(
                order.sell_token,
                order.buy_token,
                order.buy_amount
            )
            
            if external_input and external_input < order.sell_amount:
                # We can provide the buy amount for less sell amount
                profit = order.sell_amount - external_input - order.fee_amount
                
                gas_cost = 200000 * self.w3.eth.gas_price  # Estimate
                
                if profit > gas_cost + self.config.get('min_profit_wei', Web3.toWei(0.01, 'ether')):
                    return ArbitrageWithCoW(
                        cow_order=order,
                        external_quote=external_quote,
                        profit_wei=profit - gas_cost,
                        execution_type='direct_execution'
                    )
        
        return None
    
    async def _execute_cow_arbitrage(self, opportunity: ArbitrageWithCoW):
        """Execute arbitrage with CoW order"""
        print(f"🐮 CoW Arbitrage opportunity found!")
        print(f"   Order: {opportunity.cow_order.uid[:16]}...")
        print(f"   Profit: {Web3.fromWei(opportunity.profit_wei, 'ether')} ETH")
        
        if opportunity.execution_type == 'direct_execution':
            # Direct execution through CoW settlement
            await self._execute_direct_settlement(opportunity)
        else:
            # Participate in batch auction as solver
            await self._submit_solver_solution(opportunity)
    
    async def _execute_direct_settlement(self, opportunity: ArbitrageWithCoW):
        """Execute direct settlement with CoW order"""
        # This requires being a registered solver or using CoW's API
        # For now, we'll prepare the settlement data
        
        settlement = {
            'orders': [opportunity.cow_order.uid],
            'prices': {
                opportunity.cow_order.sell_token: 1,
                opportunity.cow_order.buy_token: opportunity.external_quote.effective_rate
            },
            'trades': [{
                'order_uid': opportunity.cow_order.uid,
                'exec_sell_amount': opportunity.cow_order.sell_amount,
                'exec_buy_amount': opportunity.cow_order.buy_amount
            }],
            'interactions': [{
                'target': opportunity.external_quote.to_address,
                'call_data': opportunity.external_quote.call_data.hex()
            }]
        }
        
        print(f"   Settlement prepared: {json.dumps(settlement, indent=2)}")
        
        # In production, submit this to CoW Protocol
        # For now, log it
        self.metrics['arbitrages_found'] += 1
    
    async def _monitor_auctions(self):
        """Monitor batch auctions as a solver"""
        print("🐮 Starting CoW solver monitoring...")
        
        while True:
            try:
                # Get current auction
                auction = await self._fetch_current_auction()
                
                if auction:
                    # Solve the batch
                    solution = await self._solve_batch(auction)
                    
                    if solution and solution.score > 0:
                        # Submit solution
                        await self._submit_solution(auction['id'], solution)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Solver error: {e}")
                await asyncio.sleep(60)
    
    async def _fetch_current_auction(self) -> Optional[Dict]:
        """Fetch current batch auction"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/solver/auction") as response:
                if response.status == 200:
                    return await response.json()
        return None
    
    async def _solve_batch(self, auction: Dict) -> Optional[CoWSettlement]:
        """Solve batch auction"""
        orders = [self._parse_auction_order(o) for o in auction['orders']]
        
        # Group orders by token pairs
        pair_orders = defaultdict(list)
        for order in orders:
            pair = (order.sell_token, order.buy_token)
            pair_orders[pair].append(order)
        
        # Find best settlement
        trades = []
        interactions = []
        total_score = Decimal('0')
        
        for pair, pair_orders in pair_orders.items():
            # Get external liquidity
            external_quote = await self.pathfinder.find_best_route(
                pair[0],
                pair[1],
                sum(o.sell_amount for o in pair_orders)
            )
            
            if external_quote:
                # Check if we can improve on limit prices
                for order in pair_orders:
                    if self._can_fill_order(order, external_quote):
                        trades.append({
                            'order_uid': order.uid,
                            'exec_sell_amount': order.sell_amount,
                            'exec_buy_amount': order.buy_amount
                        })
                        
                        # Calculate score (surplus)
                        surplus = self._calculate_surplus(order, external_quote)
                        total_score += surplus
                
                if trades:
                    interactions.append({
                        'target': external_quote.to_address,
                        'call_data': external_quote.call_data.hex()
                    })
        
        if trades:
            return CoWSettlement(
                orders=orders,
                clearing_prices=self._calculate_clearing_prices(orders, trades),
                trades=trades,
                interactions=interactions,
                score=total_score
            )
        
        return None
    
    def _can_fill_order(self, order: CoWOrder, quote: 'RouteQuote') -> bool:
        """Check if order can be filled profitably"""
        if order.kind == 'sell':
            # For sell orders, we need to provide at least buy_amount
            return quote.amount_out >= order.buy_amount
        else:
            # For buy orders, we need to take at most sell_amount
            return quote.amount_in <= order.sell_amount
    
    def _calculate_surplus(self, order: CoWOrder, quote: 'RouteQuote') -> Decimal:
        """Calculate surplus generated by filling order"""
        if order.kind == 'sell':
            # Surplus is extra buy tokens
            surplus_tokens = quote.amount_out - order.buy_amount
            # Convert to sell token value for scoring
            return Decimal(surplus_tokens) / Decimal(quote.effective_rate)
        else:
            # Surplus is saved sell tokens
            return Decimal(order.sell_amount - quote.amount_in)
    
    def _calculate_clearing_prices(self, orders: List[CoWOrder], trades: List[Dict]) -> Dict[str, int]:
        """Calculate uniform clearing prices"""
        prices = {}
        
        # Simple implementation - use execution prices
        for i, trade in enumerate(trades):
            order = next(o for o in orders if o.uid == trade['order_uid'])
            
            if order.sell_token not in prices:
                prices[order.sell_token] = 10**18  # Reference price
            
            if order.buy_token not in prices:
                rate = Decimal(trade['exec_buy_amount']) / Decimal(trade['exec_sell_amount'])
                prices[order.buy_token] = int(prices[order.sell_token] * rate)
        
        return prices
    
    async def _submit_solution(self, auction_id: str, solution: CoWSettlement):
        """Submit solution to CoW Protocol"""
        solution_data = {
            'auctionId': auction_id,
            'prices': solution.clearing_prices,
            'trades': solution.trades,
            'interactions': solution.interactions,
            'score': str(solution.score)
        }
        
        # Sign solution
        signature = self._sign_solution(solution_data)
        solution_data['signature'] = signature
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/solver/solution",
                json=solution_data
            ) as response:
                if response.status == 200:
                    print(f"✅ Solution submitted for auction {auction_id}")
                    self.metrics['settlements_submitted'] += 1
                else:
                    print(f"❌ Solution submission failed: {await response.text()}")
    
    def _sign_solution(self, solution_data: Dict) -> str:
        """Sign solution with solver account"""
        if not self.solver_account:
            raise ValueError("Solver account not configured")
        
        # Create message hash
        message = json.dumps(solution_data, sort_keys=True)
        message_hash = Web3.keccak(text=message)
        
        # Sign with solver account
        signature = self.solver_account.signHash(message_hash)
        
        return signature.signature.hex()
    
    def _estimate_order_size_usd(self, order: CoWOrder) -> float:
        """Estimate order size in USD"""
        # Simplified - in production use price oracle
        token_prices = {
            '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 2000,  # WETH
            '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48': 1,      # USDC
            '0x6B175474E89094C44Da98b954EedeAC495271d0F': 1,      # DAI
        }
        
        price = token_prices.get(order.sell_token, 0)
        decimals = 18 if order.sell_token == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2' else 6
        
        return (order.sell_amount / 10**decimals) * price
    
    async def _calculate_input_for_exact_output(
        self,
        token_in: str,
        token_out: str,
        exact_output: int
    ) -> Optional[int]:
        """Calculate input needed for exact output amount"""
        # Binary search for the right input amount
        low = exact_output // 2
        high = exact_output * 2
        
        while low < high:
            mid = (low + high) // 2
            
            quote = await self.pathfinder.find_best_route(token_in, token_out, mid)
            
            if not quote:
                return None
            
            if quote.amount_out < exact_output:
                low = mid + 1
            else:
                high = mid
        
        return low
    
    def _parse_auction_order(self, order_data: Dict) -> CoWOrder:
        """Parse order from auction data"""
        return CoWOrder(
            sell_token=order_data['sellToken'],
            buy_token=order_data['buyToken'],
            sell_amount=int(order_data['sellAmount']),
            buy_amount=int(order_data['buyAmount']),
            valid_to=order_data['validTo'],
            app_data=order_data['appData'],
            fee_amount=int(order_data['feeAmount']),
            kind=order_data['kind'],
            partially_fillable=order_data['partiallyFillable'],
            receiver=order_data['receiver'],
            signature=order_data['signature'],
            from_address=order_data['owner']
        )

# Integration with main ATOM system
class ATOMComplete:
    """Complete ATOM system with all components"""
    
    def __init__(self, config_path: str = 'config.json'):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Setup Web3
        self.w3 = self._setup_web3()
        
        # Initialize all components
        self.monitor = ATOMDexMonitor(self.config)
        self.pathfinder = ATOMPathfinder(self.config, self.w3)
        self.mev_protection = ATOMMEVProtection(self.config, self.w3, self._setup_account())
        self.cow_integration = ATOMCoWIntegration(self.config, self.w3, self.pathfinder)
        self.arbitrage_finder = SmartArbitrageFinder(self.pathfinder, self.config)
        
        # Metrics aggregation
        self.metrics = {
            'start_time': time.time(),
            'total_profit_wei': 0,
            'total_gas_spent_wei': 0,
            'successful_trades': 0,
            'failed_trades': 0
        }
    
    def _setup_web3(self) -> Web3:
        """Setup Web3 connection"""
        for endpoint in self.config['rpc_endpoints']:
            try:
                if endpoint.startswith('wss://'):
                    w3 = Web3(Web3.WebsocketProvider(endpoint))
                else:
                    w3 = Web3(Web3.HTTPProvider(endpoint))
                
                if w3.isConnected():
                    return w3
            except Exception:
                continue
        
        raise ConnectionError("Failed to connect to any RPC endpoint")
    
    def _setup_account(self) -> 'LocalAccount':
        """Setup account for signing"""
        from eth_account import Account
        
        private_key = self.config.get('private_key')
        if not private_key:
            # Support hardware wallet
            return self._setup_hardware_wallet()
        
        return Account.from_key(private_key)
    
    def _setup_hardware_wallet(self) -> 'LocalAccount':
        """Setup hardware wallet integration"""
        # Placeholder for hardware wallet support
        raise NotImplementedError("Hardware wallet support coming soon")
    
    async def run(self):
        """Run complete ATOM system"""
        print("""
        ╔═══════════════════════════════════════╗
        ║          ATOM v2 - Starting           ║
        ║   Arbitrage Trustless On-chain Module ║
        ╚═══════════════════════════════════════╝
        """)
        
        print(f"📊 Network: {self.config.get('network', 'mainnet')}")
        print(f"💰 Min Profit: {Web3.fromWei(self.config.get('min_profit_wei', 0), 'ether')} ETH")
        print(f"🛡️  MEV Protection: {'Enabled' if self.config.get('flashbots_enabled', True) else 'Disabled'}")
        print(f"🐮 CoW Integration: {'Enabled' if self.config.get('cow_enabled', True) else 'Disabled'}")
        print()
        
        # Start all components
        tasks = [
            self._run_dex_monitor(),
            self._run_arbitrage_finder(),
            self._run_cow_monitor() if self.config.get('cow_enabled', True) else None,
            self._run_metrics_reporter()
        ]
        
        tasks = [t for t in tasks if t is not None]
        
        await asyncio.gather(*tasks)
    
    async def _run_dex_monitor(self):
        """Run DEX monitoring with arbitrage execution"""
        # Override the execution method
        self.monitor._execute_arbitrage = self._execute_smart_arbitrage
        
        await self.monitor.start_monitoring(self.config['tokens'])
    
    async def _run_arbitrage_finder(self):
        """Run continuous arbitrage finding with smart routing"""
        while True:
            try:
                # Find arbitrage opportunities using pathfinding
                opportunities = await self.arbitrage_finder.find_arbitrage_with_routing(
                    self.config['tokens']
                )
                
                for opp in opportunities[:3]:  # Process top 3
                    await self._execute_routed_arbitrage(opp)
                
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"Arbitrage finder error: {e}")
                await asyncio.sleep(10)
    
    async def _run_cow_monitor(self):
        """Run CoW Protocol monitoring"""
        await self.cow_integration.start_monitoring()
    
    async def _execute_smart_arbitrage(self, opportunity: 'ArbitrageOpportunity'):
        """Execute arbitrage with all protections and optimizations"""
        start_time = time.time()
        
        try:
            # Check if this can be done through CoW
            cow_opportunity = await self._check_cow_alternative(opportunity)
            
            if cow_opportunity:
                print("🐮 Executing through CoW Protocol")
                await self.cow_integration._execute_cow_arbitrage(cow_opportunity)
            else:
                # Execute with MEV protection
                receipt = await self.mev_protection.execute_arbitrage_protected(
                    opportunity,
                    self.config['arbitrage_contract_address']
                )
                
                if receipt and receipt['status'] == 1:
                    self._record_success(opportunity, receipt, time.time() - start_time)
                else:
                    self._record_failure(opportunity, time.time() - start_time)
                    
        except Exception as e:
            print(f"Execution error: {e}")
            self._record_failure(opportunity, time.time() - start_time)
    
    async def _execute_routed_arbitrage(self, opportunity: Dict):
        """Execute arbitrage found through smart routing"""
        # Convert to standard opportunity format
        standard_opp = ArbitrageOpportunity(
            buy_quote=PriceQuote(
                dex=opportunity['route_ab'].aggregator,
                token_in=opportunity['token_a'],
                token_out=opportunity['token_b'],
                amount_in=opportunity['route_ab'].amount_in,
                amount_out=opportunity['route_ab'].amount_out,
                gas_estimate=opportunity['route_ab'].gas_estimate,
                pool_address='0x0000000000000000000000000000000000000000',  # Multiple pools
                timestamp=time.time(),
                block_number=self.w3.eth.block_number
            ),
            sell_quote=PriceQuote(
                dex=opportunity['route_ba'].aggregator,
                token_in=opportunity['token_b'],
                token_out=opportunity['token_a'],
                amount_in=opportunity['route_ba'].amount_in,
                amount_out=opportunity['route_ba'].amount_out,
                gas_estimate=opportunity['route_ba'].gas_estimate,
                pool_address='0x0000000000000000000000000000000000000000',
                timestamp=time.time(),
                block_number=self.w3.eth.block_number
            ),
            profit_wei=opportunity['profit'],
            profit_percentage=Decimal(str(opportunity['roi'])),
            gas_cost_wei=opportunity['gas_cost'],
            net_profit_wei=opportunity['net_profit'],
            path=[opportunity['token_a'], opportunity['token_b'], opportunity['token_a']]
        )
        
        await self._execute_smart_arbitrage(standard_opp)
    
    async def _check_cow_alternative(self, opportunity: 'ArbitrageOpportunity') -> Optional[ArbitrageWithCoW]:
        """Check if arbitrage can be done through CoW"""
        # Look for matching CoW orders
        cow_orders = self.cow_integration.monitored_orders.values()
        
        for order in cow_orders:
            if (order.sell_token == opportunity.buy_quote.token_in and
                order.buy_token == opportunity.buy_quote.token_out):
                
                # Check if CoW order provides arbitrage
                cow_arb = await self.cow_integration._check_arbitrage_opportunity(order)
                if cow_arb and cow_arb.profit_wei > opportunity.net_profit_wei:
                    return cow_arb
        
        return None
    
    def _record_success(self, opportunity: 'ArbitrageOpportunity', receipt: Dict, execution_time: float):
        """Record successful trade"""
        gas_cost = receipt['gasUsed'] * receipt['effectiveGasPrice']
        actual_profit = opportunity.profit_wei - gas_cost
        
        self.metrics['successful_trades'] += 1
        self.metrics['total_profit_wei'] += actual_profit
        self.metrics['total_gas_spent_wei'] += gas_cost
        
        print(f"""
        ✅ Trade Successful
        ├─ Profit: {Web3.fromWei(actual_profit, 'ether'):.4f} ETH
        ├─ Gas: {Web3.fromWei(gas_cost, 'ether'):.4f} ETH
        ├─ Time: {execution_time:.2f}s
        └─ Tx: {receipt['transactionHash'].hex()}
        """)
    
    def _record_failure(self, opportunity: 'ArbitrageOpportunity', execution_time: float):
        """Record failed trade"""
        self.metrics['failed_trades'] += 1
        
        print(f"""
        ❌ Trade Failed
        ├─ Expected Profit: {Web3.fromWei(opportunity.net_profit_wei, 'ether'):.4f} ETH
        └─ Time: {execution_time:.2f}s
        """)
    
    async def _run_metrics_reporter(self):
        """Report metrics periodically"""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            
            uptime = time.time() - self.metrics['start_time']
            total_trades = self.metrics['successful_trades'] + self.metrics['failed_trades']
            success_rate = (self.metrics['successful_trades'] / total_trades * 100) if total_trades > 0 else 0
            
            print(f"""
            📊 ATOM Performance Report
            ├─ Uptime: {uptime/3600:.1f} hours
            ├─ Total Trades: {total_trades}
            ├─ Success Rate: {success_rate:.1f}%
            ├─ Total Profit: {Web3.fromWei(self.metrics['total_profit_wei'], 'ether'):.4f} ETH
            ├─ Gas Spent: {Web3.fromWei(self.metrics['total_gas_spent_wei'], 'ether'):.4f} ETH
            └─ Net Profit: {Web3.fromWei(self.metrics['total_profit_wei'] - self.metrics['total_gas_spent_wei'], 'ether'):.4f} ETH
            """)

# Import required components (these would be in separate files in production)
from atom_core import ATOMDexMonitor, ArbitrageOpportunity, PriceQuote
from atom_mev_protection import ATOMMEVProtection
from atom_pathfinding import ATOMPathfinder, SmartArbitrageFinder, RouteQuote