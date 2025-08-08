"""
🎯 Strategy Router
Intelligent routing of arbitrage opportunities to optimal execution strategies
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BotStrategy(Enum):
    """Available bot strategies"""
    ATOM = "ATOM"
    ADOM = "ADOM"
    ARCHANGEL = "ARCHANGEL"

@dataclass
class RoutingSignal:
    """Signal for strategy routing"""
    profit_usd: float
    risk_score: float
    mev_vulnerability: float
    gas_cost_usd: float
    trade_size_usd: float
    time_sensitivity: float
    complexity_score: float

@dataclass
class RoutingDecision:
    """Routing decision result"""
    selected_bot: BotStrategy
    confidence: float
    reasoning: str
    fallback_bot: Optional[BotStrategy] = None

class StrategyRouter:
    """Routes arbitrage opportunities to optimal execution strategy"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.routing_history = []

        # Thresholds
        self.high_profit_threshold = self.config.get('high_profit_threshold', 100.0)  # $100
        self.high_mev_threshold = self.config.get('high_mev_threshold', 0.7)
        self.flash_loan_threshold = self.config.get('flash_loan_threshold', 1000.0)  # $1000

    def select_bot(self, signal: RoutingSignal) -> RoutingDecision:
        """Select optimal bot based on signal characteristics"""
        try:
            logger.info(f"🎯 Routing signal: ${signal.profit_usd:.2f} profit, {signal.mev_vulnerability:.2f} MEV risk")

            # High MEV vulnerability requires protected strategies
            if signal.mev_vulnerability > self.high_mev_threshold:
                decision = RoutingDecision(
                    selected_bot=BotStrategy.ADOM,
                    confidence=0.9,
                    reasoning=f"High MEV vulnerability ({signal.mev_vulnerability:.2f}) requires ADOM protection",
                    fallback_bot=BotStrategy.ATOM
                )

            # Large profit opportunities justify flash loan strategies
            elif signal.profit_usd > self.flash_loan_threshold:
                decision = RoutingDecision(
                    selected_bot=BotStrategy.ADOM,
                    confidence=0.8,
                    reasoning=f"Large profit (${signal.profit_usd:.2f}) justifies ADOM flash loan",
                    fallback_bot=BotStrategy.ATOM
                )

            # High gas cost relative to profit favors optimization
            elif signal.gas_cost_usd > signal.profit_usd * 0.5:
                decision = RoutingDecision(
                    selected_bot=BotStrategy.ATOM,
                    confidence=0.8,
                    reasoning=f"High gas cost (${signal.gas_cost_usd:.2f}) relative to profit requires ATOM optimization",
                    fallback_bot=BotStrategy.ADOM
                )

            # Time-sensitive opportunities
            elif signal.time_sensitivity > 0.8:
                decision = RoutingDecision(
                    selected_bot=BotStrategy.ATOM,
                    confidence=0.7,
                    reasoning=f"Time-sensitive opportunity ({signal.time_sensitivity:.2f}) requires fast ATOM execution",
                    fallback_bot=BotStrategy.ADOM
                )

            # Default to ATOM for simple arbitrage
            else:
                decision = RoutingDecision(
                    selected_bot=BotStrategy.ATOM,
                    confidence=0.6,
                    reasoning="Standard arbitrage opportunity routed to ATOM",
                    fallback_bot=BotStrategy.ADOM
                )

            # Record decision
            self.routing_history.append({
                'signal': signal,
                'decision': decision,
                'timestamp': logger.handlers[0].formatter.formatTime(logger.makeRecord('', 0, '', 0, '', (), None)) if logger.handlers else 'unknown'
            })

            logger.info(f"✅ Selected {decision.selected_bot.value}: {decision.reasoning}")
            return decision

        except Exception as e:
            logger.error(f"❌ Routing failed: {e}")
            # Fallback to ATOM
            return RoutingDecision(
                selected_bot=BotStrategy.ATOM,
                confidence=0.1,
                reasoning=f"Routing error, defaulting to ATOM: {str(e)}"
            )

    async def run(self, signal: RoutingSignal) -> Dict[str, Any]:
        """Execute the selected strategy"""
        decision = self.select_bot(signal)

        # This would integrate with the actual bot execution
        # For now, return the routing decision
        return {
            'bot': decision.selected_bot.value,
            'confidence': decision.confidence,
            'reasoning': decision.reasoning,
            'fallback': decision.fallback_bot.value if decision.fallback_bot else None,
            'signal': {
                'profit_usd': signal.profit_usd,
                'risk_score': signal.risk_score,
                'mev_vulnerability': signal.mev_vulnerability
            }
        }

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        if not self.routing_history:
            return {'total_routes': 0}

        bot_counts = {}
        for record in self.routing_history:
            bot = record['decision'].selected_bot.value
            bot_counts[bot] = bot_counts.get(bot, 0) + 1

        return {
            'total_routes': len(self.routing_history),
            'bot_distribution': bot_counts,
            'avg_confidence': sum(r['decision'].confidence for r in self.routing_history) / len(self.routing_history)
        }

# Singleton instance
strategy_router = StrategyRouter()