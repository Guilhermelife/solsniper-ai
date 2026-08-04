from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.common.database import Base


class Token(Base):
    __tablename__ = "tokens"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )


    address: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True
    )


    symbol: Mapped[str] = mapped_column(
        String
    )


    name: Mapped[str] = mapped_column(
        String
    )

    price_usd: Mapped[float] = mapped_column(Float, default=0)
    fdv: Mapped[float] = mapped_column(Float, default=0)


    liquidity: Mapped[float] = mapped_column(Float, default=0)
    volume_5m: Mapped[float] = mapped_column(Float, default=0)
    volume_1h: Mapped[float] = mapped_column(Float, default=0)
    volume_24h: Mapped[float] = mapped_column(Float, default=0)

    buys_5m: Mapped[int] = mapped_column(Integer, default=0)
    buys_1h: Mapped[int] = mapped_column(Integer, default=0)
    buys_24h: Mapped[int] = mapped_column(Integer, default=0)

    sells_5m: Mapped[int] = mapped_column(Integer, default=0)
    sells_1h: Mapped[int] = mapped_column(Integer, default=0)
    sells_24h: Mapped[int] = mapped_column(Integer, default=0)

    price_change_5m: Mapped[float] = mapped_column(Float, default=0)
    price_change_1h: Mapped[float] = mapped_column(Float, default=0)
    price_change_6h: Mapped[float] = mapped_column(Float, default=0)
    price_change_24h: Mapped[float] = mapped_column(Float, default=0)

    age_minutes: Mapped[float] = mapped_column(Float, nullable=True)

    dex: Mapped[str] = mapped_column(String, nullable=True)
    chain: Mapped[str] = mapped_column(String, nullable=True)
    pair_address: Mapped[str] = mapped_column(String, nullable=True)

    website: Mapped[str] = mapped_column(String, nullable=True)
    twitter: Mapped[str] = mapped_column(String, nullable=True)
    telegram: Mapped[str] = mapped_column(String, nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)

    risk_score: Mapped[float] = mapped_column(Float, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    