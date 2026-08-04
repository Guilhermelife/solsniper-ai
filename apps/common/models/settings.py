from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from apps.common.database import Base

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, default=1)
    
    # Portfolio & Position Sizing
    position_size_mode: Mapped[str] = mapped_column(String, default="FIXED_USD") # FIXED_USD, PERCENTAGE, RISK_BASED, KELLY, AI_WEIGHTED
    default_position_size: Mapped[float] = mapped_column(Float, default=20.0)
    wallet_allocation_pct: Mapped[float] = mapped_column(Float, default=10.0)
    risk_per_trade_pct: Mapped[float] = mapped_column(Float, default=2.0)
    kelly_multiplier: Mapped[float] = mapped_column(Float, default=0.5)
    max_open_positions: Mapped[int] = mapped_column(Integer, default=5)
    max_wallet_exposure_pct: Mapped[float] = mapped_column(Float, default=80.0)
    
    position_replacement_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    replacement_threshold_pct: Mapped[float] = mapped_column(Float, default=-10.0)
    priority_difference_threshold: Mapped[float] = mapped_column(Float, default=20.0)
    max_positions_per_token: Mapped[int] = mapped_column(Integer, default=1)
    
    # Entry Filters
    min_ai_score: Mapped[float] = mapped_column(Float, default=90.0)
    min_priority_score: Mapped[float] = mapped_column(Float, default=80.0)
    min_freshness_score: Mapped[float] = mapped_column(Float, default=30.0)
    min_liquidity: Mapped[float] = mapped_column(Float, default=1000.0)
    min_volume: Mapped[float] = mapped_column(Float, default=5000.0)
    min_market_cap: Mapped[float] = mapped_column(Float, default=5000.0)
    max_market_cap: Mapped[float] = mapped_column(Float, default=500000.0)
    min_buy_sell_ratio: Mapped[float] = mapped_column(Float, default=1.5)
    min_momentum: Mapped[float] = mapped_column(Float, default=10.0)
    max_token_age_minutes: Mapped[int] = mapped_column(Integer, default=1440)
    allowed_dexes: Mapped[str] = mapped_column(String, default="raydium,pumpfun,meteora,orca,pumpswap")
    
    # Exit Strategy
    trailing_stop_pct: Mapped[float] = mapped_column(Float, default=15.0)
    stop_loss_pct: Mapped[float] = mapped_column(Float, default=-20.0)
    break_even_trigger_pct: Mapped[float] = mapped_column(Float, default=20.0)
    dynamic_trailing_stop: Mapped[bool] = mapped_column(Boolean, default=True)
    min_profit_before_trailing_pct: Mapped[float] = mapped_column(Float, default=10.0)
    trend_exit_sensitivity: Mapped[float] = mapped_column(Float, default=5.0)
    momentum_exit_threshold: Mapped[float] = mapped_column(Float, default=-5.0)
    
    # Re-Entry
    reentry_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    reentry_cooldown_minutes: Mapped[int] = mapped_column(Integer, default=60)
    max_reentries: Mapped[int] = mapped_column(Integer, default=3)
    pullback_pct: Mapped[float] = mapped_column(Float, default=-15.0)
    breakout_confirmation: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Scanner
    scan_interval_seconds: Mapped[int] = mapped_column(Integer, default=30)
    max_tokens_per_scan: Mapped[int] = mapped_column(Integer, default=60)
    watchlist_size: Mapped[int] = mapped_column(Integer, default=100)
    signal_lifetime_hours: Mapped[float] = mapped_column(Float, default=6.0)
    max_cached_signals: Mapped[int] = mapped_column(Integer, default=1000)
    signal_cooldown_hours: Mapped[float] = mapped_column(Float, default=6.0)
    
    # Paper Trading
    paper_initial_wallet: Mapped[float] = mapped_column(Float, default=50.0)
    paper_trading_fee_pct: Mapped[float] = mapped_column(Float, default=0.25)
    paper_slippage_pct: Mapped[float] = mapped_column(Float, default=1.0)
    paper_default_take_profit_pct: Mapped[float] = mapped_column(Float, default=1000.0)
    paper_default_stop_loss_pct: Mapped[float] = mapped_column(Float, default=-50.0)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
