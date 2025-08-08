import asyncio
from types import SimpleNamespace
from typing import Any, Dict, List, Tuple, Optional

from backend.core.http_client import get_session


class ZeroXAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ZeroXClient:
    def __init__(self, api_key: str, network: str = "base"):
        self.api_key = api_key
        self.network = network.lower()
        self.base_url = self._get_base_url()

    def _get_base_url(self) -> str:
        network_map = {
            "mainnet": "https://api.0x.org",
            "base": "https://base.api.0x.org",
            "polygon": "https://polygon.api.0x.org",
            "bsc": "https://bsc.api.0x.org",
        }
        if self.network not in network_map:
            raise ZeroXAPIError(f"Unsupported network: {self.network}")
        return network_map[self.network]

    def _headers(self) -> Dict[str, str]:
        return {"0x-api-key": self.api_key} if self.api_key else {}

    @staticmethod
    def _quote_to_obj(data: Dict[str, Any]) -> SimpleNamespace:
        # Map 0x fields to snake_case attributes expected by router
        return SimpleNamespace(
            sell_token=data.get("sellTokenAddress") or data.get("sellToken"),
            buy_token=data.get("buyTokenAddress") or data.get("buyToken"),
            sell_amount=data.get("sellAmount"),
            buy_amount=data.get("buyAmount"),
            price=str(data.get("price")),
            guaranteed_price=str(data.get("guaranteedPrice", data.get("price"))),
            gas_estimate=str(data.get("estimatedGas") or data.get("gas") or "0"),
            gas_price=str(data.get("gasPrice", "0")),
            protocol_fee=str(data.get("protocolFee", "0")),
            allowance_target=data.get("allowanceTarget", ""),
            to=data.get("to", ""),
            data=data.get("data", ""),
            value=str(data.get("value", "0")),
            sources=data.get("sources", []),
        )

    async def get_swap_quote(
        self,
        sell_token: str,
        buy_token: str,
        sell_amount: Optional[str] = None,
        buy_amount: Optional[str] = None,
        slippage_percentage: float = 0.01,
        taker_address: Optional[str] = None,
    ) -> SimpleNamespace:
        """Get executable swap quote from 0x /swap/v1/quote"""
        url = f"{self.base_url}/swap/v1/quote"
        params: Dict[str, Any] = {
            "sellToken": sell_token,
            "buyToken": buy_token,
            "slippagePercentage": str(slippage_percentage),
        }
        if sell_amount:
            params["sellAmount"] = str(sell_amount)
        if buy_amount:
            params["buyAmount"] = str(buy_amount)
        if taker_address:
            params["takerAddress"] = taker_address

        session = await get_session()
        async with session.get(url, headers=self._headers(), params=params, timeout=10) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise ZeroXAPIError(f"0x API error: {resp.status} - {text[:400]}", status_code=resp.status)
            data = await resp.json()
            return self._quote_to_obj(data)

    async def get_token_price(self, sell_token: str, buy_token: str, sell_amount: str) -> Dict[str, Any]:
        """Get indicative price from 0x /swap/v1/price"""
        url = f"{self.base_url}/swap/v1/price"
        params = {
            "sellToken": sell_token,
            "buyToken": buy_token,
            "sellAmount": str(sell_amount),
        }
        session = await get_session()
        async with session.get(url, headers=self._headers(), params=params, timeout=10) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise ZeroXAPIError(f"0x API error: {resp.status} - {text[:400]}", status_code=resp.status)
            data = await resp.json()
            return {
                "price": float(data.get("price", 0)),
                "estimated_gas": int(data.get("estimatedGas", 0) or 0),
                "sell_amount": str(data.get("sellAmount") or params["sellAmount"]),
                "buy_amount": str(data.get("buyAmount", "0")),
                "sources": data.get("sources", []),
            }

    async def compare_prices_for_arbitrage(self, token_a: str, token_b: str, amount: str) -> Dict[str, Any]:
        """Compare A->B and then B->A to compute simple round-trip profitability."""
        # Forward: A -> B
        forward = await self.get_token_price(token_a, token_b, amount)
        amount_b = forward.get("buy_amount", "0")

        # Backward: B -> A using the output amount as sellAmount
        backward = await self.get_token_price(token_b, token_a, amount_b)
        amount_a_back = backward.get("buy_amount", "0")

        # Compute profit in wei (strings)
        try:
            profit_wei = str(int(amount_a_back) - int(amount))
        except Exception:
            profit_wei = "0"

        profit_percentage = 0.0
        try:
            if int(amount) > 0:
                profit_percentage = (int(profit_wei) / int(amount)) * 100.0
        except Exception:
            profit_percentage = 0.0

        estimated_gas = int(forward.get("estimated_gas", 0)) + int(backward.get("estimated_gas", 0))

        return {
            "token_a": token_a,
            "token_b": token_b,
            "profit_wei": profit_wei,
            "profit_percentage": profit_percentage,
            "is_profitable": int(profit_wei) > 0,
            "estimated_gas": estimated_gas,
            "gas_cost_wei": "0",  # No gas price provided by /price; left as 0
            "gas_cost_eth": 0.0,
            "net_profit_wei": profit_wei,
            "sources_a_to_b": forward.get("sources", []),
            "sources_b_to_a": backward.get("sources", []),
        }

    async def find_triangular_arbitrage(self, token_a: str, token_b: str, token_c: str, amount: str) -> Dict[str, Any]:
        """Simulate A->B->C->A using 0x price endpoint."""
        a_to_b = await self.get_token_price(token_a, token_b, amount)
        amt_b = a_to_b.get("buy_amount", "0")

        b_to_c = await self.get_token_price(token_b, token_c, amt_b)
        amt_c = b_to_c.get("buy_amount", "0")

        c_to_a = await self.get_token_price(token_c, token_a, amt_c)
        amt_a_final = c_to_a.get("buy_amount", "0")

        try:
            profit_wei = str(int(amt_a_final) - int(amount))
        except Exception:
            profit_wei = "0"
        profit_percentage = 0.0
        try:
            if int(amount) > 0:
                profit_percentage = (int(profit_wei) / int(amount)) * 100.0
        except Exception:
            profit_percentage = 0.0

        est_gas = int(a_to_b.get("estimated_gas", 0)) + int(b_to_c.get("estimated_gas", 0)) + int(c_to_a.get("estimated_gas", 0))

        return {
            "path": [token_a, token_b, token_c, token_a],
            "amounts": [str(amount), amt_b, amt_c, amt_a_final],
            "profit_wei": profit_wei,
            "profit_percentage": profit_percentage,
            "is_profitable": int(profit_wei) > 0,
            "estimated_gas": est_gas,
            "gas_cost_wei": "0",
            "gas_cost_eth": 0.0,
            "net_profit_wei": profit_wei,
            "steps": [
                {"from": token_a, "to": token_b},
                {"from": token_b, "to": token_c},
                {"from": token_c, "to": token_a},
            ],
        }

    async def get_supported_tokens(self) -> List[SimpleNamespace]:
        url = f"{self.base_url}/swap/v1/tokens"
        session = await get_session()
        async with session.get(url, headers=self._headers(), timeout=10) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise ZeroXAPIError(f"0x API error: {resp.status} - {text[:400]}", status_code=resp.status)
            data = await resp.json()
            tokens = data.get("records", []) or data.get("tokens", [])
            out: List[SimpleNamespace] = []
            for t in tokens:
                out.append(
                    SimpleNamespace(
                        address=t.get("address"),
                        symbol=t.get("symbol"),
                        name=t.get("name"),
                        decimals=int(t.get("decimals", 18)),
                        chain_id=8453,
                    )
                )
            return out

    async def get_liquidity_sources(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/swap/v1/sources"
        session = await get_session()
        async with session.get(url, headers=self._headers(), timeout=10) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise ZeroXAPIError(f"0x API error: {resp.status} - {text[:400]}", status_code=resp.status)
            data = await resp.json()
            return data.get("sources", data)

    async def batch_price_check(self, pairs: List[Tuple[str, str]], amount: str) -> Dict[str, Optional[Dict[str, Any]]]:
        async def one(a: str, b: str) -> Optional[Dict[str, Any]]:
            try:
                return await self.get_token_price(a, b, amount)
            except ZeroXAPIError:
                return None

        tasks = [one(a, b) for (a, b) in pairs]
        results = await asyncio.gather(*tasks)
        out: Dict[str, Optional[Dict[str, Any]]] = {}
        for (a, b), res in zip(pairs, results):
            out[f"{a}/{b}"] = res
        return out

    async def validate_api_key(self) -> bool:
        """Consider a 2xx response from /swap/v1/tokens as a valid key."""
        url = f"{self.base_url}/swap/v1/tokens"
        session = await get_session()
        async with session.get(url, headers=self._headers(), timeout=10) as resp:
            return 200 <= resp.status < 300

    async def health_check(self) -> Dict[str, Any]:
        """Simple health by checking sources endpoint"""
        url = f"{self.base_url}/swap/v1/sources"
        session = await get_session()
        async with session.get(url, headers=self._headers(), timeout=10) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise ZeroXAPIError(f"0x API error: {resp.status} - {text[:400]}", status_code=resp.status)
            data = await resp.json()
            return {"status": "healthy", "sources": data.get("sources", data)}
