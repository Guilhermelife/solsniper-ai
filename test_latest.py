from pprint import pprint

from apps.common.clients.dexscreener import DexScreenerClient

client = DexScreenerClient()

latest = client.get_latest_pairs()

solana = [
    t for t in latest
    if t["chainId"] == "solana"
]

token = solana[0]

print(token["tokenAddress"])

pairs = client.get_token_pairs(token["tokenAddress"])

print()
print("===== PAIRS =====")
print()

pprint(pairs)

client.close()
