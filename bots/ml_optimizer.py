#!/usr/bin/env python3
"""
ML Trade Optimizer
- Learns from executed trades
- Predicts success probability + expected profit
- Suggests strategy adjustments
"""

import os
import time
import pickle
import logging
from collections import deque
from decimal import Decimal
from typing import Dict, List, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error

from config.secure_config import SecureConfig

logger = logging.getLogger("ml_optimizer")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()


class MLTradeOptimizer:
    def __init__(self):
        self.enable_ml = _cfg.env.get("ENABLE_ML_OPTIMIZATION", "true").lower() == "true"
        self.model_path = _cfg.env.get("ML_MODEL_PATH", "/srv/atom/models")
        self.conf_thresh = float(_cfg.env.get("ML_CONFIDENCE_THRESHOLD", "0.7"))

        os.makedirs(self.model_path, exist_ok=True)

        self.trade_history = deque(maxlen=10000)
        self.scaler = StandardScaler()
        self.success_clf = RandomForestClassifier(n_estimators=100, random_state=42)
        self.profit_reg = RandomForestRegressor(n_estimators=100, random_state=42)

        self.trained = False
        self.last_train = 0
        self.train_interval = 3600
        self.min_trades = 50

        self._load_models()

    # --------------------------------------------------------------------------
    # Data ingest
    # --------------------------------------------------------------------------
    def add_trade_result(self, trade: Dict):
        try:
            features = self._extract_features(trade)
            outcome = {
                "success": trade.get("success", False),
                "profit_usd": float(trade.get("net_profit_usd", 0)),
                "gas_cost_usd": float(trade.get("gas_cost_usd", 0)),
                "execution_time": trade.get("execution_time", 0),
                "timestamp": time.time(),
            }
            self.trade_history.append({"features": features, "outcome": outcome, "raw": trade})

            if len(self.trade_history) >= self.min_trades and time.time() - self.last_train > self.train_interval:
                self._retrain()
        except Exception as e:
            logger.error(f"Trade result add failed: {e}")

    # --------------------------------------------------------------------------
    # Training
    # --------------------------------------------------------------------------
    def _retrain(self):
        try:
            X = np.array([t["features"] for t in self.trade_history])
            y_success = np.array([1 if t["outcome"]["success"] else 0 for t in self.trade_history])
            y_profit = np.array([t["outcome"]["profit_usd"] for t in self.trade_history])

            X_scaled = self.scaler.fit_transform(X)

            X_train, X_test, y_s_train, y_s_test, y_p_train, y_p_test = train_test_split(
                X_scaled, y_success, y_profit, test_size=0.2, random_state=42
            )

            self.success_clf.fit(X_train, y_s_train)
            acc = accuracy_score(y_s_test, self.success_clf.predict(X_test))

            successful = y_p_train > 0
            if np.sum(successful) > 10:
                self.profit_reg.fit(X_train[successful], y_p_train[successful])

            self.trained = True
            self.last_train = time.time()
            self._save_models()
            logger.info(f"ML retrain OK | success acc={acc:.3f}")
        except Exception as e:
            logger.error(f"Retrain failed: {e}")

    # --------------------------------------------------------------------------
    # Prediction
    # --------------------------------------------------------------------------
    def predict(self, opportunity: Dict, ctx: Dict) -> Tuple[float, float]:
        if not self.trained:
            return 0.5, 0.0
        try:
            features = self._extract_features({**ctx, "opportunity": opportunity})
            scaled = self.scaler.transform([features])
            prob = self.success_clf.predict_proba(scaled)[0][1]
            profit = float(self.profit_reg.predict(scaled)[0]) if prob > 0.3 else 0.0
            return float(prob), profit
        except Exception as e:
            logger.error(f"Predict failed: {e}")
            return 0.5, 0.0

    def should_execute(self, opportunity: Dict, ctx: Dict) -> Tuple[bool, str]:
        if not self.enable_ml or not self.trained:
            return True, "ML disabled or not trained"
        prob, profit = self.predict(opportunity, ctx)
        if prob < 0.3:
            return False, f"Low success probability {prob:.2f}"
        if profit < 1.0:
            return False, f"Low expected profit ${profit:.2f}"
        gas_cost = float(ctx.get("gas_cost_usd", 5.0))
        if profit - gas_cost < 0.5:
            return False, f"Risk-adjusted profit too low: ${profit - gas_cost:.2f}"
        return True, f"Approved {prob:.2f} prob, ${profit:.2f} profit"

    # --------------------------------------------------------------------------
    # Models
    # --------------------------------------------------------------------------
    def _save_models(self):
        try:
            with open(f"{self.model_path}/success.pkl", "wb") as f:
                pickle.dump(self.success_clf, f)
            with open(f"{self.model_path}/profit.pkl", "wb") as f:
                pickle.dump(self.profit_reg, f)
            with open(f"{self.model_path}/scaler.pkl", "wb") as f:
                pickle.dump(self.scaler, f)
        except Exception as e:
            logger.error(f"Save models failed: {e}")

    def _load_models(self):
        try:
            success_path = f"{self.model_path}/success.pkl"
            profit_path = f"{self.model_path}/profit.pkl"
            scaler_path = f"{self.model_path}/scaler.pkl"
            if all(os.path.exists(p) for p in [success_path, profit_path, scaler_path]):
                with open(success_path, "rb") as f:
                    self.success_clf = pickle.load(f)
                with open(profit_path, "rb") as f:
                    self.profit_reg = pickle.load(f)
                with open(scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
                self.trained = True
        except Exception as e:
            logger.error(f"Load models failed: {e}")

    def stats(self) -> Dict:
        return {
            "enabled": self.enable_ml,
            "trained": self.trained,
            "trade_count": len(self.trade_history),
            "last_train": self.last_train,
            "confidence_threshold": self.conf_thresh,
        }

    # --------------------------------------------------------------------------
    # Feature extraction
    # --------------------------------------------------------------------------
    def _extract_features(self, trade: Dict) -> List[float]:
        opp = trade.get("opportunity", {})
        return [
            float(opp.get("profit_bps", 0)),
            float(opp.get("expected_profit_usd", 0)),
            float(trade.get("gas_price_gwei", 50)),
            float(opp.get("liquidity_usd", 0)),
            len(str(opp.get("dex_a", ""))),
            len(str(opp.get("dex_b", ""))),
            len(str(opp.get("dex_c", ""))),
            float(opp.get("amount_in", 0)) / 1e18,
            float(trade.get("opportunity_age_seconds", 0)),
            float(time.time() % 86400),
            float(time.time() % 604800),
        ]
