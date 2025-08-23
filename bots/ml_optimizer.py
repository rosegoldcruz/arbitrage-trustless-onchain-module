#!/usr/bin/env python3
"""
Machine Learning Trade Optimizer
Simple ML system to learn from successful/failed trades and improve strategy
"""

import asyncio
import json
import logging
import os
import pickle
import time
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import numpy as np
from collections import deque
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error

logger = logging.getLogger(__name__)

class MLTradeOptimizer:
    def __init__(self):
        self.load_config()
        self.trade_history = deque(maxlen=10000)  # Store last 10k trades
        self.feature_scaler = StandardScaler()
        self.success_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.profit_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_trained = False
        self.last_training_time = 0
        self.training_interval = 3600  # Retrain every hour
        self.min_trades_for_training = 50
        
    def load_config(self):
        """Load ML configuration"""
        self.enable_ml = os.getenv('ENABLE_ML_OPTIMIZATION', 'true').lower() == 'true'
        self.model_save_path = os.getenv('ML_MODEL_PATH', 'models/')
        self.confidence_threshold = float(os.getenv('ML_CONFIDENCE_THRESHOLD', '0.7'))
        
        # Create model directory
        os.makedirs(self.model_save_path, exist_ok=True)
        
        # Try to load existing models
        self.load_models()
        
    def add_trade_result(self, trade_data: Dict):
        """Add trade result to training data"""
        try:
            # Extract features and outcome
            features = self._extract_features(trade_data)
            outcome = {
                'success': trade_data.get('success', False),
                'profit_usd': float(trade_data.get('net_profit_usd', 0)),
                'gas_cost_usd': float(trade_data.get('gas_cost_usd', 0)),
                'execution_time': trade_data.get('execution_time', 0),
                'timestamp': time.time()
            }
            
            trade_record = {
                'features': features,
                'outcome': outcome,
                'raw_data': trade_data
            }
            
            self.trade_history.append(trade_record)
            
            # Check if we should retrain
            if (len(self.trade_history) >= self.min_trades_for_training and
                time.time() - self.last_training_time > self.training_interval):
                asyncio.create_task(self.retrain_models())
                
        except Exception as e:
            logger.error(f"Error adding trade result: {e}")
            
    def _extract_features(self, trade_data: Dict) -> List[float]:
        """Extract numerical features from trade data"""
        try:
            opportunity = trade_data.get('opportunity', {})
            
            features = [
                # Profit-related features
                float(opportunity.get('profit_bps', 0)),
                float(opportunity.get('expected_profit_usd', 0)),
                
                # Market condition features
                float(trade_data.get('gas_price_gwei', 50)),
                float(opportunity.get('liquidity_usd', 0)),
                
                # DEX and token features (encoded)
                self._encode_dex(opportunity.get('dex_a', 'unknown')),
                self._encode_dex(opportunity.get('dex_b', 'unknown')),
                self._encode_dex(opportunity.get('dex_c', 'unknown')),
                
                # Token pair features (encoded)
                self._encode_token_pair(
                    opportunity.get('token_a_name', ''),
                    opportunity.get('token_b_name', ''),
                    opportunity.get('token_c_name', '')
                ),
                
                # Timing features
                float(trade_data.get('opportunity_age_seconds', 0)),
                float(time.time() % 86400),  # Time of day in seconds
                float(time.time() % 604800),  # Day of week in seconds
                
                # Network features
                float(trade_data.get('network_congestion_score', 0.5)),
                float(trade_data.get('volatility_score', 0.5)),
                
                # Trade size features
                float(opportunity.get('amount_in', 0)) / 1e18,  # Convert from wei
                
                # Historical success rate for this pattern
                self._get_pattern_success_rate(opportunity),
            ]
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return [0.0] * 15  # Return default features
            
    def _encode_dex(self, dex_name: str) -> float:
        """Encode DEX name as numerical value"""
        dex_mapping = {
            'uniswap_v3': 1.0,
            'quickswap': 2.0,
            'sushiswap': 3.0,
            'balancer': 4.0,
            'unknown': 0.0
        }
        return dex_mapping.get(dex_name.lower(), 0.0)
        
    def _encode_token_pair(self, token_a: str, token_b: str, token_c: str) -> float:
        """Encode token combination as numerical value"""
        # Simple hash-based encoding
        token_string = f"{token_a}-{token_b}-{token_c}".lower()
        return float(hash(token_string) % 1000) / 1000.0
        
    def _get_pattern_success_rate(self, opportunity: Dict) -> float:
        """Get historical success rate for similar opportunities"""
        try:
            if len(self.trade_history) < 10:
                return 0.5  # Default
                
            # Find similar trades
            similar_trades = []
            target_dex_a = opportunity.get('dex_a', '')
            target_dex_b = opportunity.get('dex_b', '')
            target_profit_bps = float(opportunity.get('profit_bps', 0))
            
            for trade in self.trade_history:
                trade_opp = trade['raw_data'].get('opportunity', {})
                if (trade_opp.get('dex_a') == target_dex_a and
                    trade_opp.get('dex_b') == target_dex_b and
                    abs(float(trade_opp.get('profit_bps', 0)) - target_profit_bps) < 10):
                    similar_trades.append(trade)
                    
            if not similar_trades:
                return 0.5
                
            success_count = sum(1 for t in similar_trades if t['outcome']['success'])
            return success_count / len(similar_trades)
            
        except Exception as e:
            logger.error(f"Error calculating pattern success rate: {e}")
            return 0.5
            
    async def retrain_models(self):
        """Retrain ML models with latest data"""
        try:
            if len(self.trade_history) < self.min_trades_for_training:
                logger.info(f"Not enough trades for training: {len(self.trade_history)}")
                return
                
            logger.info(f"Retraining ML models with {len(self.trade_history)} trades...")
            
            # Prepare training data
            X = []
            y_success = []
            y_profit = []
            
            for trade in self.trade_history:
                X.append(trade['features'])
                y_success.append(1 if trade['outcome']['success'] else 0)
                y_profit.append(trade['outcome']['profit_usd'])
                
            X = np.array(X)
            y_success = np.array(y_success)
            y_profit = np.array(y_profit)
            
            # Scale features
            X_scaled = self.feature_scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_success_train, y_success_test, y_profit_train, y_profit_test = train_test_split(
                X_scaled, y_success, y_profit, test_size=0.2, random_state=42
            )
            
            # Train success classifier
            self.success_classifier.fit(X_train, y_success_train)
            success_accuracy = accuracy_score(y_success_test, self.success_classifier.predict(X_test))
            
            # Train profit regressor (only on successful trades)
            successful_indices = y_profit_train > 0
            if np.sum(successful_indices) > 10:
                self.profit_regressor.fit(X_train[successful_indices], y_profit_train[successful_indices])
                
                # Test profit prediction
                test_successful_indices = y_profit_test > 0
                if np.sum(test_successful_indices) > 0:
                    profit_mse = mean_squared_error(
                        y_profit_test[test_successful_indices],
                        self.profit_regressor.predict(X_test[test_successful_indices])
                    )
                else:
                    profit_mse = 0
            else:
                profit_mse = 0
                
            self.model_trained = True
            self.last_training_time = time.time()
            
            logger.info(f"Models retrained - Success accuracy: {success_accuracy:.3f}, "
                       f"Profit MSE: {profit_mse:.3f}")
            
            # Save models
            self.save_models()
            
        except Exception as e:
            logger.error(f"Error retraining models: {e}")
            
    def predict_trade_success(self, opportunity: Dict, trade_context: Dict) -> Tuple[float, float]:
        """
        Predict trade success probability and expected profit
        Returns (success_probability, expected_profit)
        """
        try:
            if not self.model_trained:
                return 0.5, 0.0  # Default predictions
                
            # Create trade data for feature extraction
            trade_data = {
                'opportunity': opportunity,
                **trade_context
            }
            
            features = self._extract_features(trade_data)
            features_scaled = self.feature_scaler.transform([features])
            
            # Predict success probability
            success_prob = self.success_classifier.predict_proba(features_scaled)[0][1]
            
            # Predict expected profit (if successful)
            expected_profit = 0.0
            if success_prob > 0.3:  # Only predict profit if reasonable success chance
                try:
                    expected_profit = max(0.0, self.profit_regressor.predict(features_scaled)[0])
                except:
                    expected_profit = 0.0
                    
            return float(success_prob), float(expected_profit)
            
        except Exception as e:
            logger.error(f"Error predicting trade success: {e}")
            return 0.5, 0.0
            
    def should_execute_trade(self, opportunity: Dict, trade_context: Dict) -> Tuple[bool, str]:
        """
        Determine if trade should be executed based on ML predictions
        Returns (should_execute, reason)
        """
        try:
            if not self.enable_ml or not self.model_trained:
                return True, "ML not enabled or not trained"
                
            success_prob, expected_profit = self.predict_trade_success(opportunity, trade_context)
            
            # Decision logic
            if success_prob < 0.3:
                return False, f"Low success probability: {success_prob:.2f}"
                
            if expected_profit < 1.0:  # Less than $1 expected profit
                return False, f"Low expected profit: ${expected_profit:.2f}"
                
            # Check if profit justifies risk
            gas_cost = float(trade_context.get('gas_cost_usd', 5.0))
            risk_adjusted_profit = expected_profit - gas_cost
            
            if risk_adjusted_profit < 0.5:
                return False, f"Risk-adjusted profit too low: ${risk_adjusted_profit:.2f}"
                
            return True, f"ML approved: {success_prob:.2f} success prob, ${expected_profit:.2f} expected profit"
            
        except Exception as e:
            logger.error(f"Error in trade decision: {e}")
            return True, "Error in ML prediction, defaulting to execute"
            
    def get_optimization_suggestions(self) -> Dict:
        """Get suggestions for optimizing trading parameters"""
        try:
            if not self.model_trained or len(self.trade_history) < 20:
                return {'suggestions': [], 'confidence': 'low'}
                
            suggestions = []
            
            # Analyze successful vs failed trades
            successful_trades = [t for t in self.trade_history if t['outcome']['success']]
            failed_trades = [t for t in self.trade_history if not t['outcome']['success']]
            
            if len(successful_trades) > 5 and len(failed_trades) > 5:
                # Analyze profit thresholds
                successful_profits = [t['raw_data']['opportunity']['profit_bps'] 
                                    for t in successful_trades]
                failed_profits = [t['raw_data']['opportunity']['profit_bps'] 
                                for t in failed_trades]
                
                avg_successful_profit = np.mean(successful_profits)
                avg_failed_profit = np.mean(failed_profits)
                
                if avg_successful_profit > avg_failed_profit * 1.2:
                    suggestions.append({
                        'parameter': 'min_profit_threshold',
                        'current_avg_successful': avg_successful_profit,
                        'current_avg_failed': avg_failed_profit,
                        'suggestion': f'Consider increasing minimum profit threshold to {avg_successful_profit * 0.8:.0f} bps'
                    })
                    
                # Analyze gas price impact
                successful_gas = [t['outcome']['gas_cost_usd'] for t in successful_trades]
                failed_gas = [t['outcome']['gas_cost_usd'] for t in failed_trades]
                
                if np.mean(failed_gas) > np.mean(successful_gas) * 1.5:
                    suggestions.append({
                        'parameter': 'max_gas_price',
                        'suggestion': f'Consider lowering max gas price - failed trades use {np.mean(failed_gas):.2f} avg gas vs {np.mean(successful_gas):.2f} for successful'
                    })
                    
            return {
                'suggestions': suggestions,
                'confidence': 'high' if len(self.trade_history) > 100 else 'medium',
                'total_trades_analyzed': len(self.trade_history),
                'success_rate': len(successful_trades) / len(self.trade_history) if self.trade_history else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating optimization suggestions: {e}")
            return {'suggestions': [], 'confidence': 'low', 'error': str(e)}
            
    def save_models(self):
        """Save trained models to disk"""
        try:
            if self.model_trained:
                with open(f"{self.model_save_path}/success_classifier.pkl", 'wb') as f:
                    pickle.dump(self.success_classifier, f)
                    
                with open(f"{self.model_save_path}/profit_regressor.pkl", 'wb') as f:
                    pickle.dump(self.profit_regressor, f)
                    
                with open(f"{self.model_save_path}/feature_scaler.pkl", 'wb') as f:
                    pickle.dump(self.feature_scaler, f)
                    
                logger.info("ML models saved successfully")
                
        except Exception as e:
            logger.error(f"Error saving models: {e}")
            
    def load_models(self):
        """Load trained models from disk"""
        try:
            success_path = f"{self.model_save_path}/success_classifier.pkl"
            profit_path = f"{self.model_save_path}/profit_regressor.pkl"
            scaler_path = f"{self.model_save_path}/feature_scaler.pkl"
            
            if (os.path.exists(success_path) and 
                os.path.exists(profit_path) and 
                os.path.exists(scaler_path)):
                
                with open(success_path, 'rb') as f:
                    self.success_classifier = pickle.load(f)
                    
                with open(profit_path, 'rb') as f:
                    self.profit_regressor = pickle.load(f)
                    
                with open(scaler_path, 'rb') as f:
                    self.feature_scaler = pickle.load(f)
                    
                self.model_trained = True
                logger.info("ML models loaded successfully")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.model_trained = False
            
    def get_ml_stats(self) -> Dict:
        """Get ML system statistics"""
        return {
            'enabled': self.enable_ml,
            'model_trained': self.model_trained,
            'total_trades': len(self.trade_history),
            'last_training_time': self.last_training_time,
            'next_training_in': max(0, self.training_interval - (time.time() - self.last_training_time)),
            'confidence_threshold': self.confidence_threshold
        }
