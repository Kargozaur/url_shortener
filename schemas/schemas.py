import re
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)
from pydantic_settings import SettingsConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        if not re.search(r"[A-Z]", value):
            raise ValueError("password.uppercase_required")
        if not re.search(r"\d", value):
            raise ValueError("password.number_required")
        if not re.search(r"[!@#$%^&*(),.:<>|?]", value):
            raise ValueError("password.specialized_symbol_required")
        return value


class UserResponse(BaseModel):
    id: int
    name: str

    model_config = SettingsConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: int | None = None
    exp: int | None = None
