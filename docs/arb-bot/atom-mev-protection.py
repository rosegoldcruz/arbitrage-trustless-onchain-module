#!/usr/bin/env python3
"""
ATOM v2 - MEV Protection & Private Routing
Flashbots integration, RBF, and gas optimization
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal
import aiohttp
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from flashbots import flashbot
from eth_account.signers.local import LocalAccount

@dataclass
class TransactionBundle:
    """Transaction bundle for Flashbots submission"""
    transactions: List[str]  # Signed raw transactions
    block_number: int
    min_timestamp: Optional[int] = None
    max_timestamp: Optional[int] = None
    reverting_tx_hashes: List[str] = None
    uuid: str = None
    
    def __post_init__(self):
        if self.uuid is None:
            self.uuid = str(uuid.uuid4())

class ATOMMEVProtection:
    """MEV protection layer with Flashbots and private routing"""
    
    def __init__(self, config: Dict, w3: Web3, account: LocalAccount):
        self.config = config
        self.w3 = w3
        self.account = account
        
        # Setup Flashbots
        self.flashbots_enabled = config.get('flashbots_enabled', True)
        if self.flashbots_enabled:
            self.w3 = flashbot(w3, account, config.get('flashbots_relay_url', 'https://relay.flashbots.net'))
        
        # Transaction tracking
        self.pending_txs: Dict[str, Dict] = {}
        self.confirmed_txs: Dict[str, Dict] = {}
        self.dropped_txs: Dict[str, Dict] = {}
        
        # Gas tracking
        self.gas_history = []
        self.gas_predictor = GasPredictor(w3)
        
        # Performance metrics
        self.metrics = {
            'bundles_sent': 0,
            'bundles_included': 0,
            'txs_frontrun': 0,
            'gas_saved_wei': 0,
            'rbf_attempts': 0,
            'rbf_success': 0
        }
    
    async def execute_arbitrage_protected(self, opportunity: 'ArbitrageOpportunity', executor_contract: str) -> Optional[Dict]:
        """Execute arbitrage with MEV protection"""
        try:
            # 1. Check profitability with current gas
            gas_price = await self.gas_predictor.get_optimal_gas_price()
            
            if not self._is_profitable_with_gas(opportunity, gas_price):
                print(f"⛽ Skipping - not profitable at {Web3.fromWei(gas_price, 'gwei')} gwei")
                return None
            
            # 2. Build arbitrage transaction
            tx = await self._build_arbitrage_tx(opportunity, executor_contract, gas_price)
            
            # 3. Submit via best method
            if self.flashbots_enabled and self._should_use_flashbots(opportunity):
                return await self._submit_via_flashbots(tx, opportunity)
            else:
                return await self._submit_with_rbf(tx, opportunity)
                
        except Exception as e:
            print(f"❌ MEV protection error: {e}")
            return None
    
    def _is_profitable_with_gas(self, opportunity: 'ArbitrageOpportunity', gas_price: int) -> bool:
        """Check if arbitrage is still profitable with current gas price"""
        estimated_gas = opportunity.buy_quote.gas_estimate + opportunity.sell_quote.gas_estimate
        gas_cost_wei = estimated_gas * gas_price
        
        net_profit = opportunity.profit_wei - gas_cost_wei
        min_profit = self.config.get('min_profit_wei', Web3.toWei(0.01, 'ether'))
        
        return net_profit >= min_profit
    
    async def _build_arbitrage_tx(self, opportunity: 'ArbitrageOpportunity', executor_contract: str, gas_price: int) -> Dict:
        """Build arbitrage transaction"""
        # Encode arbitrage parameters
        params = self._encode_arbitrage_params(opportunity)
        
        # Build transaction
        nonce = self.w3.eth.get_transaction_count(self.account.address, 'pending')
        
        tx = {
            'from': self.account.address,
            'to': executor_contract,
            'value': 0,
            'data': params,
            'nonce': nonce,
            'chainId': self.w3.eth.chain_id
        }
        
        # EIP-1559 support
        latest_block = self.w3.eth.get_block('latest')
        if 'baseFeePerGas' in latest_block:
            # EIP-1559 transaction
            base_fee = latest_block['baseFeePerGas']
            priority_fee = self.config.get('priority_fee_gwei', 2) * 10**9
            
            tx.update({
                'maxFeePerGas': base_fee + priority_fee,
                'maxPriorityFeePerGas': priority_fee,
                'type': '0x2'
            })
        else:
            # Legacy transaction
            tx['gasPrice'] = gas_price
        
        # Estimate gas
        try:
            gas_estimate = self.w3.eth.estimate_gas(tx)
            tx['gas'] = int(gas_estimate * 1.2)  # 20% buffer
        except Exception as e:
            print(f"⚠️  Gas estimation failed: {e}")
            tx['gas'] = 500000  # Fallback
        
        return tx
    
    def _encode_arbitrage_params(self, opportunity: 'ArbitrageOpportunity') -> str:
        """Encode arbitrage parameters for smart contract"""
        # This should match your smart contract's executeArbitrage function
        # Example encoding for a typical arbitrage contract
        function_selector = Web3.keccak(text="executeArbitrage(address,address,uint256,address[],bytes)")[:4]
        
        # Encode parameters
        encoded_params = Web3.solidityKeccak(
            ['address', 'address', 'uint256', 'address[]', 'bytes'],
            [
                opportunity.buy_quote.token_in,
                opportunity.buy_quote.token_out,
                self.config['trade_amount_wei'],
                [opportunity.buy_quote.pool_address, opportunity.sell_quote.pool_address],
                b''  # Additional data
            ]
        )
        
        return function_selector + encoded_params
    
    def _should_use_flashbots(self, opportunity: 'ArbitrageOpportunity') -> bool:
        """Determine if Flashbots should be used"""
        # Use Flashbots for high-value opportunities
        min_flashbots_profit = self.config.get('min_flashbots_profit_wei', Web3.toWei(0.05, 'ether'))
        
        # Also consider if the opportunity is likely to be competitive
        is_popular_pair = self._is_popular_pair(opportunity.buy_quote.token_in, opportunity.buy_quote.token_out)
        
        return opportunity.net_profit_wei >= min_flashbots_profit or is_popular_pair
    
    def _is_popular_pair(self, token_a: str, token_b: str) -> bool:
        """Check if token pair is popular (likely to have MEV competition)"""
        popular_tokens = {
            '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  # WETH
            '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  # USDC
            '0x6B175474E89094C44Da98b954EedeAC495271d0F',  # DAI
            '0xdAC17F958D2ee523a2206206994597C13D831ec7',  # USDT
        }
        
        return token_a in popular_tokens and token_b in popular_tokens
    
    async def _submit_via_flashbots(self, tx: Dict, opportunity: 'ArbitrageOpportunity') -> Optional[Dict]:
        """Submit transaction via Flashbots"""
        print("🔒 Submitting via Flashbots...")
        
        # Sign transaction
        signed_tx = self.account.sign_transaction(tx)
        
        # Create bundle
        bundle = TransactionBundle(
            transactions=[signed_tx.rawTransaction.hex()],
            block_number=self.w3.eth.block_number + 1,
            min_timestamp=0,
            max_timestamp=int(time.time()) + 120  # 2 minute validity
        )
        
        # Track bundle
        self.pending_txs[bundle.uuid] = {
            'bundle': bundle,
            'opportunity': opportunity,
            'submitted_at': time.time(),
            'target_blocks': []
        }
        
        # Submit to multiple blocks
        results = []
        for block_offset in range(1, 4):  # Target next 3 blocks
            target_block = self.w3.eth.block_number + block_offset
            
            try:
                # Send bundle
                result = self.w3.flashbots.send_bundle(
                    bundle.transactions,
                    target_block_number=target_block
                )
                
                results.append(result)
                self.pending_txs[bundle.uuid]['target_blocks'].append(target_block)
                self.metrics['bundles_sent'] += 1
                
                print(f"   Bundle sent for block {target_block}")
                
            except Exception as e:
                print(f"   Failed to send bundle: {e}")
        
        # Wait for inclusion
        return await self._wait_for_flashbots_inclusion(bundle.uuid, results)
    
    async def _wait_for_flashbots_inclusion(self, bundle_uuid: str, results: List) -> Optional[Dict]:
        """Wait for Flashbots bundle inclusion"""
        max_wait_blocks = 5
        start_block = self.w3.eth.block_number
        
        while self.w3.eth.block_number < start_block + max_wait_blocks:
            # Check bundle status
            for result in results:
                try:
                    status = self.w3.flashbots.get_bundle_stats(
                        result['bundleHash'],
                        result['blockNumber']
                    )
                    
                    if status and status.get('isIncluded'):
                        print(f"✅ Bundle included in block {result['blockNumber']}")
                        self.metrics['bundles_included'] += 1
                        
                        # Get transaction receipt
                        bundle_data = self.pending_txs.get(bundle_uuid)
                        if bundle_data:
                            tx_hash = Web3.keccak(hexstr=bundle_data['bundle'].transactions[0])
                            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                            
                            # Record success
                            self.confirmed_txs[tx_hash.hex()] = {
                                'receipt': receipt,
                                'opportunity': bundle_data['opportunity'],
                                'method': 'flashbots'
                            }
                            
                            return receipt
                            
                except Exception as e:
                    pass
            
            await asyncio.sleep(1)
        
        print("⏱️  Bundle not included within timeout")
        return None
    
    async def _submit_with_rbf(self, tx: Dict, opportunity: 'ArbitrageOpportunity') -> Optional[Dict]:
        """Submit transaction with Replace-By-Fee support"""
        print("📤 Submitting transaction with RBF...")
        
        original_gas_price = tx.get('gasPrice') or tx.get('maxFeePerGas')
        tx_hash = None
        attempts = 0
        max_attempts = self.config.get('max_rbf_attempts', 3)
        
        while attempts < max_attempts:
            try:
                # Sign and send transaction
                signed_tx = self.account.sign_transaction(tx)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                print(f"   Tx sent: {tx_hash.hex()}")
                print(f"   Gas price: {Web3.fromWei(original_gas_price, 'gwei')} gwei")
                
                # Track transaction
                self.pending_txs[tx_hash.hex()] = {
                    'tx': tx,
                    'opportunity': opportunity,
                    'submitted_at': time.time(),
                    'gas_price': original_gas_price,
                    'attempts': attempts + 1
                }
                
                # Wait for confirmation with timeout
                receipt = await self._wait_for_tx_with_rbf(tx_hash, tx, opportunity)
                
                if receipt:
                    return receipt
                    
            except Exception as e:
                print(f"   Transaction error: {e}")
            
            # Increase gas price for retry
            attempts += 1
            if attempts < max_attempts:
                gas_increase = self.config.get('rbf_gas_increase_percent', 15)
                new_gas_price = int(original_gas_price * (1 + gas_increase / 100))
                
                if 'gasPrice' in tx:
                    tx['gasPrice'] = new_gas_price
                else:
                    tx['maxFeePerGas'] = new_gas_price
                    tx['maxPriorityFeePerGas'] = int(tx['maxPriorityFeePerGas'] * (1 + gas_increase / 100))
                
                print(f"   🔄 Retrying with {Web3.fromWei(new_gas_price, 'gwei')} gwei (attempt {attempts + 1})")
                self.metrics['rbf_attempts'] += 1
        
        return None
    
    async def _wait_for_tx_with_rbf(self, tx_hash: bytes, tx: Dict, opportunity: 'ArbitrageOpportunity') -> Optional[Dict]:
        """Wait for transaction confirmation with RBF option"""
        timeout = self.config.get('tx_timeout_seconds', 60)
        start_time = time.time()
        check_interval = 1
        
        while time.time() - start_time < timeout:
            try:
                # Check if transaction is mined
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                
                if receipt:
                    print(f"✅ Transaction confirmed in block {receipt['blockNumber']}")
                    
                    # Check if successful
                    if receipt['status'] == 1:
                        # Calculate actual gas used
                        gas_used = receipt['gasUsed'] * receipt['effectiveGasPrice']
                        self.gas_history.append({
                            'timestamp': time.time(),
                            'gas_used': gas_used,
                            'gas_price': receipt['effectiveGasPrice'],
                            'block': receipt['blockNumber']
                        })
                        
                        # Record success
                        self.confirmed_txs[tx_hash.hex()] = {
                            'receipt': receipt,
                            'opportunity': opportunity,
                            'method': 'rbf',
                            'gas_cost_wei': gas_used
                        }
                        
                        return receipt
                    else:
                        print(f"❌ Transaction reverted")
                        return None
                        
                # Check if transaction is still pending
                pending_tx = self.w3.eth.get_transaction(tx_hash)
                if not pending_tx:
                    print(f"⚠️  Transaction dropped from mempool")
                    self.dropped_txs[tx_hash.hex()] = self.pending_txs.pop(tx_hash.hex(), {})
                    return None
                    
            except Exception as e:
                # Transaction not found yet
                pass
            
            await asyncio.sleep(check_interval)
        
        print(f"⏱️  Transaction timeout after {timeout}s")
        return None

class GasPredictor:
    """Predict optimal gas prices using historical data"""
    
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.gas_history = []
        self.prediction_cache = {}
        self.cache_duration = 12  # seconds
    
    async def get_optimal_gas_price(self) -> int:
        """Get optimal gas price for arbitrage transaction"""
        # Check cache
        cache_key = int(time.time() / self.cache_duration)
        if cache_key in self.prediction_cache:
            return self.prediction_cache[cache_key]
        
        # Get current gas prices
        latest_block = self.w3.eth.get_block('latest', full_transactions=True)
        
        if 'baseFeePerGas' in latest_block:
            # EIP-1559 chain
            base_fee = latest_block['baseFeePerGas']
            
            # Analyze recent blocks for priority fees
            priority_fees = []
            for tx in latest_block['transactions'][:20]:  # Sample recent transactions
                if 'maxPriorityFeePerGas' in tx:
                    priority_fees.append(tx['maxPriorityFeePerGas'])
            
            if priority_fees:
                # Use 75th percentile for competitive but not excessive priority fee
                percentile_75 = sorted(priority_fees)[int(len(priority_fees) * 0.75)]
                optimal_price = base_fee + percentile_75
            else:
                # Default priority fee
                optimal_price = base_fee + (2 * 10**9)  # 2 gwei
        else:
            # Legacy gas pricing
            gas_prices = []
            for tx in latest_block['transactions'][:20]:
                if 'gasPrice' in tx:
                    gas_prices.append(tx['gasPrice'])
            
            if gas_prices:
                # Use slightly above median
                median_price = sorted(gas_prices)[len(gas_prices) // 2]
                optimal_price = int(median_price * 1.1)
            else:
                optimal_price = self.w3.eth.gas_price
        
        # Cache result
        self.prediction_cache[cache_key] = optimal_price
        
        return optimal_price
    
    async def predict_gas_spike(self, lookahead_blocks: int = 5) -> bool:
        """Predict if gas prices will spike in next few blocks"""
        # Analyze mempool density
        pending_count = self.w3.eth.get_block_transaction_count('pending')
        latest_count = self.w3.eth.get_block_transaction_count('latest')
        
        # High mempool congestion indicates potential gas spike
        congestion_ratio = pending_count / max(latest_count, 1)
        
        return congestion_ratio > 2.0

# Transaction logger
class TransactionLogger:
    """Log all transactions for analysis"""
    
    def __init__(self, log_file: str = "atom_transactions.jsonl"):
        self.log_file = log_file
    
    def log_transaction(self, tx_data: Dict):
        """Log transaction data"""
        log_entry = {
            'timestamp': time.time(),
            'tx_hash': tx_data.get('tx_hash'),
            'method': tx_data.get('method'),
            'opportunity': {
                'buy_dex': tx_data['opportunity'].buy_quote.dex,
                'sell_dex': tx_data['opportunity'].sell_quote.dex,
                'profit_wei': tx_data['opportunity'].profit_wei,
                'gas_cost_wei': tx_data.get('gas_cost_wei', 0)
            },
            'success': tx_data.get('success', False),
            'block_number': tx_data.get('block_number'),
            'gas_used': tx_data.get('gas_used'),
            'effective_gas_price': tx_data.get('effective_gas_price')
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

# Integration with main ATOM system
class ATOMExecutor:
    """Main executor combining monitoring and MEV protection"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.w3 = self._setup_web3()
        self.account = self._setup_account()
        
        # Initialize components
        from atom_core import ATOMDexMonitor
        self.monitor = ATOMDexMonitor(config)
        self.mev_protection = ATOMMEVProtection(config, self.w3, self.account)
        self.logger = TransactionLogger()
        
        # Deploy or load arbitrage contract
        self.arbitrage_contract = self._setup_arbitrage_contract()
    
    def _setup_web3(self) -> Web3:
        """Setup Web3 connection"""
        # Implementation from atom_core
        pass
    
    def _setup_account(self) -> LocalAccount:
        """Setup account for signing"""
        private_key = self.config.get('private_key')
        if not private_key:
            raise ValueError("Private key not configured")
        
        return Account.from_key(private_key)
    
    def _setup_arbitrage_contract(self) -> str:
        """Deploy or load arbitrage contract"""
        contract_address = self.config.get('arbitrage_contract_address')
        
        if not contract_address:
            print("📝 Deploying arbitrage contract...")
            # Deploy contract logic here
            contract_address = self._deploy_arbitrage_contract()
        
        return contract_address
    
    async def run(self):
        """Run the complete ATOM system"""
        print("🚀 ATOM v2 - Starting with MEV protection...")
        
        # Start monitoring with execution callback
        self.monitor._execute_arbitrage = self.execute_arbitrage
        
        # Run monitoring
        await self.monitor.start_monitoring(self.config['tokens'])
    
    async def execute_arbitrage(self, opportunity: 'ArbitrageOpportunity'):
        """Execute arbitrage with MEV protection"""
        start_time = time.time()
        
        try:
            # Execute with protection
            receipt = await self.mev_protection.execute_arbitrage_protected(
                opportunity,
                self.arbitrage_contract
            )
            
            if receipt:
                # Log success
                execution_time = time.time() - start_time
                
                self.logger.log_transaction({
                    'tx_hash': receipt['transactionHash'].hex(),
                    'method': 'flashbots' if opportunity.net_profit_wei > Web3.toWei(0.05, 'ether') else 'rbf',
                    'opportunity': opportunity,
                    'success': receipt['status'] == 1,
                    'block_number': receipt['blockNumber'],
                    'gas_used': receipt['gasUsed'],
                    'effective_gas_price': receipt['effectiveGasPrice'],
                    'gas_cost_wei': receipt['gasUsed'] * receipt['effectiveGasPrice'],
                    'execution_time': execution_time
                })
                
                # Calculate actual profit
                gas_cost = receipt['gasUsed'] * receipt['effectiveGasPrice']
                actual_profit = opportunity.profit_wei - gas_cost
                
                print(f"💰 Arbitrage executed successfully!")
                print(f"   Actual profit: {Web3.fromWei(actual_profit, 'ether')} ETH")
                print(f"   Execution time: {execution_time:.2f}s")
                
        except Exception as e:
            print(f"❌ Execution failed: {e}")
            
            self.logger.log_transaction({
                'opportunity': opportunity,
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time
            })