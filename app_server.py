"""
Module for application server.
"""

import os
import tubelist.settings
import tubelist.wsgi
import tornado.web
import tornado.wsgi
from playlists.web_socket_handler import WebSocketHandler


class Application(tornado.web.Application):

    """
    Tornado application which serves our Django application.
    Tornado handles staticfiles and web sockets,
    Django handles everything else.
    """

    def __init__(self):
        debug = True if tubelist.settings.DEBUG else False

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tubelist.settings")
        wsgi_app = tornado.wsgi.WSGIContainer(tubelist.wsgi.application)
        static_path = tubelist.settings.STATIC_ROOT

        handlers = [
            (r"/ws/(\d*)", WebSocketHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler,
                {'path': static_path}),
            (r".*", tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ]

        tornado.web.Application.__init__(self, handlers, debug=debug)
