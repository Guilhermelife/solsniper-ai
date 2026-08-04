from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict

from apps.common.database import get_db
from apps.common.models.position import Position
from apps.common.models.signal import Signal

router = APIRouter(prefix="/readiness", tags=["Readiness"])

@router.get("/")
def get_readiness_report(db: Session = Depends(get_db)):
    positions = db.query(Position).filter(Position.status == "CLOSED").all()
    signals = db.query(Signal).all()
    
    if not positions or not signals:
        return {"message": "Not enough data to generate readiness report."}
        
    # 1. Overall Profitability
    wins = [p for p in positions if p.is_win]
    gross_profit = sum(p.profit_loss for p in wins)
    gross_loss = abs(sum(p.profit_loss for p in positions if not p.is_win))
    net_profit = gross_profit - gross_loss
    is_profitable = net_profit > 0
    
    # 2. Filter Analysis (Market Cap)
    mcap_stats = defaultdict(lambda: {"trades": 0, "wins": 0, "profit": 0.0})
    for p in positions:
        if not p.market_cap:
            bucket = "Unknown"
        elif p.market_cap < 50000:
            bucket = "<50k"
        elif p.market_cap < 250000:
            bucket = "50k-250k"
        elif p.market_cap < 1000000:
            bucket = "250k-1M"
        else:
            bucket = ">1M"
            
        mcap_stats[bucket]["trades"] += 1
        if p.is_win:
            mcap_stats[bucket]["wins"] += 1
        mcap_stats[bucket]["profit"] += p.profit_loss
        
    # Best / Worst Bucket
    best_mcap = max(mcap_stats.items(), key=lambda x: x[1]["profit"], default=("None", {}))[0]
    worst_mcap = min(mcap_stats.items(), key=lambda x: x[1]["profit"], default=("None", {}))[0]
    
    # 3. Signal Validation (Untraded Signals)
    # Find signals that didn't turn into positions
    traded_tokens = {p.token_address for p in positions}
    untraded_signals = [s for s in signals if s.decision == "BUY_SIGNAL" and s.token_address not in traded_tokens]
    
    untraded_stats = {
        "total_untraded": len(untraded_signals),
        "hit_10_pct_1h": 0,
        "hit_50_pct_6h": 0,
        "hit_100_pct_24h": 0
    }
    
    for s in untraded_signals:
        entry = s.price_usd
        if not entry:
            continue
            
        if s.peak_price_1h and s.peak_price_1h >= entry * 1.10:
            untraded_stats["hit_10_pct_1h"] += 1
            
        if s.peak_price_6h and s.peak_price_6h >= entry * 1.50:
            untraded_stats["hit_50_pct_6h"] += 1
            
        if s.peak_price_24h and s.peak_price_24h >= entry * 2.00:
            untraded_stats["hit_100_pct_24h"] += 1
            
    # 4. Recommendations
    recommendations = []
    if not is_profitable:
        recommendations.append("Strategy is currently unprofitable. Consider tightening MIN_AI_SCORE or adjusting stop loss.")
    if mcap_stats.get(worst_mcap, {}).get("profit", 0) < 0:
        recommendations.append(f"Market Cap range {worst_mcap} is losing money. Consider filtering it out.")
    if untraded_stats["hit_50_pct_6h"] > len(untraded_signals) * 0.2:
        recommendations.append("Untraded signals are hitting 50% profit often. Consider increasing MAX_OPEN_POSITIONS.")
        
    return {
        "is_profitable": is_profitable,
        "net_profit_usd": round(net_profit, 2),
        "total_trades_analyzed": len(positions),
        "filter_analysis": {
            "market_cap": mcap_stats,
            "best_contributor": best_mcap,
            "worst_contributor": worst_mcap
        },
        "signal_validation": untraded_stats,
        "recommendations": recommendations
    }
