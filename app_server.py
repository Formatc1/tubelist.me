import os
import tubelist.settings
import tubelist.wsgi
import tornado.web
import tornado.wsgi
from playlists.web_socket_handler import WebSocketHandler


class Application(tornado.web.Application):
    """
    Tornado application which serves our Django application.
    Tornado handles staticfiles and web sockets, Django handles everything else.
    """

    def __init__(self):
        settings = dict()
        settings["debug"] = True if tubelist.settings.DEBUG else False

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tubelist.settings")
        wsgi_app = tornado.wsgi.WSGIContainer(tubelist.wsgi.application)
        static_path = tubelist.settings.STATIC_ROOT

        handlers = [
            (r"/ws/(\d*)", WebSocketHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': static_path}),
            (r".*", tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ]

        tornado.web.Application.__init__(self, handlers, **settings)


# class WebSocketHandler(tornado.websocket.WebSocketHandler):
#     def data_received(self, chunk):
#         # Don't do anything for now
#         pass

#     def open(self, room=0):
#         if room in USERS:
#             USERS[room].append(self)
#         else:
#             USERS[room] = [self]
#         for client in USERS[room]:
#             client.write_message(u"new client connected to room %s" % room)
#         # self.write_message(u"ws-echo: 418 I'm a teapot (as per RFC 2324) %s" % room)

#     def on_message(self, message):
#         active_users = [client for client in USERS.values() if self in client]
#         for user in active_users[0]:
#             user.write_message(u"ws-echo: %s" % message)
#         # self.write_message(u"ws-echo: " + message)

#     def check_origin(self, origin):
#         return True
