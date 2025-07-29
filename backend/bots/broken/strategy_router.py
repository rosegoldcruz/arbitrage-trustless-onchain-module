# strategy_router.py
class StrategyRouter:
    """Routes arbitrage opportunities to optimal execution strategy"""
    
    STRATEGIES = ["ADOM", "ATOM", "ARCHANGEL"]
    
    def route_strategy(self, profit: float, risk_score: float, mev_vuln: float) -> str:
        """Select best execution strategy based on conditions"""
        # High MEV vulnerability requires protected strategies
        if mev_vuln > 0.7:
            return "ADOM"  # Flashloan arb with MEV protection
        
        # High profit opportunities justify complex strategies
        if profit > 0.05:  # >5%
            return "ARCHANGEL"  # Sandwich strategy
            
        # Default atomic arb
        return "ATOM"