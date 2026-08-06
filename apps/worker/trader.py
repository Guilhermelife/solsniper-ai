from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from apps.common.models.position import Position
from apps.common.models.wallet import Wallet
from apps.common.models.settings import SystemSettings


class PaperTrader:
    def __init__(self, db: Session):
        self.db = db  # FIX-19: Removed duplicate self.db = db assignment
        self.wallet = self._get_or_create_wallet()

    def _get_or_create_wallet(self) -> Wallet:
        wallet = self.db.query(Wallet).first()
        if not wallet:
            wallet = Wallet(
                initial_balance=50.0,
                current_balance=50.0,
                total_profit=0.0,
                total_loss=0.0,
                total_trades=0,
                win_rate=0.0,
                max_open_positions=5
            )
            self.db.add(wallet)
            self.db.commit()
            self.db.refresh(wallet)
        return wallet

    def open_position(
        self,
        token: dict,
        signal_score: float,
        sys_settings: SystemSettings,
        entry_reason: Optional[str] = None
    ) -> Optional[Position]:
        open_positions = self.db.query(Position).filter(Position.status == "OPEN").all()
        if len(open_positions) >= sys_settings.max_open_positions:
            return None  # Position limit reached

        # Check Max Wallet Exposure
        current_exposure = sum([p.amount_usd for p in open_positions])
        max_allowed_exposure = self.wallet.current_balance * (sys_settings.max_wallet_exposure_pct / 100.0)

        # Calculate amount_usd based on mode
        amount_usd = sys_settings.default_position_size
        if sys_settings.position_size_mode == "PERCENTAGE":
            amount_usd = self.wallet.current_balance * (sys_settings.wallet_allocation_pct / 100.0)
        elif sys_settings.position_size_mode == "RISK_BASED":
            stop_dist = abs(sys_settings.stop_loss_pct) if sys_settings.stop_loss_pct else 10.0
            amount_usd = (self.wallet.current_balance * (sys_settings.risk_per_trade_pct / 100.0)) / (stop_dist / 100.0)
        elif sys_settings.position_size_mode == "KELLY":
            if self.wallet.total_trades < 10:
                w_prob = 0.50
                w_ratio = 1.5
            else:
                w_prob = self.wallet.win_rate / 100.0
                win_trades = self.db.query(Position).filter(Position.profit_loss > 0, Position.status == "CLOSED").count()
                # FIX: Use only actual loss trades count (exclude breakeven)
                loss_trades = self.db.query(Position).filter(Position.profit_loss < 0, Position.status == "CLOSED").count()
                avg_win = self.wallet.total_profit / win_trades if win_trades > 0 else 0
                avg_loss = self.wallet.total_loss / loss_trades if loss_trades > 0 else 0
                w_ratio = (avg_win / avg_loss) if avg_loss > 0 else 1.5

            kelly_fraction = w_prob - ((1.0 - w_prob) / w_ratio) if w_ratio > 0 else 0
            kelly_fraction = max(0.01, min(0.99, kelly_fraction))

            amount_usd = self.wallet.current_balance * kelly_fraction * sys_settings.kelly_multiplier
        elif sys_settings.position_size_mode == "AI_WEIGHTED":
            weight = max(1.0, (signal_score - 80) / 10.0)
            amount_usd = sys_settings.default_position_size * weight

        # Ensure we don't exceed max exposure limit
        if current_exposure + amount_usd > max_allowed_exposure:
            amount_usd = max_allowed_exposure - current_exposure
            if amount_usd <= 0:
                return None  # Wallet is fully exposed

        if self.wallet.current_balance < amount_usd:
            return None  # Insufficient funds

        entry_price = float(token.get("price_usd") or 0)

        # FIX-06: Guard against entry_price == 0 — position with qty=0 is meaningless
        if entry_price <= 0:
            return None

        total_entry_cost_pct = sys_settings.paper_trading_fee_pct + sys_settings.paper_slippage_pct
        effective_amount_usd = amount_usd * (1 - (total_entry_cost_pct / 100.0))

        quantity = effective_amount_usd / entry_price

        stop_loss = entry_price * (1 - (abs(sys_settings.stop_loss_pct) / 100.0))
        highest_price = entry_price
        trailing_stop_price = highest_price * (1 - (abs(sys_settings.trailing_stop_pct) / 100.0))

        position = Position(
            token_address=token.get("address"),
            symbol=token.get("symbol"),
            entry_price=entry_price,
            amount_usd=amount_usd,
            quantity=quantity,
            status="OPEN",
            target_profit=entry_price * (1 + (abs(sys_settings.paper_default_take_profit_pct) / 100.0)),
            stop_loss=stop_loss,
            highest_price=highest_price,
            lowest_price=entry_price,
            trailing_stop_price=trailing_stop_price,
            signal_score=signal_score,
            entry_reason=entry_reason,
            market_cap=token.get("market_cap"),
            liquidity=token.get("liquidity"),
            volume_24h=token.get("volume_24h"),
            age_minutes=token.get("age_minutes"),
            dex=token.get("dex"),
            buys=token.get("buys"),
            sells=token.get("sells")
        )

        self.wallet.current_balance -= amount_usd

        self.db.add(position)
        self.db.commit()
        self.db.refresh(position)
        self.db.refresh(self.wallet)

        return position

    def close_position(self, position: Position, exit_price: float, sys_settings: SystemSettings, exit_reason: Optional[str] = None) -> Position:
        if position.status == "CLOSED":
            return position

        position.exit_price = exit_price
        position.status = "CLOSED"
        position.closed_at = datetime.utcnow()
        if exit_reason:
            position.exit_reason = exit_reason

        # FIX-15: Guard against created_at being None
        if position.created_at:
            delta = position.closed_at - position.created_at
            position.holding_time = delta.total_seconds() / 60.0
        else:
            position.holding_time = 0.0

        gross_exit_value = position.quantity * exit_price
        total_exit_cost_pct = sys_settings.paper_trading_fee_pct + sys_settings.paper_slippage_pct
        net_exit_amount = gross_exit_value * (1 - (total_exit_cost_pct / 100.0))

        profit_loss = net_exit_amount - position.amount_usd
        position.profit_loss = profit_loss
        position.is_win = profit_loss > 0

        self.wallet.current_balance += net_exit_amount
        self.wallet.total_trades += 1

        if profit_loss >= 0:
            self.wallet.total_profit += profit_loss
        else:
            self.wallet.total_loss += abs(profit_loss)

        self.db.flush()
        winning_trades = self.db.query(Position).filter(Position.profit_loss > 0, Position.status == "CLOSED").count()
        self.wallet.win_rate = (winning_trades / self.wallet.total_trades) * 100.0 if self.wallet.total_trades > 0 else 0.0

        self.db.commit()
        self.db.refresh(position)
        self.db.refresh(self.wallet)

        return position

    def check_position(self, position: Position, token: dict, sys_settings: SystemSettings) -> Optional[Position]:
        """
        Check an OPEN position against the current price.
        Updates trailing stop and closes it if it hits trailing stop, hard stop_loss, or momentum crash.
        """
        if position.status != "OPEN":
            return None

        current_price = float(token.get("price_usd", 0))
        if current_price <= 0:
            return None

        # Update Highest and Lowest Prices
        if not position.highest_price or current_price > position.highest_price:
            position.highest_price = current_price

        if not position.lowest_price or current_price < position.lowest_price:
            position.lowest_price = current_price

        # Calculate ROI
        current_roi = ((current_price - position.entry_price) / position.entry_price) * 100.0
        if not position.max_roi or current_roi > position.max_roi:
            position.max_roi = current_roi
        if not position.min_roi or current_roi < position.min_roi:
            position.min_roi = current_roi

        # 1. Start with hard stop loss as the floor if trailing stop isn't set
        if not position.trailing_stop_price:
            position.trailing_stop_price = position.stop_loss

        # 2. Break-Even Trigger
        if sys_settings.break_even_trigger_pct and position.max_roi >= sys_settings.break_even_trigger_pct:
            break_even_price = position.entry_price * (1 + ((sys_settings.paper_trading_fee_pct + sys_settings.paper_slippage_pct + 0.1) / 100.0))
            if not position.trailing_stop_price or position.trailing_stop_price < break_even_price:
                position.trailing_stop_price = break_even_price

        # 3. Dynamic Trailing (Only if we crossed the min_profit threshold)
        # FIX-04: Always use max() to ensure trailing stop never goes below break-even
        if sys_settings.dynamic_trailing_stop and position.max_roi >= sys_settings.min_profit_before_trailing_pct:
            new_trailing_stop = position.highest_price * (1 - (abs(sys_settings.trailing_stop_pct) / 100.0))
            # FIX-04: Never let the trailing stop move below the already-set stop (break-even protection)
            position.trailing_stop_price = max(new_trailing_stop, position.trailing_stop_price or 0)

        self.db.commit()

        # Exit Conditions

        # 0. Take Profit Hit
        if position.target_profit and current_price >= position.target_profit:
            execution_price = min(current_price, position.target_profit * (1 + (sys_settings.paper_slippage_pct / 100.0)))
            return self.close_position(position, execution_price, sys_settings, exit_reason=f"Take Profit Hit ({((current_price - position.entry_price)/position.entry_price)*100:.1f}%)")

        # 1. Momentum Exit (Only if in profit — FIX-09: avoid closing at a loss due to momentum)
        price_change_5m = float(token.get("price_change_5m", 0))
        if sys_settings.momentum_exit_threshold and price_change_5m <= sys_settings.momentum_exit_threshold:
            if current_roi >= 5.0:
                execution_price = max(current_price, current_price * (1 - (sys_settings.paper_slippage_pct / 100.0)))
                return self.close_position(position, execution_price, sys_settings, exit_reason=f"Momentum Exit ({price_change_5m:.1f}%, ROI: {current_roi:.1f}%)")

        # 2. Trailing Stop Hit
        # FIX-02: Use min() instead of max() — slippage makes exit price WORSE (lower), not better
        if position.trailing_stop_price and current_price <= position.trailing_stop_price:
            execution_price = min(current_price, position.trailing_stop_price * (1 - (sys_settings.paper_slippage_pct / 100.0)))
            return self.close_position(position, execution_price, sys_settings, exit_reason="Trailing Stop Hit")

        # 3. Hard Stop Loss Hit
        # FIX-02: Use min() for same reason — exit price is worse when falling
        if current_price <= position.stop_loss:
            execution_price = min(current_price, position.stop_loss * (1 - (sys_settings.paper_slippage_pct / 100.0)))
            return self.close_position(position, execution_price, sys_settings, exit_reason="Hard Stop Loss Hit")

        return None
