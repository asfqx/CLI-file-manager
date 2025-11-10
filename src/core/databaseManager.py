from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Any, TypeVar, overload
from src.core.config import config
from sqlalchemy.engine import CursorResult, Result
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from sqlalchemy.sql.base import Executable
from sqlalchemy.sql.dml import UpdateBase
from sqlalchemy.sql.selectable import TypedReturnsRows


_T = TypeVar("_T", bound=Any)


class DatabaseAccessor:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker | None = None
        self._current_session: ContextVar[AsyncSession | None] = ContextVar(
            "current_session", default=None
        )

    async def connect(self):
        if self._engine is None:
            self._engine = create_async_engine(
                url=config.database.url,
                echo=True,
            )
        if self._session_maker is None:
            self._session_maker = async_sessionmaker(
                autocommit=False,
                bind=self._engine,
                autoflush=False,
                expire_on_commit=False,
            )

    async def disconnect(self):
        if self._engine is None:
            return

        await self._engine.dispose()
        self._engine = None

    @property
    def session_maker(self) -> async_sessionmaker:
        if self._session_maker is None:
            raise RuntimeError("DatabaseAccessor is not connected")

        return self._session_maker

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        scoped_session = async_scoped_session(
            session_factory=self.session_maker,
            scoped_session=current_task,
        )

        async with scoped_session() as session:
            token = self._current_session.set(session)

            yield session
            await session.commit()

            self._current_session.reset(token)
            await scoped_session.remove()

    def get_current_session(self) -> AsyncSession | None:
        return self._current_session.get()

    @overload
    async def execute(
        self,
        statement: TypedReturnsRows[_T],
    ) -> Result[_T]: ...

    @overload
    async def execute(
        self,
        statement: UpdateBase,
    ) -> CursorResult[Any]: ...

    @overload
    async def execute(
        self,
        statement: Executable,
    ) -> Result[Any]: ...

    async def execute(
        self,
        statement: Executable,
    ) -> Result[Any]:
        session = self.get_current_session()

        if session:
            return await session.execute(statement)

        async with self.session() as session:
            return await session.execute(statement)
