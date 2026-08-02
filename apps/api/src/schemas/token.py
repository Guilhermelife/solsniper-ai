from datetime import datetime
from pydantic import BaseModel


class TokenCreate(BaseModel):
    address: str
    symbol: str
    name: str
    liquidity: float
    volume_24h: float
    risk_score: float


class TokenResponse(BaseModel):
    id: int
    address: str
    symbol: str
    name: str
    liquidity: float
    volume_24h: float
    risk_score: float
    created_at: datetime


    class Config:
        from_attributes = True