from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from apps.common.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    max_open_positions: Mapped[int] = mapped_column(
        Integer,
        default=5
    )

    initial_balance: Mapped[float] = mapped_column(
        Float,
        default=50.0
    )

    current_balance: Mapped[float] = mapped_column(
        Float,
        default=50.0
    )

    total_profit: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    total_loss: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    total_trades: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    win_rate: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
