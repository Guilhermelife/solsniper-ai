from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Boolean, Index

from apps.common.database import Base


class Signal(Base):

    __tablename__ = "signals"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # FIX-26: Added index=True to token_address for query performance
    token_address = Column(
        String,
        nullable=False,
        index=True
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

    # FIX-01: Added updated_at field (was referenced in main.py but didn't exist)
    updated_at = Column(
        DateTime,
        nullable=True,
        onupdate=datetime.utcnow
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

    time_to_10_pct = Column(Float, nullable=True)  # minutes
    time_to_20_pct = Column(Float, nullable=True)
    time_to_50_pct = Column(Float, nullable=True)
    time_to_100_pct = Column(Float, nullable=True)

    priority_score = Column(Float, default=0.0)
    freshness_score = Column(Float, default=0.0)

    # FIX-14: Default changed from "CONFIRMED" to "DETECTED"
    confirmation_status = Column(String, default="DETECTED")