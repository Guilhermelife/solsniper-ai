import io
import csv
from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from apps.common.database import get_db
from apps.common.models.position import Position
from apps.common.models.wallet import Wallet
from apps.common.models.signal import Signal

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    wallet = db.query(Wallet).first()
    
    open_count = db.query(Position).filter(Position.status == "OPEN").count()
    closed_count = db.query(Position).filter(Position.status == "CLOSED").count()
    
    avg_holding_time = db.query(func.avg(Position.holding_time)).filter(Position.status == "CLOSED").scalar()
    
    return {
        "wallet": {
            "initial_balance": wallet.initial_balance if wallet else 0,
            "current_balance": wallet.current_balance if wallet else 0,
            "total_profit": wallet.total_profit if wallet else 0,
            "total_loss": wallet.total_loss if wallet else 0,
            "win_rate": wallet.win_rate if wallet else 0,
            "total_trades": wallet.total_trades if wallet else 0,
        },
        "positions": {
            "open": open_count,
            "closed": closed_count,
            "avg_holding_time_minutes": float(avg_holding_time) if avg_holding_time else 0.0
        }
    }

@router.get("/positions")
def get_positions(db: Session = Depends(get_db)):
    positions = db.query(Position).order_by(Position.created_at.desc()).all()
    return {"positions": positions}

@router.get("/signals")
def get_signals(db: Session = Depends(get_db)):
    signals = db.query(Signal).order_by(Signal.created_at.desc()).all()
    return {"signals": signals}

@router.get("/insights")
def get_analytics(db: Session = Depends(get_db)):
    """Advanced analytics computed from historical data"""
    positions = db.query(Position).filter(Position.status == "CLOSED").all()
    
    if not positions:
        return {"message": "Not enough data"}
        
    total = len(positions)
    
    # 1. Win Rate by Dex
    dex_stats = {}
    for p in positions:
        dex = p.dex or "unknown"
        if dex not in dex_stats:
            dex_stats[dex] = {"trades": 0, "wins": 0, "total_profit": 0}
        dex_stats[dex]["trades"] += 1
        if p.is_win:
            dex_stats[dex]["wins"] += 1
        dex_stats[dex]["total_profit"] += p.profit_loss
        
    for k, v in dex_stats.items():
        v["win_rate"] = (v["wins"] / v["trades"]) * 100
        
    # 2. Avg profit by score range
    score_stats = {}
    for p in positions:
        if not p.signal_score: continue
        # Bucket to nearest 5 (e.g. 90, 95)
        bucket = int(p.signal_score // 5) * 5
        range_key = f"{bucket}-{bucket+4}"
        if range_key not in score_stats:
            score_stats[range_key] = {"trades": 0, "wins": 0, "total_profit": 0}
        score_stats[range_key]["trades"] += 1
        if p.is_win:
            score_stats[range_key]["wins"] += 1
        score_stats[range_key]["total_profit"] += p.profit_loss
        
    for k, v in score_stats.items():
        v["win_rate"] = (v["wins"] / v["trades"]) * 100
        v["avg_profit"] = v["total_profit"] / v["trades"]
        
    # 3. Best Performing Dex (simple string)
    best_dex = max(dex_stats.items(), key=lambda x: x[1]["win_rate"], default=("None", {}))[0]
    
    return {
        "total_analyzed_trades": total,
        "dex_performance": dex_stats,
        "score_performance": score_stats,
        "best_performing_dex": best_dex
    }

@router.get("/export/positions")
def export_positions(db: Session = Depends(get_db)):
    positions = db.query(Position).filter(Position.status == "CLOSED").order_by(Position.closed_at.asc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "id", "token_address", "symbol", "entry_price", "exit_price", 
        "amount_usd", "profit_loss_usd", "is_win", "holding_time_minutes", 
        "signal_score", "entry_reason", "exit_reason", "highest_price", "reentry_count", 
        "market_cap", "liquidity", 
        "volume_24h", "age_minutes", "dex", "buys", "sells", 
        "created_at", "closed_at"
    ])
    
    for p in positions:
        writer.writerow([
            p.id, p.token_address, p.symbol, p.entry_price, p.exit_price,
            p.amount_usd, p.profit_loss, p.is_win, p.holding_time,
            p.signal_score, p.entry_reason, p.exit_reason, p.highest_price, p.reentry_count,
            p.market_cap, p.liquidity,
            p.volume_24h, p.age_minutes, p.dex, p.buys, p.sells,
            p.created_at, p.closed_at
        ])
        
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=positions_export.csv"
    return response


@router.get("/snapshots")
def get_snapshots(db: Session = Depends(get_db)):
    from apps.common.models.wallet import DailyWalletSnapshot
    snapshots = db.query(DailyWalletSnapshot).order_by(DailyWalletSnapshot.date.asc()).all()
    return {"snapshots": snapshots}


@router.get("/strategy")
def get_strategy_metrics(db: Session = Depends(get_db)):
    positions = db.query(Position).filter(Position.status == "CLOSED").order_by(Position.closed_at.asc()).all()
    
    if not positions:
        return {"message": "Not enough data"}
        
    wins = [p for p in positions if p.is_win]
    losses = [p for p in positions if not p.is_win]
    
    gross_profit = sum(p.profit_loss for p in wins)
    gross_loss = abs(sum(p.profit_loss for p in losses))
    
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf') if gross_profit > 0 else 0.0
    
    avg_win = (gross_profit / len(wins)) if wins else 0.0
    avg_loss = (gross_loss / len(losses)) if losses else 0.0
    
    win_rate = len(wins) / len(positions)
    loss_rate = 1 - win_rate
    
    expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
    avg_r_multiple = (avg_win / avg_loss) if avg_loss > 0 else 0.0
    
    # Calculate Max Drawdown
    peak = 0.0
    max_dd = 0.0
    equity = 0.0
    
    consecutive_wins = 0
    max_consecutive_wins = 0
    consecutive_losses = 0
    max_consecutive_losses = 0
    
    for p in positions:
        equity += p.profit_loss
        if equity > peak:
            peak = equity
            
        drawdown = peak - equity
        if drawdown > max_dd:
            max_dd = drawdown
            
        if p.is_win:
            consecutive_wins += 1
            consecutive_losses = 0
            if consecutive_wins > max_consecutive_wins:
                max_consecutive_wins = consecutive_wins
        else:
            consecutive_losses += 1
            consecutive_wins = 0
            if consecutive_losses > max_consecutive_losses:
                max_consecutive_losses = consecutive_losses
                
    durations = [p.holding_time for p in positions if p.holding_time]
    durations.sort()
    
    if durations:
        mid = len(durations) // 2
        median_duration = durations[mid] if len(durations) % 2 != 0 else (durations[mid-1] + durations[mid]) / 2.0
        avg_duration = sum(durations) / len(durations)
    else:
        median_duration = 0.0
        avg_duration = 0.0
        
    return {
        "profit_factor": round(profit_factor, 2),
        "expectancy_usd": round(expectancy, 2),
        "avg_r_multiple": round(avg_r_multiple, 2),
        "max_drawdown_usd": round(max_dd, 2),
        "max_consecutive_wins": max_consecutive_wins,
        "max_consecutive_losses": max_consecutive_losses,
        "avg_trade_duration_minutes": round(avg_duration, 2),
        "median_trade_duration_minutes": round(median_duration, 2)
    }
