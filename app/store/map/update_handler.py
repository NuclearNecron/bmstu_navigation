from typing import Optional, TYPE_CHECKING

from app.base import BaseAccessor
from app.store.map.updater import Handler


if TYPE_CHECKING:
    from app.web.app import Application


class Update_Handler(BaseAccessor):
    def __int__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.updater: Optional[Handler] = None

    async def connect(self, app: "Application"):
        self.updater = Handler(self.app)
        await self.updater.start()

    async def disconnect(self, app: "Application"):
        await self.updater.stop()
