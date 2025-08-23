#!/usr/bin/env python3
"""
Production MEV Protection - Flashbots Protect and sandwich attack prevention
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional
from web3 import Web3
import aiohttp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionMEVProtection:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.load_config()
        self.recent_transactions = []
        self.sandwich_detection_enabled = True
        
    def load_config(self):
        """Load MEV protection configuration"""
        self.use_flashbots_protect = True  # Always use on mainnet
        self.flashbots_protect_rpc = 'https://rpc.flashbots.net/fast'
        self.private_mempool_enabled = True
        self.max_priority_fee = 2 * 10**9  # 2 gwei
        self.max_fee_per_gas = 100 * 10**9  # 100 gwei
        
    def detect_sandwich_attack(self, token_in: str, token_out: str, amount_in: int) -> bool:
        """Detect potential sandwich attacks"""
        if not self.sandwich_detection_enabled:
            return False
            
        try:
            # Get pending transactions
            pending_block = self.w3.eth.get_block('pending', full_transactions=True)
            
            # Look for large transactions in same token pair
            suspicious_count = 0
            for tx in pending_block.transactions[-20:]:  # Check last 20 pending
                if tx.to and tx.input and len(tx.input) > 10:
                    # Simple heuristic: high gas price + same tokens
                    if (tx.gasPrice > self.w3.eth.gas_price * 1.5 and
                        self._involves_same_tokens(tx.input, token_in, token_out)):
                        suspicious_count += 1
                        
            return suspicious_count >= 2
            
        except Exception as e:
            logger.debug(f"Sandwich detection error: {e}")
            return False
            
    def _involves_same_tokens(self, tx_input: str, token_in: str, token_out: str) -> bool:
        """Check if transaction involves same tokens"""
        try:
            tx_data = tx_input.lower()
            return (token_in.lower()[2:] in tx_data and token_out.lower()[2:] in tx_data)
        except:
            return False
            
    def optimize_gas_price(self, base_fee: Optional[int] = None) -> tuple[int, int]:
        """Optimize gas pricing for MEV protection"""
        try:
            if base_fee is None:
                latest_block = self.w3.eth.get_block('latest')
                base_fee = latest_block.baseFeePerGas
                
            # Conservative priority fee to avoid MEV targeting
            priority_fee = min(self.max_priority_fee, int(base_fee * 0.1))
            
            # Max fee with buffer
            max_fee = min(self.max_fee_per_gas, base_fee * 2 + priority_fee)
            
            return max_fee, priority_fee
            
        except Exception as e:
            logger.error(f"Gas optimization error: {e}")
            return self.max_fee_per_gas, self.max_priority_fee
            
    async def send_protected_transaction(self, signed_transaction) -> str:
        """Send transaction with MEV protection"""
        if self.use_flashbots_protect and self.private_mempool_enabled:
            return await self._send_via_flashbots(signed_transaction)
        else:
            return await self._send_via_public_mempool(signed_transaction)
            
    async def _send_via_flashbots(self, signed_transaction) -> str:
        """Send via Flashbots Protect"""
        try:
            # Create bundle
            bundle_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_sendBundle",
                "params": [{
                    "txs": [signed_transaction.rawTransaction.hex()],
                    "blockNumber": hex(self.w3.eth.block_number + 1),
                    "minTimestamp": 0,
                    "maxTimestamp": int(time.time()) + 120
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.flashbots_protect_rpc,
                    json=bundle_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'result' in result:
                            logger.info("Transaction sent via Flashbots Protect")
                            return result['result']
                        else:
                            logger.warning(f"Flashbots error: {result}")
                            return await self._send_via_public_mempool(signed_transaction)
                    else:
                        logger.warning(f"Flashbots HTTP error: {response.status}")
                        return await self._send_via_public_mempool(signed_transaction)
                        
        except Exception as e:
            logger.warning(f"Flashbots failed: {e}, falling back to public mempool")
            return await self._send_via_public_mempool(signed_transaction)
            
    async def _send_via_public_mempool(self, signed_transaction) -> str:
        """Send via public mempool with protection"""
        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
            logger.info("Transaction sent via public mempool")
            return tx_hash.hex()
        except Exception as e:
            logger.error(f"Public mempool failed: {e}")
            raise
            
    def create_protected_transaction(
        self,
        contract_function,
        wallet_address: str,
        private_key: str,
        gas_limit: int = 500000
    ) -> dict:
        """Create transaction with MEV protection"""
        
        # Get optimized gas prices
        max_fee, priority_fee = self.optimize_gas_price()
        
        # Build transaction with EIP-1559
        transaction = contract_function.build_transaction({
            'from': wallet_address,
            'gas': gas_limit,
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': priority_fee,
            'nonce': self.w3.eth.get_transaction_count(wallet_address),
            'type': 2  # EIP-1559 transaction
        })
        
        # Sign transaction
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
        
        return signed_txn
        
    def analyze_mev_impact(self, tx_hash: str) -> Dict:
        """Analyze if transaction was affected by MEV"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            transaction = self.w3.eth.get_transaction(tx_hash)
            block = self.w3.eth.get_block(receipt.blockNumber, full_transactions=True)
            
            # Find transaction position
            tx_index = None
            for i, tx in enumerate(block.transactions):
                if tx.hash.hex() == tx_hash:
                    tx_index = i
                    break
                    
            if tx_index is None:
                return {'mev_detected': False, 'reason': 'Transaction not found'}
                
            # Check for sandwich pattern
            sandwich_detected = False
            if tx_index > 0 and tx_index < len(block.transactions) - 1:
                prev_tx = block.transactions[tx_index - 1]
                next_tx = block.transactions[tx_index + 1]
                
                # Sandwich heuristic: surrounding txs with higher gas to same contract
                if (prev_tx.to == transaction.to and next_tx.to == transaction.to and
                    prev_tx.gasPrice > transaction.gasPrice and
                    next_tx.gasPrice > transaction.gasPrice):
                    sandwich_detected = True
                    
            # Check for MEV failure
            mev_failure = (receipt.status == 0 and 
                          transaction.gasPrice < block.baseFeePerGas * 1.2)
            
            return {
                'mev_detected': sandwich_detected or mev_failure,
                'sandwich_attack': sandwich_detected,
                'mev_failure': mev_failure,
                'tx_index': tx_index,
                'block_size': len(block.transactions),
                'gas_price_percentile': self._calculate_gas_percentile(transaction, block.transactions)
            }
            
        except Exception as e:
            logger.error(f"MEV analysis error: {e}")
            return {'mev_detected': False, 'error': str(e)}
            
    def _calculate_gas_percentile(self, our_tx, all_txs) -> float:
        """Calculate gas price percentile in block"""
        try:
            gas_prices = sorted([tx.gasPrice for tx in all_txs if tx.gasPrice])
            our_gas_price = our_tx.gasPrice
            
            rank = sum(1 for price in gas_prices if price <= our_gas_price)
            return rank / len(gas_prices) if gas_prices else 0.5
            
        except:
            return 0.5
            
    def should_delay_transaction(self, token_in: str, token_out: str, amount_in: int) -> bool:
        """Determine if transaction should be delayed due to MEV risk"""
        
        # Check for sandwich attack risk
        if self.detect_sandwich_attack(token_in, token_out, amount_in):
            logger.warning("Sandwich attack detected, delaying transaction")
            return True
            
        # Check network congestion
        try:
            gas_price = self.w3.eth.gas_price
            if gas_price > self.max_fee_per_gas:
                logger.warning(f"High gas price {gas_price/10**9:.1f} gwei, delaying")
                return True
        except:
            pass
            
        return False
        
    def get_protection_stats(self) -> Dict:
        """Get MEV protection statistics"""
        return {
            'flashbots_enabled': self.use_flashbots_protect,
            'private_mempool_enabled': self.private_mempool_enabled,
            'sandwich_detection_enabled': self.sandwich_detection_enabled,
            'recent_transactions': len(self.recent_transactions),
            'max_fee_per_gas_gwei': self.max_fee_per_gas / 10**9,
            'max_priority_fee_gwei': self.max_priority_fee / 10**9
        }
        
    def add_transaction_monitoring(self, tx_hash: str, expected_profit: float):
        """Add transaction to monitoring"""
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
