from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Boolean

from apps.common.database import Base


class Signal(Base):

    __tablename__ = "signals"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    token_address = Column(
        String,
        nullable=False
    )

    symbol = Column(
        String,
        nullable=False
    )

    ai_score = Column(
        Float,
        nullable=False
    )

    decision = Column(
        String,
        nullable=False
    )

    reason = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    price_usd = Column(
        Float,
        nullable=True
    )

    peak_price_1h = Column(
        Float,
        nullable=True
    )

    peak_price_6h = Column(
        Float,
        nullable=True
    )

    peak_price_24h = Column(
        Float,
        nullable=True
    )

    hit_10_pct = Column(Boolean, default=False)
    hit_20_pct = Column(Boolean, default=False)
    hit_50_pct = Column(Boolean, default=False)
    hit_100_pct = Column(Boolean, default=False)
    did_rug = Column(Boolean, default=False)

    time_to_10_pct = Column(Float, nullable=True) # minutes
    time_to_20_pct = Column(Float, nullable=True)
    time_to_50_pct = Column(Float, nullable=True)
    time_to_100_pct = Column(Float, nullable=True)
    
    priority_score = Column(Float, default=0.0)
    freshness_score = Column(Float, default=0.0)
    confirmation_status = Column(String, default="CONFIRMED")