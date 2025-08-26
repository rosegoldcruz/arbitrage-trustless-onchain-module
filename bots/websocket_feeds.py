#!/usr/bin/env python3
"""
ATOM WebSocket Price Feeds
- Connects to The Graph endpoints for Polygon DEXs
- Falls back to HTTP polling if WS fails
- No hardcoded addresses, everything from SecureConfig
"""

import asyncio
import json
import logging
import time
from typing import Dict, Optional, Callable

import websockets
import aiohttp
from config.secure_config import SecureConfig

logger = logging.getLogger("websocket_feeds")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()


class WebSocketPriceFeeds:
    def __init__(self):
        # Endpoints from env
        self.subgraph_endpoints = {
            "uniswap_v3": _cfg.require("UNISWAP_V3_SUBGRAPH_WSS"),
            "quickswap": _cfg.require("QUICKSWAP_SUBGRAPH_WSS"),
            "sushiswap": _cfg.require("SUSHISWAP_SUBGRAPH_WSS"),
            "balancer": _cfg.require("BALANCER_SUBGRAPH_WSS"),
        }
        self.http_endpoints = {
            "uniswap_v3": _cfg.require("UNISWAP_V3_SUBGRAPH_HTTP"),
            "quickswap": _cfg.require("QUICKSWAP_SUBGRAPH_HTTP"),
            "sushiswap": _cfg.require("SUSHISWAP_SUBGRAPH_HTTP"),
            "balancer": _cfg.require("BALANCER_SUBGRAPH_HTTP"),
        }

        self.tokens = _cfg.get_token_addresses()

        self.reconnect_attempts = int(_cfg.env.get("WS_RECONNECT_ATTEMPTS", "5"))
        self.reconnect_delay = int(_cfg.env.get("WS_RECONNECT_DELAY_MS", "5000")) / 1000

        self.connections = {}
        self.price_callbacks = []
        self.latest_prices = {}
        self.connection_status = {}
        self.running = False

    def add_price_callback(self, cb: Callable):
        self.price_callbacks.append(cb)

    async def start_all(self):
        self.running = True
        logger.info("Starting WebSocket price feeds...")
        tasks = [asyncio.create_task(self._maintain_connection(name)) for name in self.subgraph_endpoints]
        await asyncio.gather(*tasks)

    async def _maintain_connection(self, dex_name: str):
        retries = 0
        while self.running and retries < self.reconnect_attempts:
            try:
                await self._connect_ws(dex_name)
                retries = 0
            except Exception as e:
                logger.warning(f"{dex_name} WS error: {e}")
                retries += 1
                if retries < self.reconnect_attempts:
                    await asyncio.sleep(self.reconnect_delay * retries)
                else:
                    logger.error(f"{dex_name} WS failed, switching to HTTP poll")
                    await self._poll_http(dex_name)

    async def _connect_ws(self, dex_name: str):
        endpoint = self.subgraph_endpoints[dex_name]
        async with websockets.connect(endpoint) as ws:
            self.connections[dex_name] = ws
            self.connection_status[dex_name] = "connected"
            logger.info(f"Connected to {dex_name} WebSocket")

            sub = {"id": "1", "type": "start", "payload": {"query": self._subscription_query(dex_name)}}
            await ws.send(json.dumps(sub))

            async for msg in ws:
                try:
                    data = json.loads(msg)
                    await self._process_prices(dex_name, data)
                except Exception as e:
                    logger.error(f"{dex_name} msg error: {e}")

    async def _poll_http(self, dex_name: str):
        endpoint = self.http_endpoints[dex_name]
        self.connection_status[dex_name] = "http_polling"
        while self.running:
            try:
                async with aiohttp.ClientSession() as s:
                    resp = await s.post(endpoint, json={"query": self._http_query(dex_name)})
                    data = await resp.json()
                    await self._process_prices(dex_name, data)
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"{dex_name} HTTP poll error: {e}")
                await asyncio.sleep(5)

    def _subscription_query(self, dex_name: str) -> str:
        # Generic subscription; tokens injected
        addrs = list(self.tokens.values())
        return f"""
            subscription {{
                pairs(
                    where: {{ token0_in: {addrs}, token1_in: {addrs} }}
                    orderBy: reserveUSD
                    orderDirection: desc
                    first: 20
                ) {{
                    id
                    token0 {{ id symbol decimals }}
                    token1 {{ id symbol decimals }}
                    token0Price
                    token1Price
                    reserveUSD
                    volumeUSD
                }}
            }}
        """

    def _http_query(self, dex_name: str) -> str:
        return self._subscription_query(dex_name).replace("subscription", "query")

    async def _process_prices(self, dex_name: str, data: Dict):
        try:
            pairs = data.get("data", {}).get("pairs", [])
            for p in pairs:
                t0, t1 = p["token0"], p["token1"]
                update = {
                    "dex": dex_name,
                    "pair": f"{t0['symbol']}/{t1['symbol']}",
                    "price": float(p["token0Price"]),
                    "reserve_usd": float(p.get("reserveUSD", 0)),
                    "volume_usd": float(p.get("volumeUSD", 0)),
                    "timestamp": time.time(),
                }
                self.latest_prices.setdefault(dex_name, {})[update["pair"]] = update
                for cb in self.price_callbacks:
                    try:
                        await cb(update)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
        except Exception as e:
            logger.error(f"Process prices error {dex_name}: {e}")
