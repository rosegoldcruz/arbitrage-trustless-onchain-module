#!/usr/bin/env python3
"""
Profit Calculation Engine - Real-time profit validation for Polygon arbitrage
SECURE: Environment Variables Only - NO HARDCODED SECRETS
"""

import logging
import os
import sys
from decimal import Decimal
from typing import Dict, Optional
from web3 import Web3

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.secure_config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProfitCalculator:
    def __init__(self):
        self.config = config
        self.setup_web3()
        self.setup_contracts()
        
    def setup_web3(self):
        """Initialize Web3 connection - SECURE: Environment Variables Only"""
        self.polygon_rpc = self.config.get('polygon_rpc_url')
        if not self.polygon_rpc:
            raise ValueError("POLYGON_RPC_URL environment variable required")

        self.w3 = Web3(Web3.HTTPProvider(self.polygon_rpc))
        if not self.w3.is_connected():
            # Try backup RPC
            backup_rpc = self.config.get('polygon_rpc_backup')
            if backup_rpc:
                self.w3 = Web3(Web3.HTTPProvider(backup_rpc))
                if not self.w3.is_connected():
                    raise Exception("Failed to connect to Polygon RPC (primary and backup)")
            else:
                raise Exception("Failed to connect to Polygon RPC")

        # Validate Polygon mainnet
        chain_id = self.w3.eth.chain_id
        if chain_id != 137:
            raise ValueError(f"Connected to wrong network. Expected Polygon (137), got {chain_id}")

        # Load configuration from secure config
        self.min_profit_bps = self.config.get('min_profit_threshold_bps')
        self.min_trade_size_usd = self.config.get('min_trade_size_usd')
        self.target_net_profit = self.config.get('target_net_profit')
        self.max_slippage_bps = Decimal('300')  # 3%
        self.aave_flash_loan_fee_bps = self.config.get('aave_flash_loan_fee_bps')
        self.max_gas_cost_usd = self.config.get('max_gas_cost_usd')

        # Token addresses from secure config
        self.tokens = self.config.get_tokens()

        # DEX addresses from secure config
        self.dex_routers = self.config.get_dex_routers()

    def setup_contracts(self):
        """Initialize contract instances"""
        # Uniswap V3 Quoter ABI
        quoter_abi = [
            {
                "inputs": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                ],
                "name": "quoteExactInputSingle",
                "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        # V2 Router ABI
        v2_abi = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"}
                ],
                "name": "getAmountsOut",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # Get quoter address from secure config
        uniswap_quoter_addr = self.config.get('uniswap_v3_quoter')
        if not uniswap_quoter_addr:
            raise ValueError("UNISWAP_V3_QUOTER environment variable required")

        self.uniswap_quoter = self.w3.eth.contract(
            address=uniswap_quoter_addr,
            abi=quoter_abi
        )
        
        self.quickswap_router = self.w3.eth.contract(
            address=self.dex_routers['quickswap'],
            abi=v2_abi
        )
        
        self.sushiswap_router = self.w3.eth.contract(
            address=self.dex_routers['sushiswap'],
            abi=v2_abi
        )
        
    def get_exact_quote(self, dex: str, token_in: str, token_out: str, amount_in: int) -> Optional[int]:
        """Get exact quote from DEX"""
        try:
            if dex == 'uniswap_v3':
                return self.uniswap_quoter.functions.quoteExactInputSingle(
                    token_in, token_out, 3000, amount_in, 0
                ).call()
            elif dex == 'quickswap':
                path = [token_in, token_out]
                amounts = self.quickswap_router.functions.getAmountsOut(amount_in, path).call()
                return amounts[-1]
            elif dex == 'sushiswap':
                path = [token_in, token_out]
                amounts = self.sushiswap_router.functions.getAmountsOut(amount_in, path).call()
                return amounts[-1]
            else:
                return None
        except Exception as e:
            logger.debug(f"Quote error for {dex}: {e}")
            return None
            
    def calculate_gas_cost_in_token(self, token_address: str, gas_price_gwei: int = 30) -> int:
        """Calculate gas cost in token terms"""
        # Estimated gas usage: 400,000 gas
        gas_usage = 400000
        gas_price_wei = gas_price_gwei * 10**9
        gas_cost_matic = gas_usage * gas_price_wei
        
        # Convert MATIC to token
        if token_address == self.tokens['WMATIC']:
            return gas_cost_matic
        elif token_address == self.tokens['USDC']:
            # Approximate: 1 MATIC = $0.8, so gas cost in USDC
            matic_usd_price = Decimal('0.8')
            gas_cost_usd = (Decimal(gas_cost_matic) / Decimal(10**18)) * matic_usd_price
            return int(gas_cost_usd * 10**6)  # USDC has 6 decimals
        elif token_address == self.tokens['WETH']:
            # Approximate: 1 ETH = 2000 MATIC
            return gas_cost_matic // 2000
        else:
            # Default to MATIC equivalent
            return gas_cost_matic
            
    def calculate_triangular_profit(
        self,
        token_a: str,
        token_b: str,
        token_c: str,
        amount_in: int,
        dex_a: str,
        dex_b: str,
        dex_c: str,
        gas_price_gwei: int = 50  # Higher default for premium execution
    ) -> Dict:
        """Calculate exact profit for triangular arbitrage"""
        
        try:
            # Step 1: A -> B
            amount_b = self.get_exact_quote(dex_a, token_a, token_b, amount_in)
            if not amount_b:
                return {'profitable': False, 'error': 'Step 1 quote failed'}
                
            # Step 2: B -> C
            amount_c = self.get_exact_quote(dex_b, token_b, token_c, amount_b)
            if not amount_c:
                return {'profitable': False, 'error': 'Step 2 quote failed'}
                
            # Step 3: C -> A
            final_amount = self.get_exact_quote(dex_c, token_c, token_a, amount_c)
            if not final_amount:
                return {'profitable': False, 'error': 'Step 3 quote failed'}
                
            # Calculate costs - AAVE V3 Flash Loan Economics
            aave_flash_loan_fee = (amount_in * int(self.aave_flash_loan_fee_bps)) // 10000  # 0.09%
            gas_cost = self.calculate_gas_cost_in_token(token_a, gas_price_gwei)
            total_costs = aave_flash_loan_fee + gas_cost

            # Convert to USD for validation
            amount_usd = self._convert_to_usd(token_a, amount_in)
            aave_fee_usd = float(aave_flash_loan_fee) / 10**18 * 2500  # Rough conversion
            gas_cost_usd = float(gas_cost) / 10**18 * 2500
            
            # Calculate profit - AAVE Economics
            if final_amount > amount_in + total_costs:
                gross_profit = final_amount - amount_in
                net_profit = gross_profit - total_costs
                profit_bps = (net_profit * 10000) // amount_in
                net_profit_usd = float(net_profit) / 10**18 * 2500  # Rough USD conversion

                # HIGH VALUE FILTER: Must meet minimum thresholds
                meets_bps_threshold = profit_bps >= self.min_profit_bps
                meets_usd_threshold = net_profit_usd >= float(self.target_net_profit)

                return {
                    'profitable': meets_bps_threshold and meets_usd_threshold,
                    'amount_in': amount_in,
                    'final_amount': final_amount,
                    'gross_profit': gross_profit,
                    'net_profit': net_profit,
                    'net_profit_usd': net_profit_usd,
                    'profit_bps': profit_bps,
                    'aave_flash_loan_fee': aave_flash_loan_fee,
                    'gas_cost': gas_cost,
                    'total_costs': total_costs,
                    'meets_bps_threshold': meets_bps_threshold,
                    'meets_usd_threshold': meets_usd_threshold,
                    'steps': {
                        'step1_out': amount_b,
                        'step2_out': amount_c,
                        'step3_out': final_amount
                    }
                }
            else:
                return {
                    'profitable': False,
                    'amount_in': amount_in,
                    'final_amount': final_amount,
                    'loss': amount_in + total_costs - final_amount
                }
                
        except Exception as e:
            return {'profitable': False, 'error': str(e)}

    def _convert_to_usd(self, token_address: str, amount: int) -> float:
        """Convert token amount to USD (rough estimate)"""
        if token_address == self.tokens['WETH']:
            return float(amount) / 10**18 * 2500  # ~$2500 per ETH
        elif token_address == self.tokens['USDC']:
            return float(amount) / 10**6  # USDC has 6 decimals
        elif token_address == self.tokens['USDT']:
            return float(amount) / 10**6  # USDT has 6 decimals
        elif token_address == self.tokens['DAI']:
            return float(amount) / 10**18  # DAI has 18 decimals
        elif token_address == self.tokens['WMATIC']:
            return float(amount) / 10**18 * 0.8  # ~$0.8 per MATIC
        else:
            return float(amount) / 10**18 * 1000  # Default estimate
            
    def find_optimal_trade_size(
        self,
        token_a: str,
        token_b: str, 
        token_c: str,
        dex_a: str,
        dex_b: str,
        dex_c: str,
        min_amount: int = None,
        max_amount: int = None
    ) -> Optional[Dict]:
        """Find optimal trade size for maximum profit"""
        
        if not min_amount:
            min_amount = int(0.01 * 10**18)  # 0.01 ETH equivalent
        if not max_amount:
            max_amount = int(10 * 10**18)    # 10 ETH equivalent
            
        best_result = None
        best_profit = 0
        
        # Test different amounts
        test_amounts = [
            min_amount,
            min_amount * 2,
            min_amount * 5,
            min_amount * 10,
            min_amount * 20,
            min_amount * 50,
            min_amount * 100,
            max_amount
        ]
        
        for amount in test_amounts:
            if amount > max_amount:
                continue
                
            result = self.calculate_triangular_profit(
                token_a, token_b, token_c, amount, dex_a, dex_b, dex_c
            )
            
            if result.get('profitable') and result.get('net_profit', 0) > best_profit:
                best_profit = result['net_profit']
                best_result = result
                
        return best_result
        
    def validate_opportunity_realtime(self, opportunity: Dict) -> Dict:
        """Validate opportunity with real-time quotes"""
        return self.calculate_triangular_profit(
            opportunity['token_a'],
            opportunity['token_b'],
            opportunity['token_c'],
            opportunity['amount_in'],
            opportunity['dex_a'],
            opportunity['dex_b'],
            opportunity['dex_c']
        )
        
    def calculate_minimum_trade_size(self, token_address: str, gas_price_gwei: int = 30) -> int:
        """Calculate minimum trade size to be profitable"""
        gas_cost = self.calculate_gas_cost_in_token(token_address, gas_price_gwei)
        flash_loan_fee_rate = self.flash_loan_fee_bps / Decimal('10000')
        min_profit_rate = self.min_profit_bps / Decimal('10000')
        
        # Minimum amount where (amount * min_profit_rate) > gas_cost + (amount * flash_loan_fee_rate)
        # Solving: amount * (min_profit_rate - flash_loan_fee_rate) > gas_cost
        net_profit_rate = min_profit_rate - flash_loan_fee_rate
        
        if net_profit_rate <= 0:
            return None  # Impossible to be profitable
            
        min_amount = int(Decimal(gas_cost) / net_profit_rate)
        return min_amount
        
    def get_profit_summary(self, opportunities: List[Dict]) -> Dict:
        """Get summary of profit calculations"""
        total_opportunities = len(opportunities)
        profitable_count = sum(1 for opp in opportunities if opp.get('profitable', False))
        
        if profitable_count == 0:
            return {
                'total_opportunities': total_opportunities,
                'profitable_count': 0,
                'profitability_rate': 0,
                'total_potential_profit': 0,
                'average_profit_bps': 0
            }
            
        profitable_opps = [opp for opp in opportunities if opp.get('profitable', False)]
        total_profit = sum(opp.get('net_profit', 0) for opp in profitable_opps)
        avg_profit_bps = sum(opp.get('profit_bps', 0) for opp in profitable_opps) / len(profitable_opps)
        
        return {
            'total_opportunities': total_opportunities,
            'profitable_count': profitable_count,
            'profitability_rate': profitable_count / total_opportunities,
            'total_potential_profit': total_profit,
            'average_profit_bps': avg_profit_bps,
            'best_opportunity': max(profitable_opps, key=lambda x: x.get('net_profit', 0))
        }
