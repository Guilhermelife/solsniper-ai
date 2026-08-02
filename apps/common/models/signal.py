from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

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

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )