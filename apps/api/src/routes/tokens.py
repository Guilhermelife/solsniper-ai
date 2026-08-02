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