#!/usr/bin/env python3
"""
MEV Protection Module
Implements Flashbots Protect RPC, transaction bundling, and sandwich attack detection
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Tuple
from web3 import Web3
from eth_account import Account
import aiohttp

logger = logging.getLogger(__name__)

class MEVProtection:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.load_config()
        self.setup_flashbots()
        self.sandwich_detection_enabled = True
        self.recent_transactions = []
        
    def load_config(self):
        """Load MEV protection configuration"""
        self.use_flashbots_protect = os.getenv('USE_FLASHBOTS_PROTECT', 'true').lower() == 'true'
        self.flashbots_protect_rpc = os.getenv('FLASHBOTS_PROTECT_RPC', 'https://rpc.flashbots.net/fast')
        self.private_mempool_enabled = os.getenv('PRIVATE_MEMPOOL_ENABLED', 'true').lower() == 'true'
        self.max_priority_fee = int(os.getenv('MAX_PRIORITY_FEE_GWEI', '2')) * 10**9
        self.max_fee_per_gas = int(os.getenv('MAX_FEE_PER_GAS_GWEI', '100')) * 10**9
        
    def setup_flashbots(self):
        """Initialize Flashbots Protect RPC connection"""
        if self.use_flashbots_protect:
            try:
                self.flashbots_w3 = Web3(Web3.HTTPProvider(self.flashbots_protect_rpc))
                logger.info("Flashbots Protect RPC initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Flashbots Protect: {e}")
                self.use_flashbots_protect = False
                
    def detect_sandwich_attack(self, token_in: str, token_out: str, amount_in: int) -> bool:
        """
        Detect potential sandwich attacks by analyzing mempool
        Returns True if sandwich attack is detected
        """
        if not self.sandwich_detection_enabled:
            return False
            
        try:
            # Get pending transactions from mempool
            pending_block = self.w3.eth.get_block('pending', full_transactions=True)
            
            # Look for large transactions in the same token pair
            suspicious_txs = []
            for tx in pending_block.transactions[-50:]:  # Check last 50 pending txs
                if tx.to and tx.input and len(tx.input) > 10:
                    # Check if transaction involves same tokens
                    if self._involves_same_tokens(tx.input, token_in, token_out):
                        # Check if transaction amount is significantly larger
                        if self._is_large_transaction(tx, amount_in):
                            suspicious_txs.append(tx)
                            
            if len(suspicious_txs) >= 2:
                logger.warning(f"Potential sandwich attack detected: {len(suspicious_txs)} suspicious transactions")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error in sandwich detection: {e}")
            return False
            
    def _involves_same_tokens(self, tx_input: str, token_in: str, token_out: str) -> bool:
        """Check if transaction input involves the same tokens"""
        try:
            # Simple check - look for token addresses in transaction data
            tx_data = tx_input.lower()
            return (token_in.lower()[2:] in tx_data and token_out.lower()[2:] in tx_data)
        except:
            return False
            
    def _is_large_transaction(self, tx, our_amount: int) -> bool:
        """Check if transaction is significantly larger than ours"""
        try:
            # Heuristic: if gas limit is much higher, likely a larger trade
            return tx.gas > 300000  # Typical arbitrage uses ~200k gas
        except:
            return False
            
    def optimize_gas_price(self, base_fee: Optional[int] = None) -> Tuple[int, int]:
        """
        Optimize gas pricing for MEV protection
        Returns (max_fee_per_gas, max_priority_fee_per_gas)
        """
        try:
            if base_fee is None:
                latest_block = self.w3.eth.get_block('latest')
                base_fee = latest_block.baseFeePerGas
                
            # Calculate optimal fees
            # Priority fee: enough to be included but not too high to attract MEV
            priority_fee = min(self.max_priority_fee, int(base_fee * 0.1))
            
            # Max fee: base fee + priority fee + buffer
            max_fee = min(self.max_fee_per_gas, base_fee * 2 + priority_fee)
            
            return max_fee, priority_fee
            
        except Exception as e:
            logger.error(f"Error optimizing gas price: {e}")
            return self.max_fee_per_gas, self.max_priority_fee
            
    def create_bundle(self, transactions: List[Dict]) -> Dict:
        """
        Create transaction bundle for Flashbots
        """
        bundle = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_sendBundle",
            "params": [
                {
                    "txs": [tx['raw_transaction'] for tx in transactions],
                    "blockNumber": hex(self.w3.eth.block_number + 1),
                    "minTimestamp": 0,
                    "maxTimestamp": int(time.time()) + 120  # 2 minutes from now
                }
            ]
        }
        return bundle
        
    async def send_protected_transaction(self, signed_transaction) -> str:
        """
        Send transaction through MEV protection
        """
        if self.use_flashbots_protect and self.private_mempool_enabled:
            return await self._send_via_flashbots(signed_transaction)
        else:
            return await self._send_via_public_mempool(signed_transaction)
            
    async def _send_via_flashbots(self, signed_transaction) -> str:
        """Send transaction via Flashbots Protect"""
        try:
            # Create bundle with single transaction
            bundle = self.create_bundle([{
                'raw_transaction': signed_transaction.rawTransaction.hex()
            }])
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.flashbots_protect_rpc,
                    json=bundle,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    result = await response.json()
                    
                    if 'result' in result:
                        logger.info("Transaction sent via Flashbots Protect")
                        return result['result']
                    else:
                        logger.error(f"Flashbots error: {result}")
                        # Fallback to public mempool
                        return await self._send_via_public_mempool(signed_transaction)
                        
        except Exception as e:
            logger.error(f"Flashbots submission failed: {e}")
            # Fallback to public mempool
            return await self._send_via_public_mempool(signed_transaction)
            
    async def _send_via_public_mempool(self, signed_transaction) -> str:
        """Send transaction via public mempool with protection"""
        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
            logger.info("Transaction sent via public mempool")
            return tx_hash.hex()
        except Exception as e:
            logger.error(f"Public mempool submission failed: {e}")
            raise
            
    def add_transaction_monitoring(self, tx_hash: str, expected_profit: float):
        """Add transaction to monitoring for MEV analysis"""
        self.recent_transactions.append({
            'tx_hash': tx_hash,
            'timestamp': time.time(),
            'expected_profit': expected_profit,
            'status': 'pending'
        })
        
        # Keep only recent transactions (last hour)
        cutoff_time = time.time() - 3600
        self.recent_transactions = [
            tx for tx in self.recent_transactions 
            if tx['timestamp'] > cutoff_time
        ]
        
    async def analyze_mev_impact(self, tx_hash: str) -> Dict:
        """
        Analyze if transaction was affected by MEV
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            transaction = self.w3.eth.get_transaction(tx_hash)
            block = self.w3.eth.get_block(receipt.blockNumber, full_transactions=True)
            
            # Find our transaction in the block
            tx_index = None
            for i, tx in enumerate(block.transactions):
                if tx.hash.hex() == tx_hash:
                    tx_index = i
                    break
                    
            if tx_index is None:
                return {'mev_detected': False, 'reason': 'Transaction not found in block'}
                
            # Check for sandwich attack pattern
            sandwich_detected = False
            if tx_index > 0 and tx_index < len(block.transactions) - 1:
                prev_tx = block.transactions[tx_index - 1]
                next_tx = block.transactions[tx_index + 1]
                
                # Simple heuristic: check if surrounding transactions are to same DEX
                if (prev_tx.to == transaction.to and next_tx.to == transaction.to and
                    prev_tx.gasPrice > transaction.gasPrice and
                    next_tx.gasPrice > transaction.gasPrice):
                    sandwich_detected = True
                    
            # Check if transaction failed due to MEV
            mev_failure = receipt.status == 0 and transaction.gasPrice < block.baseFeePerGas * 1.5
            
            return {
                'mev_detected': sandwich_detected or mev_failure,
                'sandwich_attack': sandwich_detected,
                'mev_failure': mev_failure,
                'tx_index': tx_index,
                'block_transactions': len(block.transactions),
                'gas_price_rank': self._calculate_gas_price_rank(transaction, block.transactions)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing MEV impact: {e}")
            return {'mev_detected': False, 'error': str(e)}
            
    def _calculate_gas_price_rank(self, our_tx, all_txs) -> float:
        """Calculate percentile rank of our gas price in the block"""
        try:
            gas_prices = [tx.gasPrice for tx in all_txs if tx.gasPrice]
            gas_prices.sort()
            
            our_gas_price = our_tx.gasPrice
            rank = sum(1 for price in gas_prices if price <= our_gas_price)
            
            return rank / len(gas_prices) if gas_prices else 0.5
            
        except:
            return 0.5
            
    def get_protection_stats(self) -> Dict:
        """Get MEV protection statistics"""
        total_txs = len(self.recent_transactions)
        if total_txs == 0:
            return {
                'total_transactions': 0,
                'flashbots_usage': 0,
                'mev_detected': 0,
                'protection_rate': 0
            }
            
        flashbots_used = sum(1 for tx in self.recent_transactions 
                           if tx.get('sent_via_flashbots', False))
        
        return {
            'total_transactions': total_txs,
            'flashbots_usage': flashbots_used / total_txs,
            'flashbots_enabled': self.use_flashbots_protect,
            'private_mempool_enabled': self.private_mempool_enabled,
            'sandwich_detection_enabled': self.sandwich_detection_enabled
        }

class TransactionBundler:
    """
    Advanced transaction bundling for MEV protection
    """
    
    def __init__(self, mev_protection: MEVProtection):
        self.mev_protection = mev_protection
        self.pending_bundles = []
        
    def create_arbitrage_bundle(self, arbitrage_txs: List[Dict]) -> Dict:
        """
        Create optimized bundle for arbitrage transactions
        """
        # Sort transactions by expected profit
        sorted_txs = sorted(arbitrage_txs, key=lambda x: x.get('expected_profit', 0), reverse=True)
        
        # Create bundle with optimal ordering
        bundle = {
            'transactions': sorted_txs,
            'target_block': self.mev_protection.w3.eth.block_number + 1,
            'max_block': self.mev_protection.w3.eth.block_number + 3,
            'created_at': time.time()
        }
        
        return bundle
        
    async def submit_bundle(self, bundle: Dict) -> bool:
        """
        Submit transaction bundle via Flashbots
        """
        try:
            flashbots_bundle = self.mev_protection.create_bundle(bundle['transactions'])
            
            # Submit bundle
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.mev_protection.flashbots_protect_rpc,
                    json=flashbots_bundle
                ) as response:
                    result = await response.json()
                    
                    if 'result' in result:
                        logger.info(f"Bundle submitted successfully: {result['result']}")
                        return True
                    else:
                        logger.error(f"Bundle submission failed: {result}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error submitting bundle: {e}")
            return False
