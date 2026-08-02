import httpx


class DexScreenerClient:
    BASE_URL = "https://api.dexscreener.com/latest/dex"

    def __init__(self):
        self.client = httpx.Client(timeout=20)

    def search(self, query: str):
        response = self.client.get(
            f"{self.BASE_URL}/search",
            params={"q": query},
        )

        response.raise_for_status()
        return response.json()

    def search_tokens(self, query: str):
        data = self.search(query)

        best_tokens = {}

        for pair in data.get("pairs", []):
            if pair.get("chainId") != "solana":
                continue

            address = pair["baseToken"]["address"]
            liquidity = float(pair.get("liquidity", {}).get("usd") or 0)

            token = {
                "address": address,
                "symbol": pair["baseToken"]["symbol"],
                "name": pair["baseToken"]["name"],
                "price_usd": float(pair.get("priceUsd") or 0),
                "liquidity": liquidity,
                "volume_24h": float(pair.get("volume", {}).get("h24") or 0),
                "pair_address": pair["pairAddress"],
                "dex": pair["dexId"],
            }

            if (
                address not in best_tokens
                or liquidity > best_tokens[address]["liquidity"]
            ):
                best_tokens[address] = token

        return list(best_tokens.values())

    def get_latest_pairs(self):
        response = self.client.get(
            "https://api.dexscreener.com/token-profiles/latest/v1"
        )

        response.raise_for_status()

        return response.json()

    def get_token_pairs(self, token_address: str):
        response = self.client.get(
            f"https://api.dexscreener.com/token-pairs/v1/solana/{token_address}"
        )

        response.raise_for_status()

        return response.json()

    def get_token_pairs_v2(self, address: str):
        url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"

        response = self.client.get(url)

        response.raise_for_status()

        return response.json()

    def get_pair(self, chain: str, pair_address: str):
        response = self.client.get(
            f"{self.BASE_URL}/pairs/{chain}/{pair_address}"
        )

        response.raise_for_status()
        return response.json()

    def close(self):
        self.client.close()
