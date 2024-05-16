from aiohttp.web import (
    Application as AiohttpApplication,
    View as AiohttpView,
    Request as AiohttpRequest,
)
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.web.config import setup_config, Config
from app.web.logger import setup_logging
from app.web.middlewares import setup_middlewares
from app.store import setup_store, Store, Database
from app.user.dataclasses import UserDC
import aiohttp_cors
from aiohttp_session import setup as session_setup
from app.web.routes import register_urls


class Application(AiohttpApplication):
    config: Config | None
    store: Store | None
    database: Database | None


class Request(AiohttpRequest):
    user: UserDC | None = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def database(self):
        return self.request.app.database

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


app = Application()


def setup_app(config_path: str) -> Application:
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )
    setup_config(app=app, config_path=config_path)
    setup_logging(app)
    session_setup(
        app,
        EncryptedCookieStorage(
            app.config.session.key,
            domain="navigate_bmstu.ru",
        ),
    )
    setup_middlewares(app)
    setup_aiohttp_apispec(app)
    register_urls(app, cors)
    setup_store(app=app)
    return app
