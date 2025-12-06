"""This module contains the common and base models for the application."""

from datetime import datetime, timedelta, timezone
from modules.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, event
from typing import ClassVar
from pydantic import ConfigDict, SecretStr
from pydantic import BaseModel

class TimeStampMixin(object):
    """Timestamping mixing for created_at and updated_at fields"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @staticmethod 
    def _updated_at(mapper, connection, target):
        """Set updated_at to current time plus one second"""
        target.updated_at = datetime.now(timezone.utc) + timedelta(seconds=1)

    @classmethod 
    def __declare_last__(cls):
        event.listen(cls, 'before_update', cls._updated_at)

class GwscwmBase(BaseModel):
    """Base Pydantic model with shared config for Dispatch models."""
    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        json_encoders={
            # custom output conversion for datetime
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if v else None,
            SecretStr: lambda v: v.get_secret_value() if v else None,
        },
    )


class Pagination(GwscwmBase):
    """Pydantic model for paginated results"""
    page_size: int
    page: int
    total: int

