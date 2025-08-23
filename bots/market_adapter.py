#!/usr/bin/env python3
"""
Market Condition Adaptation System
Adjusts trading strategies based on market volatility, liquidity, and network conditions
"""

import asyncio
import json
import logging
import os
import time
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import aiohttp
import numpy as np
from collections import deque

logger = logging.getLogger(__name__)

class MarketConditionAdapter:
    def __init__(self):
        self.load_config()
        self.price_history = deque(maxlen=1000)  # Store last 1000 price points
        self.volume_history = deque(maxlen=100)   # Store last 100 volume points
        self.gas_price_history = deque(maxlen=100) # Store last 100 gas price points
        self.current_conditions = {
            'volatility': 'normal',
            'liquidity': 'normal',
            'network_congestion': 'normal',
            'market_trend': 'neutral'
        }
        self.strategy_adjustments = {}
        
    def load_config(self):
        """Load market adaptation configuration"""
        # Volatility thresholds
        self.low_volatility_threshold = Decimal(os.getenv('LOW_VOLATILITY_THRESHOLD', '0.5'))  # 0.5%
        self.high_volatility_threshold = Decimal(os.getenv('HIGH_VOLATILITY_THRESHOLD', '3.0'))  # 3.0%
        
        # Liquidity thresholds (in USD)
        self.low_liquidity_threshold = Decimal(os.getenv('LOW_LIQUIDITY_THRESHOLD', '10000'))
        self.high_liquidity_threshold = Decimal(os.getenv('HIGH_LIQUIDITY_THRESHOLD', '1000000'))
        
        # Gas price thresholds (in gwei)
        self.low_gas_threshold = Decimal(os.getenv('LOW_GAS_THRESHOLD', '20'))
        self.high_gas_threshold = Decimal(os.getenv('HIGH_GAS_THRESHOLD', '100'))
        
        # Base trading parameters
        self.base_min_profit_bps = Decimal(os.getenv('ATOM_MIN_PROFIT_THRESHOLD_BPS', '23'))
        self.base_max_trade_size = Decimal(os.getenv('MAX_TRADE_AMOUNT_USD', '50000'))
        self.base_max_slippage_bps = Decimal(os.getenv('MAX_SLIPPAGE_BPS', '300'))
        
    def update_price_data(self, price_update: Dict):
        """Update price history for volatility calculation"""
        try:
            timestamp = price_update.get('timestamp', time.time())
            price = Decimal(str(price_update.get('token0_price', 0)))
            volume = Decimal(str(price_update.get('volume_usd', 0)))
            
            self.price_history.append({
                'timestamp': timestamp,
                'price': price,
                'pair': price_update.get('pair', 'unknown'),
                'dex': price_update.get('dex', 'unknown')
            })
            
            self.volume_history.append({
                'timestamp': timestamp,
                'volume': volume,
                'pair': price_update.get('pair', 'unknown')
            })
            
        except Exception as e:
            logger.error(f"Error updating price data: {e}")
            
    def update_gas_price(self, gas_price_gwei: Decimal):
        """Update gas price history"""
        self.gas_price_history.append({
            'timestamp': time.time(),
            'gas_price': gas_price_gwei
        })
        
    def calculate_volatility(self, lookback_minutes: int = 60) -> Decimal:
        """Calculate price volatility over specified time period"""
        try:
            cutoff_time = time.time() - (lookback_minutes * 60)
            recent_prices = [
                p for p in self.price_history 
                if p['timestamp'] > cutoff_time
            ]
            
            if len(recent_prices) < 10:
                return Decimal('1.0')  # Default moderate volatility
                
            prices = [float(p['price']) for p in recent_prices]
            
            # Calculate standard deviation of price changes
            price_changes = []
            for i in range(1, len(prices)):
                change = (prices[i] - prices[i-1]) / prices[i-1] * 100
                price_changes.append(change)
                
            if not price_changes:
                return Decimal('1.0')
                
            volatility = Decimal(str(np.std(price_changes)))
            return volatility
            
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return Decimal('1.0')
            
    def calculate_liquidity_condition(self) -> str:
        """Determine current liquidity conditions"""
        try:
            if not self.volume_history:
                return 'normal'
                
            # Calculate average volume over last 30 minutes
            cutoff_time = time.time() - 1800  # 30 minutes
            recent_volumes = [
                v['volume'] for v in self.volume_history 
                if v['timestamp'] > cutoff_time
            ]
            
            if not recent_volumes:
                return 'normal'
                
            avg_volume = sum(recent_volumes) / len(recent_volumes)
            
            if avg_volume < self.low_liquidity_threshold:
                return 'low'
            elif avg_volume > self.high_liquidity_threshold:
                return 'high'
            else:
                return 'normal'
                
        except Exception as e:
            logger.error(f"Error calculating liquidity condition: {e}")
            return 'normal'
            
    def calculate_network_congestion(self) -> str:
        """Determine network congestion level"""
        try:
            if not self.gas_price_history:
                return 'normal'
                
            # Get recent gas prices (last 10 minutes)
            cutoff_time = time.time() - 600
            recent_gas_prices = [
                g['gas_price'] for g in self.gas_price_history 
                if g['timestamp'] > cutoff_time
            ]
            
            if not recent_gas_prices:
                return 'normal'
                
            avg_gas_price = sum(recent_gas_prices) / len(recent_gas_prices)
            
            if avg_gas_price < self.low_gas_threshold:
                return 'low'
            elif avg_gas_price > self.high_gas_threshold:
                return 'high'
            else:
                return 'normal'
                
        except Exception as e:
            logger.error(f"Error calculating network congestion: {e}")
            return 'normal'
            
    def determine_market_trend(self) -> str:
        """Determine overall market trend"""
        try:
            if len(self.price_history) < 20:
                return 'neutral'
                
            # Get prices from last hour
            cutoff_time = time.time() - 3600
            recent_prices = [
                p for p in self.price_history 
                if p['timestamp'] > cutoff_time
            ]
            
            if len(recent_prices) < 10:
                return 'neutral'
                
            # Calculate trend using linear regression
            timestamps = [p['timestamp'] for p in recent_prices]
            prices = [float(p['price']) for p in recent_prices]
            
            # Simple trend calculation
            first_half = prices[:len(prices)//2]
            second_half = prices[len(prices)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            trend_change = (second_avg - first_avg) / first_avg * 100
            
            if trend_change > 2:
                return 'bullish'
            elif trend_change < -2:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Error determining market trend: {e}")
            return 'neutral'
            
    def update_market_conditions(self):
        """Update all market condition assessments"""
        try:
            volatility = self.calculate_volatility()
            
            # Classify volatility
            if volatility < self.low_volatility_threshold:
                volatility_condition = 'low'
            elif volatility > self.high_volatility_threshold:
                volatility_condition = 'high'
            else:
                volatility_condition = 'normal'
                
            self.current_conditions = {
                'volatility': volatility_condition,
                'volatility_value': volatility,
                'liquidity': self.calculate_liquidity_condition(),
                'network_congestion': self.calculate_network_congestion(),
                'market_trend': self.determine_market_trend(),
                'last_updated': time.time()
            }
            
            # Update strategy adjustments based on conditions
            self._calculate_strategy_adjustments()
            
        except Exception as e:
            logger.error(f"Error updating market conditions: {e}")
            
    def _calculate_strategy_adjustments(self):
        """Calculate strategy adjustments based on market conditions"""
        try:
            adjustments = {
                'min_profit_bps': self.base_min_profit_bps,
                'max_trade_size': self.base_max_trade_size,
                'max_slippage_bps': self.base_max_slippage_bps,
                'trade_frequency_multiplier': Decimal('1.0'),
                'risk_multiplier': Decimal('1.0')
            }
            
            # Volatility adjustments
            if self.current_conditions['volatility'] == 'high':
                # High volatility: increase profit threshold, reduce trade size
                adjustments['min_profit_bps'] *= Decimal('1.5')
                adjustments['max_trade_size'] *= Decimal('0.7')
                adjustments['max_slippage_bps'] *= Decimal('1.3')
                adjustments['risk_multiplier'] = Decimal('1.5')
            elif self.current_conditions['volatility'] == 'low':
                # Low volatility: slightly reduce profit threshold, increase frequency
                adjustments['min_profit_bps'] *= Decimal('0.8')
                adjustments['trade_frequency_multiplier'] = Decimal('1.2')
                adjustments['risk_multiplier'] = Decimal('0.8')
                
            # Liquidity adjustments
            if self.current_conditions['liquidity'] == 'low':
                # Low liquidity: increase slippage tolerance, reduce trade size
                adjustments['max_slippage_bps'] *= Decimal('1.5')
                adjustments['max_trade_size'] *= Decimal('0.5')
                adjustments['min_profit_bps'] *= Decimal('1.2')
            elif self.current_conditions['liquidity'] == 'high':
                # High liquidity: can trade larger sizes with tighter spreads
                adjustments['max_trade_size'] *= Decimal('1.3')
                adjustments['min_profit_bps'] *= Decimal('0.9')
                
            # Network congestion adjustments
            if self.current_conditions['network_congestion'] == 'high':
                # High gas prices: increase profit threshold significantly
                adjustments['min_profit_bps'] *= Decimal('2.0')
                adjustments['trade_frequency_multiplier'] = Decimal('0.5')
            elif self.current_conditions['network_congestion'] == 'low':
                # Low gas prices: can be more aggressive
                adjustments['min_profit_bps'] *= Decimal('0.9')
                adjustments['trade_frequency_multiplier'] = Decimal('1.3')
                
            # Market trend adjustments
            if self.current_conditions['market_trend'] == 'bullish':
                # Bullish trend: slightly more aggressive
                adjustments['trade_frequency_multiplier'] *= Decimal('1.1')
                adjustments['max_trade_size'] *= Decimal('1.1')
            elif self.current_conditions['market_trend'] == 'bearish':
                # Bearish trend: more conservative
                adjustments['min_profit_bps'] *= Decimal('1.1')
                adjustments['max_trade_size'] *= Decimal('0.9')
                adjustments['risk_multiplier'] *= Decimal('1.2')
                
            # Ensure reasonable bounds
            adjustments['min_profit_bps'] = max(
                Decimal('10'), 
                min(Decimal('200'), adjustments['min_profit_bps'])
            )
            adjustments['max_trade_size'] = max(
                Decimal('100'), 
                min(Decimal('100000'), adjustments['max_trade_size'])
            )
            adjustments['max_slippage_bps'] = max(
                Decimal('100'), 
                min(Decimal('1000'), adjustments['max_slippage_bps'])
            )
            
            self.strategy_adjustments = adjustments
            
            logger.info(f"Strategy adjusted for {self.current_conditions}: "
                       f"min_profit={adjustments['min_profit_bps']}bps, "
                       f"max_size=${adjustments['max_trade_size']}, "
                       f"max_slippage={adjustments['max_slippage_bps']}bps")
            
        except Exception as e:
            logger.error(f"Error calculating strategy adjustments: {e}")
            
    def get_adjusted_parameters(self) -> Dict:
        """Get current adjusted trading parameters"""
        return {
            'market_conditions': self.current_conditions,
            'strategy_adjustments': self.strategy_adjustments,
            'recommended_action': self._get_recommended_action()
        }
        
    def _get_recommended_action(self) -> str:
        """Get recommended trading action based on current conditions"""
        try:
            volatility = self.current_conditions['volatility']
            liquidity = self.current_conditions['liquidity']
            congestion = self.current_conditions['network_congestion']
            
            # High risk conditions
            if (volatility == 'high' and liquidity == 'low') or congestion == 'high':
                return 'conservative'
            
            # Optimal conditions
            elif volatility == 'normal' and liquidity == 'high' and congestion == 'low':
                return 'aggressive'
            
            # Good conditions
            elif volatility == 'low' and congestion == 'normal':
                return 'moderate_aggressive'
            
            # Default
            else:
                return 'normal'
                
        except Exception as e:
            logger.error(f"Error getting recommended action: {e}")
            return 'normal'
            
    def should_pause_trading(self) -> bool:
        """Determine if trading should be paused due to extreme conditions"""
        try:
            conditions = self.current_conditions
            
            # Pause if extreme volatility and low liquidity
            if (conditions['volatility'] == 'high' and 
                conditions['liquidity'] == 'low' and
                conditions['network_congestion'] == 'high'):
                return True
                
            # Pause if volatility is extremely high
            if (hasattr(conditions, 'volatility_value') and 
                conditions['volatility_value'] > Decimal('10.0')):  # 10% volatility
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking pause condition: {e}")
            return False
            
    def get_market_summary(self) -> Dict:
        """Get comprehensive market condition summary"""
        return {
            'conditions': self.current_conditions,
            'adjustments': self.strategy_adjustments,
            'recommended_action': self._get_recommended_action(),
            'should_pause': self.should_pause_trading(),
            'data_points': {
                'price_history_count': len(self.price_history),
                'volume_history_count': len(self.volume_history),
                'gas_price_history_count': len(self.gas_price_history)
            }
        }
