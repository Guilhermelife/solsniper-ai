import os
import json
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from apps.common.models.position import Position
from apps.common.models.signal import Signal

class Reporter:
    def __init__(self, db: Session):
        self.db = db
        os.makedirs("reports", exist_ok=True)
        
    def generate_daily_report(self, target_date: date):
        # Time window
        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = start_dt + timedelta(days=1)
        
        # Signals
        signals_query = self.db.query(Signal).filter(Signal.created_at >= start_dt, Signal.created_at < end_dt)
        signals_total = signals_query.count()
        signals_buy = signals_query.filter(Signal.decision == "BUY_SIGNAL").count()
        
        avg_ai_score = self.db.query(func.avg(Signal.ai_score)).filter(
            Signal.created_at >= start_dt, Signal.created_at < end_dt
        ).scalar() or 0.0
        
        # Positions
        pos_query = self.db.query(Position).filter(Position.created_at >= start_dt, Position.created_at < end_dt)
        trades_opened = pos_query.count()
        
        closed_query = self.db.query(Position).filter(Position.closed_at >= start_dt, Position.closed_at < end_dt, Position.status == "CLOSED")
        trades_closed = closed_query.count()
        
        wins = closed_query.filter(Position.is_win == True).count()
        win_rate = (wins / trades_closed * 100.0) if trades_closed > 0 else 0.0
        
        total_pnl = self.db.query(func.sum(Position.profit_loss)).filter(
            Position.closed_at >= start_dt, Position.closed_at < end_dt, Position.status == "CLOSED"
        ).scalar() or 0.0
        
        avg_holding = self.db.query(func.avg(Position.holding_time)).filter(
            Position.closed_at >= start_dt, Position.closed_at < end_dt, Position.status == "CLOSED"
        ).scalar() or 0.0
        
        # Best/Worst
        best_trade = closed_query.order_by(Position.profit_loss.desc()).first()
        worst_trade = closed_query.order_by(Position.profit_loss.asc()).first()
        
        best_trade_symbol = best_trade.symbol if best_trade else "N/A"
        worst_trade_symbol = worst_trade.symbol if worst_trade else "N/A"
        
        data = {
            "date": target_date.isoformat(),
            "signals_generated": signals_total,
            "buy_signals": signals_buy,
            "avg_ai_score": round(avg_ai_score, 2),
            "trades_opened": trades_opened,
            "trades_closed": trades_closed,
            "win_rate": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "best_trade": best_trade_symbol,
            "worst_trade": worst_trade_symbol,
            "avg_holding_time_minutes": round(avg_holding, 2)
        }
        
        # Save JSON
        json_path = f"reports/{target_date.isoformat()}.json"
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)
            
        # Save Markdown
        md_path = f"reports/{target_date.isoformat()}.md"
        with open(md_path, "w") as f:
            f.write(f"# Daily Report: {target_date.isoformat()}\n\n")
            f.write("## Signals\n")
            f.write(f"- **Total Scanned**: {signals_total}\n")
            f.write(f"- **BUY Signals**: {signals_buy}\n")
            f.write(f"- **Avg AI Score**: {round(avg_ai_score, 2)}\n\n")
            f.write("## Trades\n")
            f.write(f"- **Opened**: {trades_opened}\n")
            f.write(f"- **Closed**: {trades_closed}\n")
            f.write(f"- **Win Rate**: {round(win_rate, 2)}%\n")
            f.write(f"- **Total PnL**: ${round(total_pnl, 2)}\n")
            f.write(f"- **Avg Holding Time**: {round(avg_holding, 2)} minutes\n\n")
            f.write("## Highlights\n")
            f.write(f"- **Best Trade**: {best_trade_symbol}\n")
            f.write(f"- **Worst Trade**: {worst_trade_symbol}\n")
