from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.common.database import Base


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    token_address: Mapped[str] = mapped_column(
        String,
        index=True
    )

    symbol: Mapped[str] = mapped_column(
        String
    )

    entry_price: Mapped[float] = mapped_column(
        Float
    )

    amount_usd: Mapped[float] = mapped_column(
        Float
    )

    quantity: Mapped[float] = mapped_column(
        Float
    )

    status: Mapped[str] = mapped_column(
        String,
        default="OPEN"
    )

    target_profit: Mapped[float] = mapped_column(
        Float
    )

    stop_loss: Mapped[float] = mapped_column(
        Float
    )

    exit_price: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    profit_loss: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    highest_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lowest_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_roi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_roi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    signal_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    entry_reason: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True
    )

    exit_reason: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True
    )

    trailing_stop_price: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    reentry_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=0,
        nullable=True
    )

    holding_time: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    market_cap: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    liquidity: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    volume_24h: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    age_minutes: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    dex: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True
    )

    buys: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    sells: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    is_win: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
