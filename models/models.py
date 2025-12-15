from typing import List
from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False
    )
    urls: Mapped[List["Urls"]] = relationship(
        "Urls", back_populates="user"
    )


class LongUrls(Base):
    __tablename__ = "long_url"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    short: Mapped["Urls"] = relationship(
        "Urls", back_populates="long"
    )


class Urls(Base):
    __tablename__ = "short_url"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    full_url_id: Mapped[int] = mapped_column(
        ForeignKey("long_url.id", ondelete="CASCADE"), nullable=True
    )
    short_url: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    user: Mapped["User"] = relationship("User", back_populates="urls")
    long: Mapped["LongUrls"] = relationship(
        "LongUrls", back_populates="short"
    )
