from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.api.src.schemas.token import TokenCreate, TokenResponse
from apps.common.database import get_db
from apps.common.models.token import Token


router = APIRouter(
    prefix="/tokens",
    tags=["Tokens"]
)


@router.post("/", response_model=TokenResponse)
def create_token(
    token: TokenCreate,
    db: Session = Depends(get_db)
):

    existing_token = (
        db.query(Token)
        .filter(Token.address == token.address)
        .first()
    )

    if existing_token:
        raise HTTPException(
            status_code=409,
            detail="Token já cadastrado"
        )

    db_token = Token(
        **token.model_dump()
    )

    try:
        db.add(db_token)
        db.commit()
        db.refresh(db_token)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Token já cadastrado"
        )

    return db_token



@router.get("/", response_model=list[TokenResponse])
def list_tokens(
    db: Session = Depends(get_db)
):
    return db.query(Token).all()


@router.get("/{address}", response_model=TokenResponse)
def get_token(
    address: str,
    db: Session = Depends(get_db)
):
    token = db.query(Token).filter(Token.address == address).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return token


@router.get("/{address}/snapshots")
def get_token_snapshots(
    address: str,
    db: Session = Depends(get_db)
):
    from apps.common.models.token_snapshot import TokenSnapshot
    
    snapshots = db.query(TokenSnapshot).filter(
        TokenSnapshot.token_address == address
    ).order_by(TokenSnapshot.timestamp.asc()).all()
    
    return [
        {
            "timestamp": s.timestamp.isoformat(),
            "price_usd": s.price_usd,
            "market_cap": s.market_cap,
            "liquidity": s.liquidity,
            "volume_24h": s.volume_24h,
            "buys": s.buys,
            "sells": s.sells
        }
        for s in snapshots
    ]