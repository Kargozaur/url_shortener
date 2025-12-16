from fastapi import Depends, APIRouter, HTTPException, status
from schemas.schemas import (
    UserCreate,
    TokenPayload,
    Token,
    UserLogin,
    UserResponse,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.models import User
from oauth2.hash_pass import hash_password, verify_password
from oauth2.oauth2 import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signin", response_model=UserResponse)
async def create_user(
    user: UserCreate, db: AsyncSession = Depends(get_db)
):
    query = await db.execute(
        select(User.email).where(User.email == user.email)
    )
    existing_user = query.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    try:
        hashed_passwrod = hash_password(user.password)
        user.password = hashed_passwrod  # type: ignore
        new_user = User(**user.model_dump())
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{Exception}",
        )
    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    user_credential: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    query = await db.execute(
        select(User).where(User.email == user_credential.email)
    )
    user_data = query.scalar_one_or_none()
    fake_hast = "$2b$12$XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    hashed_password = user_data.password if user_data else fake_hast
    if not (
        verify_password(user_credential.password, hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": str(user_data.id), "email": user_data.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}
