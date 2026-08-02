import time

from apps.common.clients.dexscreener import DexScreenerClient


def scan_tokens():

    print("🔎 Procurando novos pares Solana...")

    client = DexScreenerClient()

    try:

        data = client.search("pump")

        tokens = []

        for pair in data.get("pairs", []):

            if pair.get("chainId") != "solana":
                continue

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

                created = datetime.datetime.fromtimestamp(
                    pair["pairCreatedAt"] / 1000
                )

                now = datetime.datetime.now()

                age_minutes = (
                    now - created
                ).total_seconds() / 60

            tokens.append({

                "address":
                    pair["baseToken"]["address"],

                "symbol":
                    pair["baseToken"]["symbol"],

                "name":
                    pair["baseToken"]["name"],

                "market_cap":
                    market_cap,

                "liquidity":
                    liquidity,

                "volume_24h":
                    volume,

                "buys":
                    pair.get("txns", {})
                    .get("h1", {})
                    .get("buys",0),

                "sells":
                    pair.get("txns", {})
                    .get("h1", {})
                    .get("sells",0),

                "price_change":
                    float(
                        pair.get("priceChange", {})
                        .get("h1") or 0
                    ),

                "age_minutes":
                    age_minutes,

                "dex":
                    pair.get("dexId")

            })

        return tokens

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