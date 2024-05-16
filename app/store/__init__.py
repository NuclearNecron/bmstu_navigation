import typing
from app.store.database.database import Database
from app.store.user import UserAccessor
from app.store.map import MapAccessor, Update_Handler
from app.map_module.mapper import Map


if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        self.userAPI = UserAccessor(app)
        self.mapAPI = MapAccessor(app)
        self.updater = Update_Handler(app)
        self.map = Map(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
