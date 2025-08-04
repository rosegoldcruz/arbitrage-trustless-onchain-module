import requests


class ZeroXAPIError(Exception):
    pass


class ZeroXClient:
    def __init__(self, api_key: str, network: str = "mainnet"):
        self.api_key = api_key
        self.network = network.lower()
        self.base_url = self._get_base_url()

    def _get_base_url(self):
        network_map = {
            "mainnet": "https://api.0x.org",
            "base": "https://base.api.0x.org",
            "polygon": "https://polygon.api.0x.org",
            "bsc": "https://bsc.api.0x.org"
        }
        if self.network not in network_map:
            raise ZeroXAPIError(f"Unsupported network: {self.network}")
        return network_map[self.network]

    def get_swap_quote(self, buy_token: str, sell_token: str, sell_amount: int, slippage: float = 0.005):
        url = f"{self.base_url}/swap/v1/quote"
        headers = {
            "0x-api-key": self.api_key
        }
        params = {
            "buyToken": buy_token,
            "sellToken": sell_token,
            "sellAmount": sell_amount,
            "slippagePercentage": slippage
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise ZeroXAPIError(f"0x API error: {response.status_code} - {response.text}")

        return response.json()
