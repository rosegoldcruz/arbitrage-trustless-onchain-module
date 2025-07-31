#!/usr/bin/env python3
"""
AEON Network Orchestrator
Cross-ecosystem communication and coordination layer
Enables AEON, ATOM/ADOM, and SPECTRE to work together as antifragile intelligence
"""

import asyncio
import json
import logging
import time
import websockets
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import redis
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EcosystemStatus:
    ecosystem: str
    status: str
    last_heartbeat: float
    performance_metrics: Dict[str, Any]
    current_opportunities: int
    total_executions: int
    success_rate: float
    is_healthy: bool

@dataclass
class CrossEcosystemSignal:
    source_ecosystem: str
    target_ecosystem: str
    signal_type: str
    data: Dict[str, Any]
    timestamp: float
    priority: str

@dataclass
class ConsensusDecision:
    decision_id: str
    opportunity_data: Dict[str, Any]
    ecosystem_votes: Dict[str, str]  # ecosystem -> vote (execute/skip/wait)
    consensus_reached: bool
    final_decision: str
    confidence_score: float
    timestamp: float

class AEONOrchestrator:
    """
    AEON Network Orchestrator
    Coordinates communication between all three ecosystems for antifragile intelligence
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.ecosystem_status: Dict[str, EcosystemStatus] = {}
        self.signal_queue: List[CrossEcosystemSignal] = []
        self.consensus_decisions: List[ConsensusDecision] = []
        
        # Communication channels
        self.redis_client = None
        self.websocket_server = None
        self.db_connection = None
        
        # Ecosystem endpoints
        self.endpoints = {
            'AEON': 'ws://64.23.154.163:8000',      # On-chain autonomous
            'ATOM': 'ws://64.23.154.163:8000',      # Python hybrid bot
            'ADOM': 'ws://64.23.154.163:8000',      # Node.js MEV bot
            'SPECTRE': 'http://64.23.154.163:8000'  # Analytics engine
        }
        
        # Performance tracking
        self.orchestrator_stats = {
            'total_signals_processed': 0,
            'consensus_decisions_made': 0,
            'cross_ecosystem_executions': 0,
            'average_response_time': 0.0,
            'ecosystem_sync_rate': 0.0
        }
        
        logger.info("🔗 AEON Network Orchestrator initialized")
        logger.info(f"Managing {len(self.endpoints)} ecosystems")

    async def start(self):
        """Start the AEON Network Orchestrator"""
        logger.info("🚀 Starting AEON Network Orchestrator...")
        
        try:
            # Initialize communication infrastructure
            await self.initialize_infrastructure()
            
            # Start orchestration tasks
            tasks = [
                self.ecosystem_monitor(),
                self.signal_processor(),
                self.consensus_engine(),
                self.performance_optimizer(),
                self.health_checker(),
                self.data_synchronizer()
            ]
            
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"❌ Orchestrator error: {e}")
            raise
        finally:
            await self.cleanup()

    async def initialize_infrastructure(self):
        """Initialize communication infrastructure"""
        logger.info("🔧 Initializing communication infrastructure...")
        
        try:
            # Initialize Redis for fast inter-ecosystem communication
            import redis.asyncio as redis
            self.redis_client = redis.Redis(
                host=self.config.get('redis_host', 'localhost'),
                port=self.config.get('redis_port', 6379),
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
            
        except Exception as e:
            logger.warning(f"⚠️  Redis not available: {e}")
            self.redis_client = None
        
        # Initialize SQLite for persistent storage
        self.db_connection = sqlite3.connect('aeon_orchestrator.db')
        self.setup_database()
        logger.info("✅ Database initialized")
        
        # Start WebSocket server for real-time communication
        await self.start_websocket_server()

    def setup_database(self):
        """Setup database tables"""
        cursor = self.db_connection.cursor()
        
        # Ecosystem status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ecosystem_status (
                ecosystem TEXT PRIMARY KEY,
                status TEXT,
                last_heartbeat REAL,
                performance_metrics TEXT,
                is_healthy BOOLEAN
            )
        ''')
        
        # Signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cross_ecosystem_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_ecosystem TEXT,
                target_ecosystem TEXT,
                signal_type TEXT,
                data TEXT,
                timestamp REAL,
                priority TEXT,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Consensus decisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consensus_decisions (
                decision_id TEXT PRIMARY KEY,
                opportunity_data TEXT,
                ecosystem_votes TEXT,
                consensus_reached BOOLEAN,
                final_decision TEXT,
                confidence_score REAL,
                timestamp REAL
            )
        ''')
        
        self.db_connection.commit()

    async def start_websocket_server(self):
        """Start WebSocket server for ecosystem communication"""
        async def handle_ecosystem_connection(websocket, path):
            try:
                ecosystem_id = await websocket.recv()
                logger.info(f"🔌 {ecosystem_id} connected")
                
                # Register ecosystem
                await self.register_ecosystem(ecosystem_id, websocket)
                
                # Handle messages
                async for message in websocket:
                    await self.process_ecosystem_message(ecosystem_id, json.loads(message))
                    
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"🔌 {ecosystem_id} disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
        
        # Start server (non-blocking)
        asyncio.create_task(
            websockets.serve(handle_ecosystem_connection, "localhost", 8000)
        )
        logger.info("✅ WebSocket server started on ws://localhost:8000")

    async def register_ecosystem(self, ecosystem_id: str, websocket):
        """Register an ecosystem connection"""
        self.ecosystem_status[ecosystem_id] = EcosystemStatus(
            ecosystem=ecosystem_id,
            status='connected',
            last_heartbeat=time.time(),
            performance_metrics={},
            current_opportunities=0,
            total_executions=0,
            success_rate=0.0,
            is_healthy=True
        )
        
        # Store in database
        cursor = self.db_connection.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO ecosystem_status 
            (ecosystem, status, last_heartbeat, performance_metrics, is_healthy)
            VALUES (?, ?, ?, ?, ?)
        ''', (ecosystem_id, 'connected', time.time(), '{}', True))
        self.db_connection.commit()

    async def ecosystem_monitor(self):
        """Monitor all ecosystem health and performance"""
        logger.info("👁️  Starting ecosystem monitor...")
        
        while True:
            try:
                current_time = time.time()
                
                for ecosystem_id, status in self.ecosystem_status.items():
                    # Check heartbeat
                    if current_time - status.last_heartbeat > 60:  # 1 minute timeout
                        status.status = 'disconnected'
                        status.is_healthy = False
                        logger.warning(f"⚠️  {ecosystem_id} heartbeat timeout")
                    
                    # Request status update
                    await self.request_ecosystem_status(ecosystem_id)
                
                # Log overall network health
                healthy_ecosystems = sum(1 for s in self.ecosystem_status.values() if s.is_healthy)
                total_ecosystems = len(self.ecosystem_status)
                
                if healthy_ecosystems < total_ecosystems:
                    logger.warning(f"🏥 Network health: {healthy_ecosystems}/{total_ecosystems} ecosystems healthy")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Ecosystem monitor error: {e}")
                await asyncio.sleep(30)

    async def request_ecosystem_status(self, ecosystem_id: str):
        """Request status update from ecosystem"""
        if self.redis_client:
            try:
                await self.redis_client.publish(f"{ecosystem_id}:commands", json.dumps({
                    'command': 'status_request',
                    'timestamp': time.time()
                }))
            except Exception as e:
                logger.error(f"Error requesting status from {ecosystem_id}: {e}")

    async def signal_processor(self):
        """Process cross-ecosystem signals"""
        logger.info("📡 Starting signal processor...")
        
        while True:
            try:
                if self.signal_queue:
                    signal = self.signal_queue.pop(0)
                    await self.process_signal(signal)
                    self.orchestrator_stats['total_signals_processed'] += 1
                
                # Also process signals from Redis
                if self.redis_client:
                    await self.process_redis_signals()
                
                await asyncio.sleep(0.1)  # High-frequency processing
                
            except Exception as e:
                logger.error(f"Signal processor error: {e}")
                await asyncio.sleep(1)

    async def process_signal(self, signal: CrossEcosystemSignal):
        """Process a cross-ecosystem signal"""
        logger.info(f"📨 Processing signal: {signal.source_ecosystem} → {signal.target_ecosystem} ({signal.signal_type})")
        
        try:
            if signal.signal_type == 'opportunity_detected':
                await self.handle_opportunity_signal(signal)
            elif signal.signal_type == 'execution_result':
                await self.handle_execution_result(signal)
            elif signal.signal_type == 'performance_update':
                await self.handle_performance_update(signal)
            elif signal.signal_type == 'consensus_request':
                await self.handle_consensus_request(signal)
            else:
                logger.warning(f"Unknown signal type: {signal.signal_type}")
        
        except Exception as e:
            logger.error(f"Error processing signal: {e}")

    async def handle_opportunity_signal(self, signal: CrossEcosystemSignal):
        """Handle opportunity detection signal"""
        opportunity_data = signal.data
        
        # Broadcast to all other ecosystems for validation
        for ecosystem_id in self.ecosystem_status.keys():
            if ecosystem_id != signal.source_ecosystem:
                validation_signal = CrossEcosystemSignal(
                    source_ecosystem='ORCHESTRATOR',
                    target_ecosystem=ecosystem_id,
                    signal_type='validate_opportunity',
                    data=opportunity_data,
                    timestamp=time.time(),
                    priority='high'
                )
                await self.send_signal_to_ecosystem(ecosystem_id, validation_signal)

    async def consensus_engine(self):
        """Run consensus engine for cross-ecosystem decisions"""
        logger.info("🤝 Starting consensus engine...")
        
        while True:
            try:
                # Check for pending consensus decisions
                pending_decisions = [d for d in self.consensus_decisions if not d.consensus_reached]
                
                for decision in pending_decisions:
                    await self.evaluate_consensus(decision)
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Consensus engine error: {e}")
                await asyncio.sleep(5)

    async def evaluate_consensus(self, decision: ConsensusDecision):
        """Evaluate if consensus has been reached"""
        total_ecosystems = len(self.ecosystem_status)
        votes_received = len(decision.ecosystem_votes)
        
        # Require majority vote
        if votes_received >= (total_ecosystems // 2) + 1:
            # Count votes
            execute_votes = sum(1 for vote in decision.ecosystem_votes.values() if vote == 'execute')
            skip_votes = sum(1 for vote in decision.ecosystem_votes.values() if vote == 'skip')
            
            if execute_votes > skip_votes:
                decision.final_decision = 'execute'
                decision.confidence_score = execute_votes / votes_received
            else:
                decision.final_decision = 'skip'
                decision.confidence_score = skip_votes / votes_received
            
            decision.consensus_reached = True
            
            logger.info(f"✅ Consensus reached: {decision.final_decision} (confidence: {decision.confidence_score:.2f})")
            
            # Execute decision
            await self.execute_consensus_decision(decision)

    async def execute_consensus_decision(self, decision: ConsensusDecision):
        """Execute a consensus decision"""
        if decision.final_decision == 'execute':
            # Find best ecosystem to execute
            best_ecosystem = self.select_optimal_executor(decision.opportunity_data)
            
            execution_signal = CrossEcosystemSignal(
                source_ecosystem='ORCHESTRATOR',
                target_ecosystem=best_ecosystem,
                signal_type='execute_opportunity',
                data=decision.opportunity_data,
                timestamp=time.time(),
                priority='critical'
            )
            
            await self.send_signal_to_ecosystem(best_ecosystem, execution_signal)
            self.orchestrator_stats['cross_ecosystem_executions'] += 1

    def select_optimal_executor(self, opportunity_data: Dict) -> str:
        """Select the optimal ecosystem to execute an opportunity"""
        # Score ecosystems based on performance and suitability
        scores = {}
        
        for ecosystem_id, status in self.ecosystem_status.items():
            if not status.is_healthy:
                continue
            
            score = 0
            
            # Base scores by ecosystem type
            if ecosystem_id == 'AEON':
                score += 10  # Autonomous, reliable
            elif ecosystem_id == 'ATOM':
                score += 15  # Flexible, fast
            elif ecosystem_id == 'ADOM':
                score += 20  # MEV optimized
            
            # Performance bonus
            score += status.success_rate * 10
            
            # Current load penalty
            score -= status.current_opportunities * 2
            
            scores[ecosystem_id] = score
        
        # Return highest scoring ecosystem
        return max(scores.items(), key=lambda x: x[1])[0] if scores else 'AEON'

    async def send_signal_to_ecosystem(self, ecosystem_id: str, signal: CrossEcosystemSignal):
        """Send signal to specific ecosystem"""
        if self.redis_client:
            try:
                await self.redis_client.publish(
                    f"{ecosystem_id}:signals",
                    json.dumps(asdict(signal), default=str)
                )
            except Exception as e:
                logger.error(f"Error sending signal to {ecosystem_id}: {e}")

    async def performance_optimizer(self):
        """Optimize cross-ecosystem performance"""
        logger.info("⚡ Starting performance optimizer...")
        
        while True:
            try:
                # Analyze ecosystem performance
                performance_data = await self.analyze_ecosystem_performance()
                
                # Generate optimization recommendations
                recommendations = await self.generate_optimization_recommendations(performance_data)
                
                # Apply optimizations
                for ecosystem_id, recommendations_list in recommendations.items():
                    await self.apply_optimizations(ecosystem_id, recommendations_list)
                
                await asyncio.sleep(300)  # Optimize every 5 minutes
                
            except Exception as e:
                logger.error(f"Performance optimizer error: {e}")
                await asyncio.sleep(300)

    async def analyze_ecosystem_performance(self) -> Dict:
        """Analyze performance across all ecosystems"""
        performance_data = {}
        
        for ecosystem_id, status in self.ecosystem_status.items():
            performance_data[ecosystem_id] = {
                'success_rate': status.success_rate,
                'total_executions': status.total_executions,
                'current_opportunities': status.current_opportunities,
                'response_time': status.performance_metrics.get('avg_response_time', 0),
                'is_healthy': status.is_healthy
            }
        
        return performance_data

    async def generate_optimization_recommendations(self, performance_data: Dict) -> Dict:
        """Generate optimization recommendations"""
        recommendations = {}
        
        for ecosystem_id, metrics in performance_data.items():
            ecosystem_recommendations = []
            
            # Low success rate
            if metrics['success_rate'] < 0.8:
                ecosystem_recommendations.append('increase_validation_threshold')
            
            # High opportunity backlog
            if metrics['current_opportunities'] > 10:
                ecosystem_recommendations.append('increase_processing_speed')
            
            # Slow response time
            if metrics['response_time'] > 5.0:
                ecosystem_recommendations.append('optimize_execution_path')
            
            recommendations[ecosystem_id] = ecosystem_recommendations
        
        return recommendations

    async def apply_optimizations(self, ecosystem_id: str, recommendations: List[str]):
        """Apply optimizations to ecosystem"""
        for recommendation in recommendations:
            optimization_signal = CrossEcosystemSignal(
                source_ecosystem='ORCHESTRATOR',
                target_ecosystem=ecosystem_id,
                signal_type='optimization_command',
                data={'optimization': recommendation},
                timestamp=time.time(),
                priority='medium'
            )
            
            await self.send_signal_to_ecosystem(ecosystem_id, optimization_signal)

    async def health_checker(self):
        """Monitor overall network health"""
        while True:
            try:
                # Check ecosystem health
                healthy_count = sum(1 for s in self.ecosystem_status.values() if s.is_healthy)
                total_count = len(self.ecosystem_status)
                
                health_percentage = (healthy_count / total_count) * 100 if total_count > 0 else 0
                
                if health_percentage < 75:
                    logger.warning(f"🚨 Network health critical: {health_percentage:.1f}%")
                    await self.trigger_recovery_procedures()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Health checker error: {e}")
                await asyncio.sleep(60)

    async def trigger_recovery_procedures(self):
        """Trigger network recovery procedures"""
        logger.info("🔧 Triggering network recovery procedures...")
        
        # Attempt to restart unhealthy ecosystems
        for ecosystem_id, status in self.ecosystem_status.items():
            if not status.is_healthy:
                recovery_signal = CrossEcosystemSignal(
                    source_ecosystem='ORCHESTRATOR',
                    target_ecosystem=ecosystem_id,
                    signal_type='recovery_command',
                    data={'action': 'restart'},
                    timestamp=time.time(),
                    priority='critical'
                )
                
                await self.send_signal_to_ecosystem(ecosystem_id, recovery_signal)

    async def data_synchronizer(self):
        """Synchronize data across ecosystems"""
        while True:
            try:
                # Sync performance data
                await self.sync_performance_data()
                
                # Sync opportunity data
                await self.sync_opportunity_data()
                
                await asyncio.sleep(60)  # Sync every minute
                
            except Exception as e:
                logger.error(f"Data synchronizer error: {e}")
                await asyncio.sleep(60)

    async def sync_performance_data(self):
        """Synchronize performance data across ecosystems"""
        # Aggregate performance metrics
        total_executions = sum(s.total_executions for s in self.ecosystem_status.values())
        avg_success_rate = sum(s.success_rate for s in self.ecosystem_status.values()) / len(self.ecosystem_status)
        
        sync_data = {
            'network_total_executions': total_executions,
            'network_avg_success_rate': avg_success_rate,
            'timestamp': time.time()
        }
        
        # Broadcast to all ecosystems
        for ecosystem_id in self.ecosystem_status.keys():
            sync_signal = CrossEcosystemSignal(
                source_ecosystem='ORCHESTRATOR',
                target_ecosystem=ecosystem_id,
                signal_type='performance_sync',
                data=sync_data,
                timestamp=time.time(),
                priority='low'
            )
            
            await self.send_signal_to_ecosystem(ecosystem_id, sync_signal)

    async def sync_opportunity_data(self):
        """Synchronize opportunity data across ecosystems"""
        # This would sync opportunity databases, price feeds, etc.
        pass

    async def process_redis_signals(self):
        """Process signals from Redis pub/sub"""
        if not self.redis_client:
            return
        
        try:
            # Check for signals in Redis
            for ecosystem_id in self.ecosystem_status.keys():
                signal_data = await self.redis_client.lpop(f"{ecosystem_id}:outgoing_signals")
                if signal_data:
                    signal = CrossEcosystemSignal(**json.loads(signal_data))
                    self.signal_queue.append(signal)
        except Exception as e:
            logger.error(f"Error processing Redis signals: {e}")

    async def process_ecosystem_message(self, ecosystem_id: str, message: Dict):
        """Process message from ecosystem"""
        message_type = message.get('type')
        
        if message_type == 'heartbeat':
            self.ecosystem_status[ecosystem_id].last_heartbeat = time.time()
            self.ecosystem_status[ecosystem_id].performance_metrics = message.get('metrics', {})
        
        elif message_type == 'opportunity':
            signal = CrossEcosystemSignal(
                source_ecosystem=ecosystem_id,
                target_ecosystem='ALL',
                signal_type='opportunity_detected',
                data=message.get('data', {}),
                timestamp=time.time(),
                priority='high'
            )
            self.signal_queue.append(signal)
        
        elif message_type == 'execution_result':
            # Update ecosystem stats
            if message.get('success'):
                self.ecosystem_status[ecosystem_id].total_executions += 1

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up orchestrator resources...")
        
        if self.redis_client:
            await self.redis_client.close()
        
        if self.db_connection:
            self.db_connection.close()

async def main():
    """Main orchestrator execution"""
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'websocket_port': 8000,
        'log_level': 'INFO'
    }
    
    orchestrator = AEONOrchestrator(config)
    
    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        logger.info("👋 AEON Network Orchestrator shutdown")

if __name__ == "__main__":
    asyncio.run(main())
