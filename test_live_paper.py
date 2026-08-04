from apps.common.database import SessionLocal
from apps.common.models.position import Position
from apps.common.models.signal import Signal
from apps.worker.trader import PaperTrader
import time

def mock_scan_cycle_1():
    return [
        {
            "address": "MOCK111111111111111111111111111111111111111",
            "symbol": "MOCK",
            "name": "Mock Token",
            "price_usd": 0.0001,
            "liquidity": 50000,
            "volume_24h": 100000,
            "buys": 300,
            "sells": 100,
            "price_change": 10,
            "market_cap": 100000,
            "age_minutes": 10,
            "dex": "raydium"
        }
    ]

def mock_scan_cycle_2():
    return [
        {
            "address": "MOCK111111111111111111111111111111111111111",
            "symbol": "MOCK",
            "price_usd": 0.00018, # An 80% gain, hits our TP of 50%
        }
    ]

def run_test():
    db = SessionLocal()
    trader = PaperTrader(db)
    
    # Cleanup DB before test
    db.query(Position).delete()
    db.query(Signal).delete()
    db.commit()

    print("\n--- CYCLE 1: MOCK SCAN & BUY ---")
    
    # Cycle 1
    tokens_c1 = mock_scan_cycle_1()
    
    # Analyze (Mocking the analyzer which should return BUY_SIGNAL for MOCK)
    for token in tokens_c1:
        # Mocking analyze_token result:
        result = {"decision": "BUY_SIGNAL", "ai_score": 95}
        
        print("\nSignal found:")
        print(f"TOKEN: {token['symbol']}")
        print(f"Score: {result['ai_score']}")
        print(f"Decision: BUY_SIGNAL")
        
        signal = Signal(
            token_address=token["address"],
            symbol=token["symbol"],
            ai_score=result["ai_score"],
            decision="BUY_SIGNAL"
        )
        db.add(signal)
        db.commit()
        
        print("\nOpening paper position:")
        print(f"Amount: $20.0")
        print(f"Entry price: {token['price_usd']}")
        
        pos = trader.open_position(
            token=token,
            signal_score=result["ai_score"],
            amount_usd=20.0,
            entry_reason="Test Signal"
        )

    print(f"\nWallet Balance after buy: ${trader.wallet.current_balance:.2f}")

    time.sleep(1)

    print("\n--- CYCLE 2: MOCK PRICE UPDATE & SELL ---")
    
    tokens_c2 = mock_scan_cycle_2()
    live_prices = {t["address"]: t["price_usd"] for t in tokens_c2}
    
    open_positions = db.query(Position).filter(Position.status == "OPEN").all()
    
    for pos in open_positions:
        current_price = live_prices.get(pos.token_address)
        if current_price:
            updated_pos = trader.check_position(pos, current_price)
            pnl_pct = ((current_price - pos.entry_price) / pos.entry_price) * 100
            
            if updated_pos and updated_pos.status == "CLOSED":
                print(f"{pos.symbol} {pnl_pct:+.1f}% (CLOSED)")
            else:
                print(f"{pos.symbol} {pnl_pct:+.1f}%")

    print(f"\nFinal Wallet Balance: ${trader.wallet.current_balance:.2f} | Win Rate: {trader.wallet.win_rate:.1f}%")

    db.close()

if __name__ == "__main__":
    run_test()
