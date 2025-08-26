import logging
import threading
import time
from typing import Dict, List, Optional

from web3 import Web3
from prometheus_client import Gauge, Counter
from config.secure_config import SecureConfig

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
logger = logging.getLogger("rpc_manager")
logger.setLevel(logging.INFO)

# ------------------------------------------------------------------------------
# Prometheus Metrics
# ------------------------------------------------------------------------------
rpc_latency_gauge = Gauge("rpc_latency_ms", "RPC latency in ms", ["chain", "provider"])
rpc_failovers_total = Counter("rpc_failovers_total", "RPC failovers", ["chain"])
rpc_current_provider = Gauge("rpc_current_provider", "Active RPC provider (index)", ["chain"])

# ------------------------------------------------------------------------------
# RPC Manager
# ------------------------------------------------------------------------------
class RPCManager:
    def __init__(self):
        self.config = SecureConfig()

        # Define RPC endpoints per chain (primary → backups)
        self.rpc_endpoints: Dict[str, List[str]] = {
            "polygon": [
                self.config.require("POLYGON_RPC_URL"),
                self.config.require("POLYGON_RPC_BACKUP"),
                self.config.require("POLYGON_RPC_BACKUP2"),
            ],
            "ethereum": [self.config.require("ETHEREUM_RPC_URL")],
            "base": [self.config.require("BASE_RPC_URL")],
            "arbitrum": [self.config.require("ARBITRUM_RPC_URL")],
        }

        # Track current provider index per chain
        self.current_provider_idx: Dict[str, int] = {c: 0 for c in self.rpc_endpoints.keys()}

        # Web3 instances per chain
        self.web3_instances: Dict[str, Optional[Web3]] = {
            c: self._make_web3(c, self.rpc_endpoints[c][0]) for c in self.rpc_endpoints.keys()
        }

        # Start health monitor
        self.monitor_thread = threading.Thread(target=self._health_monitor, daemon=True)
        self.monitor_thread.start()

    def _make_web3(self, chain: str, url: str) -> Optional[Web3]:
        try:
            w3 = Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 10}))
            if not w3.is_connected():
                raise Exception("Not connected")
            logger.info(f"✅ Connected to {chain} RPC: {url}")
            return w3
        except Exception as e:
            logger.error(f"❌ Failed to connect to {chain} RPC {url}: {e}")
            return None

    def get_web3(self, chain: str) -> Web3:
        """
        Get current working Web3 instance for a chain.
        Fail-fast if none available.
        """
        w3 = self.web3_instances.get(chain)
        if w3 and w3.is_connected():
            return w3
        else:
            logger.warning(f"⚠️ {chain} RPC unavailable, attempting failover...")
            self._failover(chain)
            w3 = self.web3_instances.get(chain)
            if not w3 or not w3.is_connected():
                logger.critical(f"❌ No working RPC providers for {chain}")
                raise RuntimeError(f"No working RPC providers for {chain}")
            return w3

    def _failover(self, chain: str):
        endpoints = self.rpc_endpoints[chain]
        self.current_provider_idx[chain] = (self.current_provider_idx[chain] + 1) % len(endpoints)
        idx = self.current_provider_idx[chain]
        new_url = endpoints[idx]

        w3 = self._make_web3(chain, new_url)
        if w3 and w3.is_connected():
            self.web3_instances[chain] = w3
            rpc_failovers_total.labels(chain=chain).inc()
            rpc_current_provider.labels(chain=chain).set(idx)
            logger.info(f"🔄 {chain} failover: switched to {new_url}")
        else:
            logger.error(f"❌ {chain} failover failed for {new_url}")

    def _health_monitor(self):
        """
        Periodically ping all RPC providers to measure latency and auto-failover.
        """
        while True:
            for chain, w3 in self.web3_instances.items():
                if not w3:
                    continue
                try:
                    start = time.time()
                    _ = w3.eth.block_number
                    latency = (time.time() - start) * 1000
                    rpc_latency_gauge.labels(chain=chain, provider=self.current_provider_idx[chain]).set(latency)
                except Exception as e:
                    logger.warning(f"⚠️ {chain} RPC unhealthy: {e}")
                    self._failover(chain)
            time.sleep(5)  # every 5s
