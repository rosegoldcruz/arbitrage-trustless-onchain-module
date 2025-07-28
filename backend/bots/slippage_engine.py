# slippage_engine.py
import numpy as np

class SlippageSentinel:
    """Predicts and mitigates slippage risk"""
    
    SLIPPAGE_MODELS = {
        'uniswap': lambda size, depth: size**2 / (depth * 1000),
        'curve': lambda size, depth: size / (depth * 10),
        # ... other DEX models ...
    }
    
    def calculate_slippage_buffer(self, path: list, chain: str, immediate=False) -> float:
        """Calculate expected slippage loss for path"""
        total_slippage = 0.0
        for i in range(len(path)-1):
            token_in, token_out = path[i], path[i+1]
            pool = self._get_pool(token_in, token_out, chain)
            model = self.SLIPPAGE_MODELS[pool['dex_type']]
            
            # Get pool depth and trade size estimation
            depth = pool['reserves'][token_in]
            size = self._estimate_trade_size(path, i)
            
            # Apply slippage model
            total_slippage += model(size, depth)
            
        return total_slippage
    
    def calculate_effective_price(self, amount_in: float, pool_state: dict) -> float:
        """Calculate effective output price after slippage"""
        x, y = pool_state['reserves']
        k = x * y
        new_x = x + amount_in
        new_y = k / new_x
        return (y - new_y) / amount_in