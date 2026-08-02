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


    liquidity: Mapped[float] = mapped_column(
        Float,
        default=0
    )


    volume_24h: Mapped[float] = mapped_column(
        Float,
        default=0
    )


    risk_score: Mapped[float] = mapped_column(
        Float,
        default=0
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    