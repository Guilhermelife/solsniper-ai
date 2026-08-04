import os
import time
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv

from apps.common.database import SessionLocal
from apps.common.models.position import Position
from apps.common.models.signal import Signal
from apps.common.models.snapshot import DailyWalletSnapshot
from apps.common.models.token_snapshot import TokenSnapshot
from apps.common.models.token import Token
from apps.common.models.settings import SystemSettings
from apps.worker.scout import scan_tokens
from apps.worker.analyzer import analyze_token
from apps.worker.trader import PaperTrader

# Setup Logging
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("worker")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("logs/worker.log", maxBytes=10*1024*1024, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

trades_logger = logging.getLogger("trades")
trades_logger.setLevel(logging.INFO)
t_handler = RotatingFileHandler("logs/trades.log", maxBytes=10*1024*1024, backupCount=5)
t_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
trades_logger.addHandler(t_handler)

errors_logger = logging.getLogger("errors")
errors_logger.setLevel(logging.ERROR)
e_handler = RotatingFileHandler("logs/errors.log", maxBytes=10*1024*1024, backupCount=5)
e_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
errors_logger.addHandler(e_handler)

def run():
    print("🚀 SolSniper Worker iniciado")
    logger.info("SolSniper Worker started")
    
    db = SessionLocal()
    trader = PaperTrader(db)
    
    start_time = datetime.utcnow()
    scans_performed = 0
    tokens_analyzed = 0
    signals_generated = 0
    last_snapshot_time = datetime.min
    last_cleanup_time = datetime.min
    
    try:
        while True:
            # Reload settings
            load_dotenv(override=True)
            
            # Fetch dynamic system settings
            sys_settings = db.query(SystemSettings).first()
            if not sys_settings:
                sys_settings = SystemSettings(id=1)
                db.add(sys_settings)
                db.commit()
                db.refresh(sys_settings)
            
            scans_performed += 1
            print("\n" + "=" * 40)
            print("🚀 SolSniper Cycle")
            
            # Fetch new pairs
            try:
                tokens = scan_tokens(sys_settings)
                tokens_analyzed += len(tokens)
                print(f"\nTokens scanned: {len(tokens)}")
                logger.info(f"Scan cycle completed. Tokens: {len(tokens)}")
                
                # Dump for API
                with open("logs/latest_scan.json", "w") as f:
                    json.dump(tokens, f)
            except Exception as e:
                errors_logger.error(f"Error scanning tokens: {e}")
                sleep_interval = sys_settings.scan_interval_seconds or 30
                time.sleep(sleep_interval)
                continue
            
            # Create a dict of token addresses to their current live price from the scan
            live_prices = {t["address"]: t.get("price_usd") for t in tokens if t.get("price_usd", 0) > 0}
            
            # 0. Save TokenSnapshots every 5 minutes and Upsert Tokens
            now = datetime.utcnow()
            if (now - last_snapshot_time).total_seconds() >= 300:
                snapshot_count = 0
                seen_tokens = set()
                for token in tokens:
                    addr = token.get("address")
                    if addr and addr not in seen_tokens:
                        seen_tokens.add(addr)
                        # Upsert Token
                        db_token = db.query(Token).filter(Token.address == addr).first()
                        if not db_token:
                            db_token = Token(
                                address=addr,
                                symbol=token.get("symbol", ""),
                                name=token.get("name", "")
                            )
                            db.add(db_token)
                            db.flush() # Flush to prevent duplicates within same batch
                        else:
                            db_token.symbol = token.get("symbol", "")
                            db_token.name = token.get("name", "")
                        
                        db_token.price_usd = token.get("price_usd", 0)
                        db_token.market_cap = token.get("market_cap", 0)
                        db_token.fdv = token.get("fdv", 0)
                        db_token.liquidity = token.get("liquidity", 0)
                        db_token.volume_5m = token.get("volume_5m", 0)
                        db_token.volume_1h = token.get("volume_1h", 0)
                        db_token.volume_24h = token.get("volume_24h", 0)
                        db_token.buys_5m = token.get("buys_5m", 0)
                        db_token.buys_1h = token.get("buys_1h", 0)
                        db_token.buys_24h = token.get("buys_24h", 0)
                        db_token.sells_5m = token.get("sells_5m", 0)
                        db_token.sells_1h = token.get("sells_1h", 0)
                        db_token.sells_24h = token.get("sells_24h", 0)
                        db_token.price_change_5m = token.get("price_change_5m", 0)
                        db_token.price_change_1h = token.get("price_change_1h", 0)
                        db_token.price_change_6h = token.get("price_change_6h", 0)
                        db_token.price_change_24h = token.get("price_change_24h", 0)
                        db_token.age_minutes = token.get("age_minutes", 0)
                        db_token.dex = token.get("dex")
                        db_token.chain = token.get("chain")
                        db_token.pair_address = token.get("pair_address")
                        db_token.website = token.get("website")
                        db_token.twitter = token.get("twitter")
                        db_token.telegram = token.get("telegram")
                        db_token.image = token.get("image")
                        db_token.description = token.get("description")

                        # Add Snapshot
                        snapshot = TokenSnapshot(
                            token_address=token["address"],
                            price_usd=token.get("price_usd", 0),
                            market_cap=token.get("market_cap", 0),
                            liquidity=token.get("liquidity", 0),
                            volume_24h=token.get("volume_24h", 0),
                            buys=token.get("buys", 0),
                            sells=token.get("sells", 0)
                        )
                        db.add(snapshot)
                        snapshot_count += 1
                db.commit()
                logger.info(f"Saved {snapshot_count} tokens and snapshots")
                last_snapshot_time = now
            
            # 1. Update all OPEN positions using live prices
            open_positions = db.query(Position).filter(Position.status == "OPEN").all()
            
            # Ensure we have prices for all OPEN positions, even if they fell off the scanner list
            missing_addresses = [pos.token_address for pos in open_positions if pos.token_address not in live_prices]
            if missing_addresses:
                try:
                    from apps.common.clients.dexscreener import DexScreenerClient
                    client = DexScreenerClient()
                    best_missing = {}
                    for i in range(0, len(missing_addresses), 30):
                        chunk = ",".join(missing_addresses[i:i+30])
                        data = client.get_token_pairs_v2(chunk)
                        for pair in data.get("pairs", []):
                            if pair.get("chainId") != "solana": continue
                            addr = pair.get("baseToken", {}).get("address")
                            liquidity = float(pair.get("liquidity", {}).get("usd") or 0)
                            if addr not in best_missing or liquidity > best_missing[addr].get("liquidity", 0):
                                price = float(pair.get("priceUsd") or 0)
                                best_missing[addr] = {
                                    "address": addr,
                                    "symbol": pair.get("baseToken", {}).get("symbol", ""),
                                    "name": pair.get("baseToken", {}).get("name", ""),
                                    "price_usd": price,
                                    "liquidity": liquidity
                                }
                    tokens_for_ui = list(tokens)
                    for addr, token_data in best_missing.items():
                        if token_data["price_usd"] > 0:
                            live_prices[addr] = token_data["price_usd"]
                            tokens_for_ui.append(token_data)
                    client.close()
                    
                    # Update API file so frontend stops "Waiting for tick..."
                    with open("logs/latest_scan.json", "w") as f:
                        json.dump(tokens_for_ui, f)
                        
                except Exception as e:
                    errors_logger.error(f"Error fetching missing prices for open positions: {e}")
            
            positions_status = []
            
            for pos in open_positions:
                token_data = next((t for t in tokens_for_ui if t["address"] == pos.token_address), None)
                
                if token_data and token_data.get("price_usd", 0) > 0:
                    # Check position
                    updated_pos = trader.check_position(pos, token_data, sys_settings)
                    current_price = token_data["price_usd"]
                    
                    # Calculate current PnL % for display
                    pnl_pct = ((current_price - pos.entry_price) / pos.entry_price) * 100
                    
                    if updated_pos and updated_pos.status == "CLOSED":
                        positions_status.append(f"{pos.symbol} {pnl_pct:+.1f}% (CLOSED)")
                        trades_logger.info(f"CLOSED {pos.symbol} at {current_price} | PnL: {updated_pos.profit_loss}")
                    else:
                        positions_status.append(f"{pos.symbol} {pnl_pct:+.1f}%")
                else:
                    positions_status.append(f"{pos.symbol} (Awaiting Price Update)")
                    
            # 2. Track Signal Quality (Prices for signals in last 24h)
            last_24h = datetime.utcnow() - timedelta(hours=24)
            recent_signals = db.query(Signal).filter(Signal.created_at >= last_24h).all()
            for sig in recent_signals:
                current_price = live_prices.get(sig.token_address)
                if current_price:
                    age_hours = (datetime.utcnow() - sig.created_at).total_seconds() / 3600
                    
                    if age_hours <= 1.0:
                        if not sig.peak_price_1h or current_price > sig.peak_price_1h:
                            sig.peak_price_1h = current_price
                    if age_hours <= 6.0:
                        if not sig.peak_price_6h or current_price > sig.peak_price_6h:
                            sig.peak_price_6h = current_price
                    if age_hours <= 24.0:
                        if not sig.peak_price_24h or current_price > sig.peak_price_24h:
                            sig.peak_price_24h = current_price
                            
            db.commit()
            
            # 2.5 Evaluate PENDING signals
            pending_signals = db.query(Signal).filter(Signal.confirmation_status == "PENDING").all()
            for sig in pending_signals:
                token = next((t for t in tokens if t["address"] == sig.token_address), None)
                if not token:
                    continue
                current_price = token.get("price_usd", 0)
                if current_price > 0 and sig.price_usd > 0:
                    price_change_since_signal = ((current_price - sig.price_usd) / sig.price_usd) * 100
                    
                    # Confirm if price increases by 2% (momentum confirmed)
                    if price_change_since_signal >= 2.0:
                        sig.confirmation_status = "CONFIRMED"
                        logger.info(f"Signal CONFIRMED for {sig.symbol} (+{price_change_since_signal:.2f}%)")
                        
                        # Open position now that it is confirmed
                        open_token_positions = db.query(Position).filter(
                            Position.token_address == sig.token_address,
                            Position.status == "OPEN"
                        ).count()
                        
                        if open_token_positions >= sys_settings.max_positions_per_token:
                            logger.info(f"Skipping {sig.symbol}: Max positions per token ({sys_settings.max_positions_per_token}) reached")
                            continue
                            
                        # Re-Entry Logic check
                        closed_positions = db.query(Position).filter(
                            Position.token_address == token["address"],
                            Position.status == "CLOSED"
                        ).order_by(Position.closed_at.desc()).all()
                        
                        reentry_count = 0
                        if closed_positions:
                            if not sys_settings.reentry_enabled:
                                logger.info(f"Skipping {sig.symbol}: Re-entries are disabled globally")
                                continue
                                
                            reentry_count = len(closed_positions)
                            if reentry_count >= sys_settings.max_reentries:
                                logger.info(f"Skipping {sig.symbol}: Max re-entries ({sys_settings.max_reentries}) reached")
                                continue
                                
                            last_closed = closed_positions[0]
                            pullback_target = last_closed.highest_price * (1 + (sys_settings.pullback_pct / 100.0))
                            if current_price > pullback_target:
                                logger.info(f"Skipping {sig.symbol}: Price {current_price} hasn't pulled back enough (Target: {pullback_target})")
                                continue
                                
                            entry_reason = f"Re-Entry #{reentry_count} (Confirmed)"
                        else:
                            entry_reason = "Scout BUY_SIGNAL (Confirmed)"
                            
                        # Phase 4: Portfolio Manager - Position Replacement
                        open_positions = db.query(Position).filter(Position.status == "OPEN").all()
                        max_positions = sys_settings.max_open_positions if sys_settings.max_open_positions else 5
                        
                        if len(open_positions) >= max_positions:
                            if not sys_settings.position_replacement_enabled:
                                logger.info(f"Portfolio full. Replacement disabled. {sig.symbol} rejected.")
                                continue
                                
                            for p in open_positions:
                                t = next((tx for tx in tokens if tx["address"] == p.token_address), None)
                                p._current_price = float(t.get("price_usd", p.entry_price) if t else p.entry_price)
                                p._roi = ((p._current_price - p.entry_price) / p.entry_price) * 100.0 if p.entry_price > 0 else 0
                            
                            open_positions.sort(key=lambda x: x._roi)
                            weakest_pos = open_positions[0]
                            
                            # Replace if weakest is underperforming (ROI < threshold) and new token has higher priority
                            priority_diff = sig.priority_score - (weakest_pos.signal_score or 0)
                            if weakest_pos._roi < sys_settings.replacement_threshold_pct and priority_diff >= sys_settings.priority_difference_threshold:
                                logger.info(f"PORTFOLIO MANAGER: Replacing {weakest_pos.symbol} (ROI: {weakest_pos._roi:.2f}%) with {sig.symbol} (Priority: {sig.priority_score:.1f}, Diff: {priority_diff:.1f})")
                                trades_logger.info(f"PORTFOLIO REPLACEMENT: Closed {weakest_pos.symbol} to buy {sig.symbol}")
                                trader.close_position(weakest_pos, weakest_pos._current_price, sys_settings, exit_reason="Portfolio Manager Replacement")
                            else:
                                logger.info(f"Portfolio full. {sig.symbol} rejected. Weakest is {weakest_pos.symbol} (ROI: {weakest_pos._roi:.2f}%), Priority diff {priority_diff:.1f} not enough.")
                                continue # Skip opening this position
                                
                            logger.info(f"Signal executed for {sig.symbol} (CONFIRMED)")
                            pos = trader.open_position(
                                token=token,
                                signal_score=sig.ai_score,
                                sys_settings=sys_settings,
                                entry_reason=entry_reason
                            )
                            if pos and reentry_count > 0:
                                pos.reentry_count = reentry_count
                            if not pos:
                                print(f"-> Failed to open position for {sig.symbol}.")
                            else:
                                trades_logger.info(f"OPENED {pos.symbol} at {pos.entry_price}")
                    
                    # Reject if price drops by 5% or lifetime passes
                    elif price_change_since_signal <= -5.0 or (datetime.utcnow() - sig.created_at).total_seconds() > (sys_settings.signal_lifetime_hours * 3600):
                        sig.confirmation_status = "REJECTED"
                        logger.info(f"Signal REJECTED for {sig.symbol} (Timeout or dropped {price_change_since_signal:.2f}%)")
            db.commit()

            # 3. Analyze new opportunities
            analyzed_results = []
            for token in tokens:
                if not token.get("price_usd") or token["price_usd"] <= 0:
                    continue
                    
                result = analyze_token(token, sys_settings)
                analyzed_results.append(result)
                
            # Sort by Priority Score DESC
            analyzed_results.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
            
            for result in analyzed_results:
                token = result["token"]
                
                is_new_buy = False
                
                # Cooldown check
                cooldown_hours = sys_settings.signal_cooldown_hours or 6.0
                cooldown_dt = datetime.utcnow() - timedelta(hours=cooldown_hours)
                existing_buy_signal = db.query(Signal).filter(
                    Signal.token_address == token["address"],
                    Signal.decision == "BUY_SIGNAL",
                    Signal.created_at >= cooldown_dt
                ).first()
                
                # Fetch latest signal (any decision)
                latest_signal = db.query(Signal).filter(
                    Signal.token_address == token["address"]
                ).order_by(Signal.created_at.desc()).first()

                if not latest_signal or latest_signal.decision != result["decision"]:
                    # Create new signal record because decision changed or it's the first time
                    signal = Signal(
                        token_address=token["address"],
                        symbol=token["symbol"],
                        ai_score=result["ai_score"],
                        priority_score=result.get("priority_score", 0),
                        freshness_score=result.get("freshness_score", 0),
                        decision=result["decision"],
                        reason=result.get("reason"),
                        price_usd=token["price_usd"],
                        peak_price_1h=token["price_usd"],
                        peak_price_6h=token["price_usd"],
                        peak_price_24h=token["price_usd"],
                        confirmation_status="PENDING" if result["decision"] == "BUY_SIGNAL" else "CONFIRMED"
                    )
                    db.add(signal)
                    db.commit()
                    if result["decision"] == "BUY_SIGNAL":
                        is_new_buy = True
                else:
                    # Update existing signal to reflect latest score and reason
                    latest_signal.ai_score = result["ai_score"]
                    latest_signal.priority_score = result.get("priority_score", 0)
                    latest_signal.freshness_score = result.get("freshness_score", 0)
                    latest_signal.reason = result.get("reason")
                    latest_signal.updated_at = datetime.utcnow()
                    db.commit()
                
                if result["decision"] == "BUY_SIGNAL" and is_new_buy:
                    signals_generated += 1
                    print(f"\nSignal found (PENDING CONFIRMATION): {token['symbol']} | Priority: {result.get('priority_score', 0):.1f}")
                    
                    if existing_buy_signal:
                        print(f"-> Skipping: Duplicate BUY_SIGNAL within {sys_settings.signal_cooldown_hours}h cooldown.")
                        logger.info(f"Duplicate BUY_SIGNAL suppressed for {token['symbol']}")
                        continue
                        
                    # Check if open position already exists
                    existing_pos = db.query(Position).filter(
                        Position.token_address == token["address"],
                        Position.status == "OPEN"
                    ).first()
                    
                    if existing_pos:
                        print(f"-> Skipping: Position already OPEN for {token['symbol']}")
                        continue
                        
                    # Re-Entry Logic check
                    closed_positions = db.query(Position).filter(
                        Position.token_address == token["address"],
                        Position.status == "CLOSED"
                    ).order_by(Position.closed_at.desc()).all()
                    
                    if closed_positions:
                        last_closed = closed_positions[0]
                        reentry_cooldown = sys_settings.reentry_cooldown_minutes if sys_settings and sys_settings.reentry_cooldown_minutes is not None else 60
                        cooldown_end = last_closed.closed_at + timedelta(minutes=reentry_cooldown)
                        if datetime.utcnow() < cooldown_end:
                            logger.info(f"Skipping Re-entry Watchlist for {token['symbol']} (Cooldown active until {cooldown_end})")
                            latest_signal = db.query(Signal).filter(Signal.token_address == token["address"]).order_by(Signal.created_at.desc()).first()
                            if latest_signal:
                                latest_signal.confirmation_status = "REJECTED"
                                latest_signal.reason = "Re-entry Cooldown"
                                db.commit()
                            continue
                    
                    logger.info(f"Added to Watchlist (PENDING): {token['symbol']}")
            
            # Show Open Positions
            if positions_status:
                print("\nOpen positions:")
                for status in positions_status:
                    print(status)
            else:
                print("\nOpen positions: None")
                
            print(f"\nWallet Balance: ${trader.wallet.current_balance:.2f} | Win Rate: {trader.wallet.win_rate:.1f}%")
            
            # 4. Daily Snapshot and Report
            today = datetime.utcnow().date()
            existing_snapshot = db.query(DailyWalletSnapshot).filter(DailyWalletSnapshot.date == today).first()
            if not existing_snapshot:
                w = trader.wallet
                open_count = db.query(Position).filter(Position.status == "OPEN").count()
                
                unrealized = 0.0
                current_open_positions = db.query(Position).filter(Position.status == "OPEN").all()
                for p in current_open_positions:
                    curr_price = live_prices.get(p.token_address)
                    if curr_price:
                        unrealized += ((curr_price - p.entry_price) / p.entry_price) * p.amount_usd
                
                snapshot = DailyWalletSnapshot(
                    date=today,
                    balance=w.current_balance,
                    realized_profit=w.total_profit - w.total_loss,
                    unrealized_profit=unrealized,
                    open_positions=open_count,
                    total_trades=w.total_trades
                )
                db.add(snapshot)
                db.commit()
                logger.info(f"Created daily snapshot for {today}")
                
                # Generate Daily Report for Yesterday
                from apps.worker.reporter import Reporter
                yesterday = today - timedelta(days=1)
                rep = Reporter(db)
                try:
                    rep.generate_daily_report(yesterday)
                    logger.info(f"Generated daily report for {yesterday}")
                except Exception as e:
                    errors_logger.error(f"Failed to generate daily report: {e}")
                
            # 5. Write Runtime State
            runtime_state = {
                "worker_running": True,
                "uptime_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "last_scan_at": datetime.utcnow().isoformat(),
                "scans_performed": scans_performed,
                "tokens_analyzed": tokens_analyzed,
                "signals_generated": signals_generated,
                "open_positions": db.query(Position).filter(Position.status == "OPEN").count(),
                "wallet_balance": trader.wallet.current_balance
            }
            with open("logs/runtime.json", "w") as f:
                json.dump(runtime_state, f)
                
            # 6. Auto-Cleanup Snapshots (Every 1 hour)
            if (now - last_cleanup_time).total_seconds() >= 3600:
                try:
                    cutoff = now - timedelta(hours=24)
                    
                    # Fetch all tokens that the bot has ever bought (Open or Closed)
                    active_positions = db.query(Position.token_address).all()
                    active_addresses = [p[0] for p in active_positions]
                    
                    # Delete snapshots older than 24h where token was NEVER bought
                    deleted = db.query(TokenSnapshot).filter(
                        TokenSnapshot.timestamp < cutoff,
                        ~TokenSnapshot.token_address.in_(active_addresses) if active_addresses else True
                    ).delete(synchronize_session=False)
                    
                    db.commit()
                    logger.info(f"Auto-cleanup: Deleted {deleted} old snapshots")
                except Exception as e:
                    errors_logger.error(f"Error during auto-cleanup: {e}")
                finally:
                    last_cleanup_time = now
            
            # Sleep
            sleep_interval = sys_settings.scan_interval_seconds or 30
            time.sleep(sleep_interval)
            
    except KeyboardInterrupt:
        print("\n⏹️ SolSniper Worker encerrado.")
        logger.info("Worker stopped by user")
    except Exception as e:
        errors_logger.exception("Fatal error in worker loop")
    finally:
        db.close()

if __name__ == "__main__":
    run()