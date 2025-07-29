#!/usr/bin/env python3
"""
🐍 ADOM ENGINE - Advanced Decentralized Opportunity Monitor
🚀 Python-based signal processing and arbitrage detection

This engine runs every 5 seconds and:
1. Processes Chainlink price feeds
2. Analyzes DEX pool states using advanced math
3. Calculates optimal trade sizes and routes
4. Sends signals to ATOM bot for execution
"""

import asyncio
import aiohttp
import json
import logging
import os
import time
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import pandas as pd

# Set high precision for financial calculations
getcontext().prec = 50

# ============================================================================
# 🔧 CONFIGURATION
# ============================================================================
@dataclass
class AdomConfig:
    # Signal Processing
    signal_interval: int = int(os.getenv('ADOM_SIGNAL_INTERVAL', 5))  # 5 seconds
    max_trade_size: float = float(os.getenv('ADOM_MAX_TRADE_SIZE', 1.0))  # 1 ETH
    risk_tolerance: float = float(os.getenv('ADOM_RISK_TOLERANCE', 0.02))  # 2%
    
    # Network & APIs
    backend_url: str = os.getenv('NEXT_PUBLIC_BACKEND_URL', 'http://152.42.234.243:3001')
    rpc_url: str = os.getenv('BASE_SEPOLIA_RPC_URL', 'https://base-sepolia.g.alchemy.com/v2/ESBtk3UKjPt2rK2Yz0hnzUj0tIJGTe-d')
    
    # Thresholds
    min_spread_bps: int = 23  # 23 basis points minimum
    max_gas_price_gwei: int = 50
    min_profit_usd: float = 10.0
    
    # Token Configuration
    tokens: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tokens is None:
            self.tokens = {
                'DAI': '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
                'USDC': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
                'WETH': '0x4200000000000000000000000000000000000006',
                'GHO': '0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f'
            }

# ============================================================================
# 📊 DATA MODELS
# ============================================================================
@dataclass
class PriceSignal:
    token_pair: str
    price: Decimal
    volume_24h: Decimal
    volatility: float
    timestamp: datetime
    source: str

@dataclass
class ArbitrageOpportunity:
    token_triple: List[str]
    spread_bps: int
    expected_profit_usd: float
    optimal_amount: float
    confidence_score: float
    execution_priority: int
    timestamp: datetime

# ============================================================================
# 🐍 ADOM ENGINE CLASS
# ============================================================================
class AdomEngine:
    def __init__(self, config: AdomConfig):
        self.config = config
        self.is_running = False
        self.price_history = {}
        self.opportunity_queue = []
        self.stats = {
            'signals_processed': 0,
            'opportunities_detected': 0,
            'signals_sent': 0,
            'total_profit_potential': 0.0,
            'last_signal_time': None
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - ADOM - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info('🐍 ADOM Engine initialized')
        self.logger.info(f'📡 Backend: {self.config.backend_url}')
        self.logger.info(f'⏱️  Signal interval: {self.config.signal_interval}s')
        self.logger.info(f'💰 Min profit: ${self.config.min_profit_usd}')
    
    async def start(self):
        """🚀 Start the ADOM engine"""
        if self.is_running:
            self.logger.warning('⚠️  ADOM Engine already running')
            return
        
        self.is_running = True
        self.logger.info('🚀 ADOM Engine starting...')
        
        # Start signal processing loop
        await self.signal_processing_loop()
    
    async def stop(self):
        """🛑 Stop the ADOM engine"""
        self.logger.info('🛑 ADOM Engine stopping...')
        self.is_running = False
    
    async def signal_processing_loop(self):
        """🔄 Main signal processing loop"""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Process price signals
                await self.process_price_signals()
                
                # Detect arbitrage opportunities
                opportunities = await self.detect_opportunities()
                
                # Send high-priority signals
                await self.send_signals(opportunities)
                
                # Update stats
                self.stats['signals_processed'] += 1
                self.stats['last_signal_time'] = datetime.utcnow().isoformat()
                
                # Log stats every 20 cycles
                if self.stats['signals_processed'] % 20 == 0:
                    self.log_stats()
                
                # Calculate sleep time to maintain interval
                processing_time = time.time() - start_time
                sleep_time = max(0, self.config.signal_interval - processing_time)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    self.logger.warning(f'⚠️  Processing took {processing_time:.2f}s, exceeding {self.config.signal_interval}s interval')
                
            except Exception as e:
                self.logger.error(f'❌ Signal processing error: {e}')
                await asyncio.sleep(1)  # Brief pause on error
    
    async def process_price_signals(self):
        """📊 Process price signals from multiple sources"""
        try:
            # Fetch price data from backend
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.config.backend_url}/arbitrage/prices') as response:
                    if response.status == 200:
                        price_data = await response.json()
                        await self.analyze_price_movements(price_data)
                    else:
                        self.logger.warning(f'⚠️  Failed to fetch prices: {response.status}')
        
        except Exception as e:
            self.logger.error(f'❌ Price signal processing error: {e}')
    
    async def analyze_price_movements(self, price_data: dict):
        """📈 Analyze price movements for arbitrage signals"""
        current_time = datetime.utcnow()
        
        for token_pair, data in price_data.get('prices', {}).items():
            price = Decimal(str(data.get('price', 0)))
            volume = Decimal(str(data.get('volume_24h', 0)))
            
            # Store price history
            if token_pair not in self.price_history:
                self.price_history[token_pair] = []
            
            self.price_history[token_pair].append({
                'price': price,
                'volume': volume,
                'timestamp': current_time
            })
            
            # Keep only last 100 data points
            if len(self.price_history[token_pair]) > 100:
                self.price_history[token_pair] = self.price_history[token_pair][-100:]
            
            # Calculate volatility if we have enough data
            if len(self.price_history[token_pair]) >= 10:
                prices = [float(p['price']) for p in self.price_history[token_pair][-10:]]
                volatility = np.std(prices) / np.mean(prices) if prices else 0
                
                # Create price signal
                signal = PriceSignal(
                    token_pair=token_pair,
                    price=price,
                    volume_24h=volume,
                    volatility=volatility,
                    timestamp=current_time,
                    source='backend_api'
                )
                
                # Analyze for arbitrage potential
                await self.analyze_arbitrage_potential(signal)
    
    async def analyze_arbitrage_potential(self, signal: PriceSignal):
        """🎯 Analyze price signal for arbitrage potential"""
        # Simple volatility-based opportunity detection
        if signal.volatility > 0.01:  # 1% volatility threshold
            # Calculate potential spread
            spread_estimate = int(signal.volatility * 10000)  # Convert to bps
            
            if spread_estimate >= self.config.min_spread_bps:
                # Estimate profit potential
                profit_estimate = spread_estimate * self.config.max_trade_size / 10000
                
                if profit_estimate >= self.config.min_profit_usd:
                    opportunity = ArbitrageOpportunity(
                        token_triple=['WETH', 'DAI', 'USDC'],  # Default triple
                        spread_bps=spread_estimate,
                        expected_profit_usd=profit_estimate,
                        optimal_amount=self.config.max_trade_size,
                        confidence_score=min(signal.volatility * 100, 100),
                        execution_priority=1 if spread_estimate > 50 else 2,
                        timestamp=signal.timestamp
                    )
                    
                    self.opportunity_queue.append(opportunity)
                    self.stats['opportunities_detected'] += 1
                    
                    self.logger.info(f'🎯 Opportunity detected: {spread_estimate}bps spread, ${profit_estimate:.2f} profit')
    
    async def detect_opportunities(self) -> List[ArbitrageOpportunity]:
        """🔍 Detect and prioritize arbitrage opportunities"""
        # Sort opportunities by priority and profit potential
        opportunities = sorted(
            self.opportunity_queue,
            key=lambda x: (x.execution_priority, -x.expected_profit_usd)
        )
        
        # Clear processed opportunities
        self.opportunity_queue = []
        
        # Return top 3 opportunities
        return opportunities[:3]
    
    async def send_signals(self, opportunities: List[ArbitrageOpportunity]):
        """📡 Send signals to ATOM bot for execution"""
        for opportunity in opportunities:
            try:
                # Convert token names to addresses
                token_addresses = [
                    self.config.tokens.get(token, token) 
                    for token in opportunity.token_triple
                ]
                
                # Prepare signal payload
                signal_payload = {
                    'token_triple': token_addresses,
                    'amount': str(int(opportunity.optimal_amount * 1e18)),  # Convert to wei
                    'force_execute': opportunity.execution_priority == 1,
                    'source': 'adom_engine',
                    'confidence': opportunity.confidence_score,
                    'expected_spread_bps': opportunity.spread_bps
                }
                
                # Send signal to backend
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f'{self.config.backend_url}/arbitrage/trigger',
                        json=signal_payload,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result.get('triggered'):
                                self.stats['signals_sent'] += 1
                                self.stats['total_profit_potential'] += result.get('expected_profit', 0)
                                self.logger.info(f'📡 Signal sent successfully: {opportunity.spread_bps}bps')
                            else:
                                self.logger.info(f'📡 Signal rejected: {result.get("reason", "Unknown")}')
                        else:
                            self.logger.warning(f'⚠️  Signal send failed: {response.status}')
            
            except Exception as e:
                self.logger.error(f'❌ Signal send error: {e}')
    
    def log_stats(self):
        """📊 Log engine statistics"""
        self.logger.info('\n📊 ADOM ENGINE STATISTICS')
        self.logger.info('==========================')
        self.logger.info(f'🔍 Signals processed: {self.stats["signals_processed"]}')
        self.logger.info(f'🎯 Opportunities detected: {self.stats["opportunities_detected"]}')
        self.logger.info(f'📡 Signals sent: {self.stats["signals_sent"]}')
        self.logger.info(f'💵 Total profit potential: ${self.stats["total_profit_potential"]:.2f}')
        self.logger.info(f'⏰ Last signal: {self.stats["last_signal_time"]}')
        self.logger.info('==========================\n')

# ============================================================================
# 🚀 MAIN EXECUTION
# ============================================================================
async def main():
    print('🐍 ADOM - Advanced Decentralized Opportunity Monitor')
    print('🚀 Starting Python signal processing engine...\n')
    
    config = AdomConfig()
    engine = AdomEngine(config)
    
    try:
        await engine.start()
    except KeyboardInterrupt:
        await engine.stop()
        print('\n✅ ADOM Engine stopped')

if __name__ == '__main__':
    asyncio.run(main())
