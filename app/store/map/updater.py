import typing
import asyncio
from asyncio import Task


if typing.TYPE_CHECKING:
    from app.web.app import Application


class Handler:
    def __init__(self, app: "Application"):
        self.app = app
        self.is_running = False
        self.handle_task: Task | None

    async def start(self):
        print("manager init")
        self.is_running = True
        self.handle_task = asyncio.create_task(self.handle_update())

    async def stop(self):
        self.is_running = False
        self.handle_task.cancel()

    async def handle_update(self):
        pass
