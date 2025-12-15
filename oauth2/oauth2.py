from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from models import models
from schemas.schemas import TokenPayload
from settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire: datetime | float = datetime.now() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded: str = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded


def verify_access_token(
    token: str, credential_exception
) -> TokenPayload:
    try:
        payload: dict = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        id = payload.get("user_id")
        if not id:
            raise credential_exception
        return TokenPayload(sub=id)
    except JWTError:
        raise credential_exception


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> models.User:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unathorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credential_exception)
    result = await db.execute(
        select(models.User).where(models.User.id == token_data.sub)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise credential_exception
    return user  # type: ignore
