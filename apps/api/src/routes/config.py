from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from apps.common.database import get_db
from apps.common.models.settings import SystemSettings

router = APIRouter(prefix="/config", tags=["Configuration"])

class SystemSettingsUpdate(BaseModel):
    # Portfolio & Position Sizing
    position_size_mode: str | None = None
    default_position_size: float | None = None
    wallet_allocation_pct: float | None = None
    risk_per_trade_pct: float | None = None
    kelly_multiplier: float | None = None
    max_open_positions: int | None = None
    max_wallet_exposure_pct: float | None = None
    
    position_replacement_enabled: bool | None = None
    replacement_threshold_pct: float | None = None
    priority_difference_threshold: float | None = None
    max_positions_per_token: int | None = None
    
    # Entry Filters
    min_ai_score: float | None = None
    min_priority_score: float | None = None
    min_freshness_score: float | None = None
    min_liquidity: float | None = None
    min_volume: float | None = None
    min_market_cap: float | None = None
    max_market_cap: float | None = None
    min_buy_sell_ratio: float | None = None
    min_momentum: float | None = None
    max_token_age_minutes: int | None = None
    allowed_dexes: str | None = None
    
    # Exit Strategy
    trailing_stop_pct: float | None = None
    stop_loss_pct: float | None = None
    break_even_trigger_pct: float | None = None
    dynamic_trailing_stop: bool | None = None
    min_profit_before_trailing_pct: float | None = None
    trend_exit_sensitivity: float | None = None
    momentum_exit_threshold: float | None = None
    
    # Re-Entry
    reentry_enabled: bool | None = None
    reentry_cooldown_minutes: int | None = None
    max_reentries: int | None = None
    pullback_pct: float | None = None
    breakout_confirmation: bool | None = None
    
    # Scanner
    scan_interval_seconds: int | None = None
    max_tokens_per_scan: int | None = None
    watchlist_size: int | None = None
    signal_lifetime_hours: float | None = None
    max_cached_signals: int | None = None
    signal_cooldown_hours: float | None = None
    
    # Paper Trading
    paper_initial_wallet: float | None = None
    paper_trading_fee_pct: float | None = None
    paper_slippage_pct: float | None = None
    paper_default_take_profit_pct: float | None = None
    paper_default_stop_loss_pct: float | None = None

@router.get("/")
def get_config(db: Session = Depends(get_db)):
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("/")
def update_config(update_data: SystemSettingsUpdate, db: Session = Depends(get_db)):
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings(id=1)
        db.add(settings)
    
    update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in update_dict.items():
        setattr(settings, key, value)
        
    db.commit()
    db.refresh(settings)
    return settings
