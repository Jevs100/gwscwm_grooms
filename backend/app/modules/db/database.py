"""MySQL database driver"""

import re
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import declared_attr
from modules.core.config import DATABASE_URL

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create async sessionmaker
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Dependency for FastAPI or similar
@asynccontextmanager
async def get_db():
    """Yields a database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def resolve_table_name(name):
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)  # noqa
    return "_".join([x.lower() for x in names if x])
# Base class for models
class Base(DeclarativeBase):
    """Base class for all database models"""
    
    @declared_attr
    # pylint: disable=no-self-argument
    def __tablename__(cls):
        return resolve_table_name(cls.__name__)

    def dict(self):
        """Returns a dict representation of a model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}