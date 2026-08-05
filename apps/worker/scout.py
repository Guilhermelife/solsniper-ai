import time

from apps.common.clients.dexscreener import DexScreenerClient


def scan_tokens(sys_settings=None):

    print("🔎 Procurando novos pares Solana...")

    client = DexScreenerClient()

    try:

        profiles = client.get_latest_pairs()
        addresses = [p["tokenAddress"] for p in profiles if p.get("chainId") == "solana"]
        
        tokens = []
        if not addresses:
            return tokens
            
        limit = sys_settings.max_tokens_per_scan if sys_settings and sys_settings.max_tokens_per_scan else 30
        chunk = ",".join(addresses[:limit])
        data = client.get_token_pairs_v2(chunk)

        best_tokens = {}
        for pair in data.get("pairs", []):

            if pair.get("chainId") != "solana":
                continue

            address = pair["baseToken"]["address"]
            market_cap = float(
                pair.get("marketCap") or 0
            )

            liquidity = float(
                pair.get("liquidity", {}).get("usd") or 0
            )

            volume = float(
                pair.get("volume", {}).get("h24") or 0
            )

            age_minutes = 999999

            if pair.get("pairCreatedAt"):

                import datetime

                created = datetime.datetime.utcfromtimestamp(
                    pair["pairCreatedAt"] / 1000
                )

                now = datetime.datetime.utcnow()

                age_minutes = (
                    now - created
                ).total_seconds() / 60

            # Parse info
            info = pair.get("info", {})
            image = info.get("imageUrl")
            website = None
            twitter = None
            telegram = None

            for w in info.get("websites", []):
                if w.get("url"):
                    website = w.get("url")
                    break
            
            for s in info.get("socials", []):
                if s.get("type") == "twitter":
                    twitter = s.get("url")
                elif s.get("type") == "telegram":
                    telegram = s.get("url")

            txns = pair.get("txns", {})
            price_change = pair.get("priceChange", {})

            token_data = {
                "address": address,
                "symbol": pair["baseToken"]["symbol"],
                "name": pair["baseToken"]["name"],
                "price_usd": float(pair.get("priceUsd") or 0),
                "market_cap": market_cap,
                "fdv": float(pair.get("fdv") or 0),
                "liquidity": liquidity,
                "volume_5m": float(pair.get("volume", {}).get("m5") or 0),
                "volume_1h": float(pair.get("volume", {}).get("h1") or 0),
                "volume_24h": volume,
                "buys_5m": txns.get("m5", {}).get("buys", 0),
                "buys_1h": txns.get("h1", {}).get("buys", 0),
                "buys_24h": txns.get("h24", {}).get("buys", 0),
                "sells_5m": txns.get("m5", {}).get("sells", 0),
                "sells_1h": txns.get("h1", {}).get("sells", 0),
                "sells_24h": txns.get("h24", {}).get("sells", 0),
                "price_change_5m": float(price_change.get("m5") or 0),
                "price_change_1h": float(price_change.get("h1") or 0),
                "price_change_6h": float(price_change.get("h6") or 0),
                "price_change_24h": float(price_change.get("h24") or 0),
                "age_minutes": age_minutes,
                "dex": pair.get("dexId"),
                "chain": pair.get("chainId"),
                "pair_address": pair.get("pairAddress"),
                "website": website,
                "twitter": twitter,
                "telegram": telegram,
                "image": image,
                "description": None,
                "buys": txns.get("h1", {}).get("buys", 0),
                "sells": txns.get("h1", {}).get("sells", 0),
                "price_change": float(price_change.get("h1") or 0)
            }
            
            if address not in best_tokens or liquidity > best_tokens[address]["liquidity"]:
                best_tokens[address] = token_data

        return list(best_tokens.values())

    finally:

        client.close()


def run_scout():

    while True:

        tokens = scan_tokens()

        print(
            f"Encontrados {len(tokens)} tokens"
        )

        for token in tokens:

            from apps.worker.analyzer import analyze_token

            result = analyze_token(token)

            print("\n📊 Análise")
            print("====================")
            print(result)

        time.sleep(30)