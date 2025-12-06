"""This module contains the models for the users module"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from modules.db.database import Base
from models import GwscwmBase
from passlib.context import CryptContext
from pydantic import computed_field


# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """User model representing a user in the system"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    firstname: Mapped[str] = mapped_column(String(50), nullable=True)
    lastname: Mapped[str] = mapped_column(String(50), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)


class UserBase(GwscwmBase):
    """Base class for User model with common attributes"""

    id: int
    username: str
    email: str
    firstname: str
    lastname: str


class UserCreate(UserBase):
    """Model for creating a new user"""

    password: str

    @computed_field
    def hashed_password(self) -> str:
        """Compute and return the bcrypt hash for the provided password.

        This is a read-only computed field derived from `password` and
        will be included when the model is serialized.
        """
        return pwd_context.hash(self.password)


class UserUpdate(UserBase):
    """Model for updating an existing user"""

    is_active: bool
    is_superuser: bool


class UserLogin(GwscwmBase):
    """Model for user login"""

    username: str
    password: str