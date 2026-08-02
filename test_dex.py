from pprint import pprint

from apps.common.clients.dexscreener import DexScreenerClient

client = DexScreenerClient()

tokens = client.search_tokens("BONK")

pprint(tokens[:5])

client.close()
