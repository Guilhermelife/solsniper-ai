from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String
from apps.common.database import Base

class TokenSnapshot(Base):
    __tablename__ = "token_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    token_address = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    price_usd = Column(Float, default=0.0)
    market_cap = Column(Float, default=0.0)
    liquidity = Column(Float, default=0.0)
    volume_24h = Column(Float, default=0.0)
    buys = Column(Integer, default=0)
    sells = Column(Integer, default=0)
