def analyze_token(token: dict):

    score = 0

    liquidity = token.get("liquidity", 0)
    volume = token.get("volume_24h", 0)
    buys = token.get("buys", 0)
    sells = token.get("sells", 0)
    price_change = token.get("price_change", 0)
    market_cap = token.get("market_cap", 0)
    age = token.get("age_minutes", 999999)

    # Liquidez
    if liquidity >= 100000:
        score += 20
    elif liquidity >= 30000:
        score += 15
    elif liquidity >= 10000:
        score += 10

    # Volume
    if volume >= 200000:
        score += 20
    elif volume >= 50000:
        score += 15
    elif volume >= 10000:
        score += 10

    # Compra vs venda
    if buys > sells * 2:
        score += 25
    elif buys > sells:
        score += 15

    # Market Cap (potencial 100x)
    if market_cap < 50000:
        score += 30
    elif market_cap < 250000:
        score += 25
    elif market_cap < 1000000:
        score += 15
    elif market_cap < 10000000:
        score += 5

    # Idade
    if age < 30:
        score += 25
    elif age < 180:
        score += 20
    elif age < 1440:
        score += 10

    # Movimento
    if price_change >= 50:
        score += 10
    elif price_change >= 20:
        score += 5

    if score >= 90:
        decision = "BUY_SIGNAL"
    elif score >= 60:
        decision = "WATCH"
    else:
        decision = "IGNORE"

    return {
        "token": token,
        "ai_score": score,
        "decision": decision
    }