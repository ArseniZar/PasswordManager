from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, LargeBinary
from flask_login import UserMixin
from .passwords import Passwords
from ..exstesions import db, login_manager 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    encryption_salt: Mapped[bytes] = mapped_column(LargeBinary(16), nullable=False)

    passwords: Mapped[List["Passwords"]] = relationship("Passwords", back_populates="user", cascade="all, delete-orphan")
    
    
