from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..exstesions import db

if TYPE_CHECKING:
    from .user import User


class Passwords(db.Model):
    __tablename__ = "passwords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(200), nullable=False)
    login: Mapped[str] = mapped_column(String(100), nullable=False)  # логин от сайта
    password: Mapped[str] = mapped_column(String(200), nullable=False)  # сам пароль
    description: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # описание
    site: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship(back_populates="passwords")
