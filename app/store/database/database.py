from typing import TYPE_CHECKING, Callable

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.base import db

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: AsyncEngine | None = None
        self._db: declarative_base | None = None
        self.session: [Callable[[], AsyncSession]] | None = None

    async def connect(self, *_: list, **__: dict) -> None:
        self._db = db
        self._engine = create_async_engine(
            f"postgresql+asyncpg://{self.app.config.database.user}:{self.app.config.database.password}@{self.app.config.database.host}:{self.app.config.database.port}/{self.app.config.database.database}",
            echo=True,
            future=True,
        )
        self.session = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    async def disconnect(self, *_: list, **__: dict) -> None:
        if self.session:
            self.session = None
        if self._engine:
            await self._engine.dispose()
