import os
import time
import json
import tempfile
import psutil
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
    # FIX-25: Initialize to a proper past time to avoid huge delta on first call
    last_snapshot_time = datetime.utcnow() - timedelta(hours=24)
    last_cleanup_time = datetime.utcnow() - timedelta(hours=24)
    
    try:
        while True:
            cycle_start_time = time.time()
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
                print(f"\nTokens scanned: {len(tokens)}")
                logger.info(f"Scan cycle completed. Tokens: {len(tokens)}")
                
                # FIX-05: Atomic write — prevents API from reading a truncated/empty file
                try:
                    with tempfile.NamedTemporaryFile('w', dir='logs', delete=False, suffix='.tmp') as tmp:
                        json.dump(tokens, tmp)
                    os.replace(tmp.name, 'logs/latest_scan.json')
                except Exception as e:
                    errors_logger.error(f"Error writing latest_scan.json: {e}")
            except Exception as e:
                errors_logger.error(f"Error scanning tokens: {e}")
                sleep_interval = sys_settings.scan_interval_seconds or 30
                time.sleep(sleep_interval)
                continue
            
            # Create a dict of token addresses to their current live price from the scan
            live_prices = {t["address"]: t.get("price_usd") for t in tokens if t.get("price_usd", 0) > 0}
            
            # Initialize tokens_for_ui early - will be updated later if missing prices are fetched
            tokens_for_ui = list(tokens)
            
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
                        token_snapshot = TokenSnapshot(
                            token_address=token["address"],
                            price_usd=token.get("price_usd", 0),
                            market_cap=token.get("market_cap", 0),
                            liquidity=token.get("liquidity", 0),
                            volume_24h=token.get("volume_24h", 0),
                            buys=token.get("buys", 0),
                            sells=token.get("sells", 0)
                        )
                        db.add(token_snapshot)
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
                if current_price and sig.price_usd and sig.price_usd > 0:
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
                    
                    # FIX-21: Update milestone fields — these were defined but never populated
                    roi_pct = ((current_price - sig.price_usd) / sig.price_usd) * 100.0
                    
                    if roi_pct >= 10.0 and not sig.hit_10_pct:
                        sig.hit_10_pct = True
                        if not sig.time_to_10_pct:
                            sig.time_to_10_pct = age_hours * 60  # store in minutes
                    if roi_pct >= 20.0 and not sig.hit_20_pct:
                        sig.hit_20_pct = True
                        if not sig.time_to_20_pct:
                            sig.time_to_20_pct = age_hours * 60
                    if roi_pct >= 50.0 and not sig.hit_50_pct:
                        sig.hit_50_pct = True
                        if not sig.time_to_50_pct:
                            sig.time_to_50_pct = age_hours * 60
                    if roi_pct >= 100.0 and not sig.hit_100_pct:
                        sig.hit_100_pct = True
                        if not sig.time_to_100_pct:
                            sig.time_to_100_pct = age_hours * 60
                    # Detect rugpull: price dropped more than 70% from signal price
                    if roi_pct <= -70.0 and not sig.did_rug:
                        sig.did_rug = True
                            
            db.commit()
            
            # 2.5 Evaluate WATCHING signals (e.g. for re-entries or pullbacks)
            watching_signals = db.query(Signal).filter(Signal.confirmation_status == "WATCHING").all()
            for sig in watching_signals:
                token = next((t for t in tokens if t["address"] == sig.token_address), None)
                if not token:
                    continue
                current_price = token.get("price_usd", 0)
                if current_price > 0:
                    # Check Re-Entry Logic
                    closed_positions = db.query(Position).filter(
                        Position.token_address == token["address"],
                        Position.status == "CLOSED"
                    ).order_by(Position.closed_at.desc()).all()
                    
                    if closed_positions:
                        last_closed = closed_positions[0]
                        # FIX-07: Use abs() so pullback works correctly regardless of sign
                        pullback_target = last_closed.highest_price * (1 - (abs(sys_settings.pullback_pct) / 100.0))
                        
                        if current_price <= pullback_target:  # Price dropped to or below pullback target
                            sig.confirmation_status = "BUYING"
                            db.commit()
                            
                            logger.info(f"Signal RE-ENTRY triggered for {sig.symbol} (Target: {pullback_target}, Current: {current_price})")
                            
                            # Phase 4: Portfolio Manager - Position Replacement
                            open_positions = db.query(Position).filter(Position.status == "OPEN").all()
                            max_positions = sys_settings.max_open_positions if sys_settings.max_open_positions else 5
                            
                            can_buy = True
                            if len(open_positions) >= max_positions:
                                if not sys_settings.position_replacement_enabled:
                                    logger.info(f"Portfolio full. Replacement disabled. {sig.symbol} rejected.")
                                    can_buy = False
                                else:
                                    for p in open_positions:
                                        t = next((tx for tx in tokens if tx["address"] == p.token_address), None)
                                        p._current_price = float(t.get("price_usd", p.entry_price) if t else p.entry_price)
                                        p._roi = ((p._current_price - p.entry_price) / p.entry_price) * 100.0 if p.entry_price > 0 else 0
                                    
                                    open_positions.sort(key=lambda x: x._roi)
                                    weakest_pos = open_positions[0]
                                    
                                    priority_diff = sig.priority_score - (weakest_pos.signal_score or 0)
                                    if weakest_pos._roi < sys_settings.replacement_threshold_pct and priority_diff >= sys_settings.priority_difference_threshold:
                                        logger.info(f"PORTFOLIO MANAGER: Replacing {weakest_pos.symbol} (ROI: {weakest_pos._roi:.2f}%) with {sig.symbol}")
                                        trades_logger.info(f"PORTFOLIO REPLACEMENT: Closed {weakest_pos.symbol} to buy {sig.symbol}")
                                        trader.close_position(weakest_pos, weakest_pos._current_price, sys_settings, exit_reason="Portfolio Manager Replacement")
                                    else:
                                        logger.info(f"Portfolio full. {sig.symbol} rejected.")
                                        can_buy = False
                            
                            if can_buy:
                                pos = trader.open_position(
                                    token=token,
                                    signal_score=sig.ai_score,
                                    sys_settings=sys_settings,
                                    entry_reason=f"Re-Entry (Pullback hit)"
                                )
                                if pos:
                                    sig.confirmation_status = "OPEN"
                                    pos.reentry_count = len(closed_positions)
                                    trades_logger.info(f"OPENED {pos.symbol} at {pos.entry_price}")
                                else:
                                    sig.confirmation_status = "REJECTED"
                                    sig.reason = "Failed to open position"
                            else:
                                sig.confirmation_status = "REJECTED"
                                sig.reason = "Portfolio Manager Rejected (Full)"
                            db.commit()
                        elif (datetime.utcnow() - sig.created_at).total_seconds() > (sys_settings.signal_lifetime_hours * 3600):
                            sig.confirmation_status = "EXPIRED"
                            logger.info(f"Signal EXPIRED for {sig.symbol} (Timeout waiting for pullback)")
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
            
            # FIX-24: Count only tokens that actually passed price filter and were analyzed
            tokens_analyzed += len(analyzed_results)

            # FIX-05: Atomic write for live signals cache
            try:
                with tempfile.NamedTemporaryFile('w', dir='logs', delete=False, suffix='.tmp') as tmp:
                    json.dump(analyzed_results, tmp)
                os.replace(tmp.name, 'logs/live_signals.json')
            except Exception as e:
                errors_logger.error(f"Error dumping live signals: {e}")
            
            for result in analyzed_results:
                token = result["token"]
                decision = result["decision"]
                
                latest_signal = db.query(Signal).filter(Signal.token_address == token["address"]).order_by(Signal.created_at.desc()).first()
                
                if decision == "BUY_SIGNAL":
                    cooldown_dt = datetime.utcnow() - timedelta(hours=sys_settings.signal_cooldown_hours or 6.0)
                    
                    # FIX: Only apply cooldown to signals that were ACTUALLY EXECUTED.
                    # REJECTED signals (no capital, position limit) should NOT block re-entry.
                    # The Live Radar shows BUY NOW → the bot must try again when capital is available.
                    executed_buy = db.query(Signal).filter(
                        Signal.token_address == token["address"],
                        Signal.decision == "BUY_SIGNAL",
                        Signal.confirmation_status.in_(["OPEN", "BUYING", "WATCHING"]),
                        Signal.created_at >= cooldown_dt
                    ).first()
                    
                    if executed_buy:
                        continue  # Already have an active position or watching this token

                    signals_generated += 1
                    print(f"\nSignal found (IMMEDIATE EXECUTION): {token['symbol']} | Priority: {result.get('priority_score', 0):.1f}")
                    
                    existing_pos = db.query(Position).filter(
                        Position.token_address == token["address"],
                        Position.status == "OPEN"
                    ).first()
                    
                    if existing_pos:
                        print(f"-> Skipping: Position already OPEN for {token['symbol']}")
                        continue
                        
                    closed_positions = db.query(Position).filter(
                        Position.token_address == token["address"],
                        Position.status == "CLOSED"
                    ).order_by(Position.closed_at.desc()).all()
                    
                    target_status = "BUYING"
                    entry_reason = "Scout BUY_SIGNAL (Immediate)"
                    reentry_count = 0
                    reject_reason = None
                    
                    if closed_positions:
                        if not sys_settings.reentry_enabled:
                            target_status = "REJECTED"
                            reject_reason = "Re-entries disabled"
                        else:
                            reentry_count = len(closed_positions)
                            if reentry_count >= sys_settings.max_reentries:
                                target_status = "REJECTED"
                                reject_reason = "Max re-entries reached"
                            else:
                                last_closed = closed_positions[0]
                                cooldown_end = last_closed.closed_at + timedelta(minutes=sys_settings.reentry_cooldown_minutes or 60)
                                if datetime.utcnow() < cooldown_end:
                                    target_status = "REJECTED"
                                    reject_reason = "Re-entry Cooldown"
                                else:
                                    # FIX-07: Use abs() to normalize pullback_pct regardless of sign entered by user
                                    pullback_target = last_closed.highest_price * (1 - (abs(sys_settings.pullback_pct) / 100.0))
                                    current_price = token.get("price_usd", 0)
                                    if current_price > pullback_target:
                                        target_status = "WATCHING"
                                        reject_reason = f"Waiting for pullback to {pullback_target:.8f}"
                                    else:
                                        entry_reason = f"Re-Entry #{reentry_count} (Immediate)"
                                        
                    # If target is BUYING, we execute NOW.
                    if target_status == "BUYING":
                        # Check portfolio replacement if full
                        open_positions = db.query(Position).filter(Position.status == "OPEN").all()
                        max_positions = sys_settings.max_open_positions if sys_settings.max_open_positions else 5
                        
                        if len(open_positions) >= max_positions:
                            if not sys_settings.position_replacement_enabled:
                                target_status = "REJECTED"
                                reject_reason = "Portfolio full"
                            else:
                                for p in open_positions:
                                    t = next((tx for tx in tokens if tx["address"] == p.token_address), None)
                                    p._current_price = float(t.get("price_usd", p.entry_price) if t else p.entry_price)
                                    p._roi = ((p._current_price - p.entry_price) / p.entry_price) * 100.0 if p.entry_price > 0 else 0
                                
                                open_positions.sort(key=lambda x: x._roi)
                                weakest_pos = open_positions[0]
                                priority_diff = result.get("priority_score", 0) - (weakest_pos.signal_score or 0)
                                
                                if weakest_pos._roi < sys_settings.replacement_threshold_pct and priority_diff >= sys_settings.priority_difference_threshold:
                                    trader.close_position(weakest_pos, weakest_pos._current_price, sys_settings, exit_reason="Portfolio Manager Replacement")
                                else:
                                    target_status = "REJECTED"
                                    reject_reason = "Portfolio full (Weakest not replaced)"
                                    
                    # Create signal record
                    signal = Signal(
                        token_address=token["address"],
                        symbol=token["symbol"],
                        ai_score=result["ai_score"],
                        priority_score=result.get("priority_score", 0),
                        freshness_score=result.get("freshness_score", 0),
                        decision=decision,
                        reason=reject_reason or result.get("reason"),
                        price_usd=token["price_usd"],
                        peak_price_1h=token["price_usd"],
                        peak_price_6h=token["price_usd"],
                        peak_price_24h=token["price_usd"],
                        confirmation_status=target_status
                    )
                    db.add(signal)
                    db.commit()
                    
                    if target_status == "BUYING":
                        pos = trader.open_position(
                            token=token,
                            signal_score=result["ai_score"],
                            sys_settings=sys_settings,
                            entry_reason=entry_reason
                        )
                        if pos:
                            signal.confirmation_status = "OPEN"
                            if reentry_count > 0:
                                pos.reentry_count = reentry_count
                            trades_logger.info(f"OPENED {pos.symbol} at {pos.entry_price}")
                        else:
                            signal.confirmation_status = "REJECTED"
                            signal.reason = "Failed to open position"
                        db.commit()

                elif not latest_signal or latest_signal.decision != decision:
                    signal = Signal(
                        token_address=token["address"],
                        symbol=token["symbol"],
                        ai_score=result["ai_score"],
                        priority_score=result.get("priority_score", 0),
                        freshness_score=result.get("freshness_score", 0),
                        decision=decision,
                        reason=result.get("reason"),
                        price_usd=token["price_usd"],
                        peak_price_1h=token["price_usd"],
                        peak_price_6h=token["price_usd"],
                        peak_price_24h=token["price_usd"],
                        confirmation_status="DETECTED"
                    )
                    db.add(signal)
                    db.commit()
                else:
                    latest_signal.ai_score = result["ai_score"]
                    latest_signal.priority_score = result.get("priority_score", 0)
                    latest_signal.freshness_score = result.get("freshness_score", 0)
                    latest_signal.reason = result.get("reason")
                    # FIX-01: updated_at is now a real column on Signal model
                    latest_signal.updated_at = datetime.utcnow()
                    db.commit()

            
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
            cpu_usage = psutil.cpu_percent(interval=None)
            mem_usage = psutil.virtual_memory().percent
            loop_duration = time.time() - cycle_start_time
            
            runtime_state = {
                "worker_running": True,
                "uptime_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "last_scan_at": datetime.utcnow().isoformat(),
                "scans_performed": scans_performed,
                "tokens_analyzed": tokens_analyzed,
                "signals_generated": signals_generated,
                "open_positions": db.query(Position).filter(Position.status == "OPEN").count(),
                "wallet_balance": trader.wallet.current_balance,
                "trades_executed": trader.wallet.total_trades,
                "cpu_usage_percent": cpu_usage,
                "memory_usage_percent": mem_usage,
                "loop_duration_seconds": loop_duration
            }
            with open("logs/runtime.json", "w") as f:
                json.dump(runtime_state, f)
                
            # 6. Auto-Cleanup Snapshots (Every 1 hour)
            # FIX-25: Use fresh datetime instead of loop-start 'now' to avoid drift
            cleanup_now = datetime.utcnow()
            if (cleanup_now - last_cleanup_time).total_seconds() >= 3600:
                try:
                    cutoff = cleanup_now - timedelta(hours=24)
                    
                    # Fetch all tokens that the bot has ever bought (Open or Closed)
                    active_positions = db.query(Position.token_address).all()
                    active_addresses = [p[0] for p in active_positions]
                    
                    # Delete snapshots older than 24h where token was NEVER bought
                    # Note: when active_addresses is empty, we skip the filter entirely
                    # to avoid accidentally deleting all snapshots
                    if active_addresses:
                        deleted = db.query(TokenSnapshot).filter(
                            TokenSnapshot.timestamp < cutoff,
                            ~TokenSnapshot.token_address.in_(active_addresses)
                        ).delete(synchronize_session=False)
                    else:
                        deleted = db.query(TokenSnapshot).filter(
                            TokenSnapshot.timestamp < cutoff
                        ).delete(synchronize_session=False)
                    
                    db.commit()
                    logger.info(f"Auto-cleanup: Deleted {deleted} old snapshots")
                except Exception as e:
                    errors_logger.error(f"Error during auto-cleanup: {e}")
                finally:
                    last_cleanup_time = cleanup_now
            
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