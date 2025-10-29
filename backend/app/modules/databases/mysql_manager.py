"""Class for the MySQL manager"""
from __future__ import annotations

import os
from typing import AsyncIterator, Optional
from urllib.parse import quote_plus

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel


class MysqlManager:
    """Async Database wrapper for SQLModel + MySQL (via aiomysql or asyncmy)."""

    def __init__(
        self,
        *,
        user: str,
        password: str,
        host: str,
        port: int,
        database: str,
        driver: str = "aiomysql",   # or "asyncmy"
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 10,
        pool_pre_ping: bool = True,
        pool_recycle: int = 1800,
        # Whether to perform an explicit test (SELECT 1) on startup after connecting
        test_on_startup: bool = True,
        # DBAPI-level connect timeout in seconds (passed via connect_args)
        connect_timeout: int = 5,
    ) -> None:
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.driver = driver

        self.echo = echo
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_pre_ping = pool_pre_ping
        self.pool_recycle = pool_recycle
        self.test_on_startup = test_on_startup
        self.connect_timeout = connect_timeout

        self._engine: Optional[AsyncEngine] = None
        self._session_maker: Optional[sessionmaker] = None

    @classmethod
    def from_env(
        cls,
        *,
        user_env="MYSQL_USER",
        password_env="MYSQL_PASSWORD",
        host_env="MYSQL_HOST",
        port_env="MYSQL_PORT",
        db_env="MYSQL_DATABASE",
        driver_env="MYSQL_DRIVER",  # "aiomysql" or "asyncmy"
    ) -> "MysqlManager":
        return cls(
            user=os.getenv(user_env, "root"),
            password=os.getenv(password_env, ""),
            host=os.getenv(host_env, "localhost"),
            port=int(os.getenv(port_env, "3306")),
            database=os.getenv(db_env, "app"),
            driver=os.getenv(driver_env, "aiomysql"),
            echo=bool(int(os.getenv("SQL_ECHO", "0"))),
            pool_size=int(os.getenv("SQL_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("SQL_MAX_OVERFLOW", "10")),
            pool_recycle=int(os.getenv("SQL_POOL_RECYCLE", "1800")),
            test_on_startup=bool(int(os.getenv("SQL_TEST_ON_STARTUP", "1"))),
            connect_timeout=int(os.getenv("SQL_CONNECT_TIMEOUT", "5")),
        )

    def url(self) -> str:
        pw = quote_plus(self.password or "")
        return f"mysql+{self.driver}://{self.user}:{pw}@{self.host}:{self.port}/{self.database}"

    async def connect(self) -> None:
        if self._engine is not None:
            return
        self._engine = create_async_engine(
            self.url(),
            echo=self.echo,
            pool_pre_ping=self.pool_pre_ping,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_recycle=self.pool_recycle,
            # pass connect args to the underlying DBAPI so connection attempts
            # will time out predictably during startup checks
            connect_args={"connect_timeout": self.connect_timeout},
            future=True,
        )
        self._session_maker = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    async def startup(self) -> None:
        """Create the engine and optionally perform a test query to verify the DB is reachable.

        Raises:
            RuntimeError: if test_on_startup is True and the test query fails.
        """
        await self.connect()
        if self.test_on_startup:
            ok = await self.ping()
            if not ok:
                # ensure we clean up the engine if the ping fails
                await self.disconnect()
                raise RuntimeError("Database startup ping failed: cannot reach MySQL server")

    async def disconnect(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_maker = None

    async def shutdown(self) -> None:
        """Gracefully dispose of the engine and session maker."""
        await self.disconnect()

    async def ping(self) -> bool:
        if self._engine is None:
            await self.connect()
        assert self._engine is not None
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except OperationalError:
            return False

    async def create_all(self) -> None:
        assert self._engine is not None, "Call connect() first."
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_maker is None:
            await self.connect()
        assert self._session_maker is not None
        async with self._session_maker() as s:
            yield s
