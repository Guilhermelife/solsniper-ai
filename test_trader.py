from apps.common.database import SessionLocal
from apps.common.models.signal import Signal
from apps.worker.trader import PaperTrader
import time

def run_test():
    db = SessionLocal()
    try:
        # Create a dummy signal
        signal = Signal(
            token_address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            symbol="USDC",
            ai_score=85.0,
            decision="BUY_SIGNAL"
        )
        db.add(signal)
        db.commit()
        db.refresh(signal)

        # Initialize Trader
        # Using 0.25% entry fee, 0.25% exit fee, 1.0% slippage as defaults
        trader = PaperTrader(db, take_profit_pct=50.0, stop_loss_pct=-20.0)
        
        print(f"Initial Wallet Balance: ${trader.wallet.current_balance}")
        print(f"Max Open Positions Configured: {trader.wallet.max_open_positions}")
        
        # Open Position
        amount_to_invest = 20.0
        entry_price = 1.0 # 1 USDC = $1
        print(f"Opening position for ${amount_to_invest} at price {entry_price}")
        position = trader.open_position(
            signal=signal, 
            entry_price=entry_price, 
            amount_usd=amount_to_invest,
            entry_reason="Testing paper trader logic with fees"
        )
        
        if not position:
            print("Failed to open position")
            return
            
        print(f"Position opened: {position.quantity:.4f} tokens (after {trader.entry_fee_pct + trader.slippage_pct}% fees). New balance: ${trader.wallet.current_balance:.2f}")
        print(f"Target Profit: {position.target_profit:.2f}, Stop Loss: {position.stop_loss:.2f}")
        
        # Check position with neutral price
        trader.check_position(position, current_price=1.1)
        print(f"After checking with price 1.1, status is {position.status}")
        
        # Delay briefly so holding time is > 0
        time.sleep(1)
        
        # Check position with hit target profit
        trader.check_position(position, current_price=1.55) # over 1.50
        print(f"After checking with price 1.55, status is {position.status}")
        
        if position.status == "CLOSED":
            print(f"Position Closed! Exit Price: {position.exit_price}")
            print(f"Profit/Loss (after {trader.exit_fee_pct + trader.slippage_pct}% fees): ${position.profit_loss:.4f}")
            print(f"Holding time: {position.holding_time:.4f} minutes")
            print(f"Final Wallet Balance: ${trader.wallet.current_balance:.4f}")
            print(f"Total Trades: {trader.wallet.total_trades}, Win Rate: {trader.wallet.win_rate:.1f}%")
            
    finally:
        # Cleanup
        db.delete(signal)
        if 'position' in locals() and position:
            db.delete(position)
        # Reset wallet for clean slate
        db.delete(trader.wallet)
        db.commit()
        db.close()

if __name__ == "__main__":
    run_test()
