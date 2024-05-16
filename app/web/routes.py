import typing
from aiohttp.web_app import Application
from aiohttp_cors import CorsConfig


__all__ = ("register_urls",)


def register_urls(application: Application, cors: CorsConfig):
    from app.map.routes import register_urls as map_urls

    map_urls(application)

    from app.user.routes import register_urls as user_urls

    user_urls(application)
    for route in list(application.router.routes()):
        cors.add(route)
