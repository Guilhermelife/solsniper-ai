from apps.common.models.settings import SystemSettings

def analyze_token(token: dict, sys_settings: SystemSettings):
    score = 0
    priority_score = 0.0
    freshness_score = 100.0

    liquidity = token.get("liquidity", 0)
    volume = token.get("volume_24h", 0)
    buys = token.get("buys", 0)
    sells = token.get("sells", 0)
    price_change = token.get("price_change", 0)
    market_cap = token.get("market_cap", 0)
    age = token.get("age_minutes", 999999)

    # Hard Filters
    if market_cap < sys_settings.min_market_cap or market_cap > sys_settings.max_market_cap:
        return {"token": token, "ai_score": 0, "priority_score": 0, "freshness_score": 0, "decision": "IGNORE", "reason": f"MCap {market_cap} outside range"}

    # FIX-12: Guard against dex being None explicitly (not just absent)
    dex = (token.get("dex") or "").lower()

    # Optional DEX allowed list check
    allowed_dexes = [d.strip().lower() for d in sys_settings.allowed_dexes.split(",") if d.strip()]
    if allowed_dexes and dex not in allowed_dexes:
        return {"token": token, "ai_score": 0, "priority_score": 0, "freshness_score": 0, "decision": "IGNORE", "reason": f"DEX {dex} not allowed"}

    if dex == "pumpfun":
        if buys < 30:  # Pumpfun still needs some minimal buys
            return {"token": token, "ai_score": 0, "priority_score": 0, "freshness_score": 0, "decision": "IGNORE", "reason": f"Pump.fun Buys {buys} too low"}
    else:
        if liquidity < sys_settings.min_liquidity:
            return {"token": token, "ai_score": 0, "priority_score": 0, "freshness_score": 0, "decision": "IGNORE", "reason": f"Liq {liquidity} too low"}

        if volume < sys_settings.min_volume:
            return {"token": token, "ai_score": 0, "priority_score": 0, "freshness_score": 0, "decision": "IGNORE", "reason": f"Vol {volume} too low"}

    # Freshness Validation
    if age > sys_settings.max_token_age_minutes:
        return {"token": token, "ai_score": 0, "priority_score": 0, "freshness_score": 0, "decision": "IGNORE", "reason": f"Age {age} exceeds max allowed"}

    if age > 1440:  # 24h
        freshness_score -= 30
    if age > 4320:  # 3 days
        freshness_score -= 30
    if price_change > 300:  # Already up 300%
        freshness_score -= 40
    if price_change > 1000:  # Already up 10x
        freshness_score -= 60

    # FIX-08: Clamp freshness_score to 0 minimum — negative scores are semantically wrong
    freshness_score = max(0.0, freshness_score)

    if freshness_score < sys_settings.min_freshness_score:
        return {"token": token, "ai_score": 0, "priority_score": 0, "freshness_score": freshness_score, "decision": "IGNORE", "reason": f"Low Freshness (Score {freshness_score:.1f})"}

    # Buy/Sell Ratio Check
    if sells > 0 and (buys / sells) < sys_settings.min_buy_sell_ratio:
        return {"token": token, "ai_score": 0, "priority_score": 0, "freshness_score": freshness_score, "decision": "IGNORE", "reason": "Buy/Sell ratio too low"}

    # AI Score Calculation (Base logic)
    # Liquidez
    if liquidity >= 100000:
        score += 20
    elif liquidity >= 30000:
        score += 15
    elif liquidity >= 10000:
        score += 10
    elif dex == "pumpfun" and market_cap >= 15000:
        score += 15  # Compensate for lack of liquidity before migration

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

    # Calculate Priority Score (combining AI Score, Freshness, and volume/liquidity weighting)
    priority_score = score + (freshness_score * 0.5)

    if score >= sys_settings.min_ai_score and priority_score >= sys_settings.min_priority_score:
        decision = "BUY_SIGNAL"
        reason = f"High Score ({score}) Priority ({priority_score:.1f})"
    elif score >= sys_settings.min_ai_score - 30:
        decision = "WATCH"
        reason = f"Medium Score ({score})"
    else:
        decision = "IGNORE"
        reason = f"Low Score ({score})"

    return {
        "token": token,
        "ai_score": score,
        "priority_score": priority_score,
        "freshness_score": freshness_score,
        "decision": decision,
        "reason": reason
    }