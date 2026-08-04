from datetime import date
from sqlalchemy import Date, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from apps.common.database import Base

class DailyWalletSnapshot(Base):
    __tablename__ = "daily_wallet_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    balance: Mapped[float] = mapped_column(Float)
    realized_profit: Mapped[float] = mapped_column(Float, default=0.0)
    unrealized_profit: Mapped[float] = mapped_column(Float, default=0.0)
    open_positions: Mapped[int] = mapped_column(Integer, default=0)
    total_trades: Mapped[int] = mapped_column(Integer, default=0)
