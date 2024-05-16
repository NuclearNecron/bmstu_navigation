from app.web.app import Application

from app.map.views import ConnectionView, NodeView, NavigateView, TypeView, StartView


def register_urls(application: Application):

    application.router.add_view("/map/conn/", ConnectionView)
    application.router.add_view("/map/conn/{conn_id}", ConnectionView)
    application.router.add_view("/map/node/", NodeView)
    application.router.add_view("/map/node/{node_id}", NodeView)
    application.router.add_view("/map/type/", TypeView)
    application.router.add_view("/map/type/{type_id}", TypeView)
    application.router.add_view("/map/navigate", NavigateView)
    application.router.add_view("/map/start", StartView)
