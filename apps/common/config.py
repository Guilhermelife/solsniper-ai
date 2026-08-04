from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SolSniper AI API"
    version: str = "0.1.0"
    environment: str = "development"
    
    scan_interval_seconds: int = 30
    default_position_size: float = 20.0
    take_profit_pct: float = 50.0
    stop_loss_pct: float = -20.0
    trailing_stop_pct: float = 15.0
    reentry_cooldown_minutes: int = 60
    max_open_positions: int = 5
    initial_balance: float = 50.0
    signal_cooldown_hours: float = 6.0
    
    min_market_cap: float = 10000.0
    max_market_cap: float = 500000.0
    min_liquidity: float = 5000.0
    min_volume: float = 10000.0
    min_ai_score: float = 90.0
    
    class Config:
        env_file = ".env"

settings = Settings()