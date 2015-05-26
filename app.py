#!/bin/env python

import os
import sys
import tornado.httpserver
import tornado.ioloop
import tornado.options

import app_server as app


# Return the libs path (this path is appended to module search path/sys.path).
def get_libs_path():
    zpath = os.getenv("OPENSHIFT_REPO_DIR")
    zpath = zpath if zpath else "./"
    return os.path.abspath(os.path.join(zpath, "libs"))


# Return the interface we need to bind to.
def get_bind_interface():
    ipaddr = os.getenv("OPENSHIFT_PYTHON_IP")
    return ipaddr if ipaddr else "127.0.0.1"


def get_bind_interface_port():
    port = os.getenv("OPENSHIFT_PYTHON_PORT")
    try:
        port = int(port)
    except TypeError:
        port = 8080
    return port


# Server main.
def start_tornado():
    # Tornado server address and port number.
    tornado.options.define("address", default=get_bind_interface(),
                           help="network address/interface to bind to")
    tornado.options.define("port", default=get_bind_interface_port(),
                           help="port number to bind to", type=int)
    tornado.options.parse_command_line()

    zoptions = tornado.options.options
    zserver = tornado.httpserver.HTTPServer(app.Application())
    zserver.listen(zoptions.port, zoptions.address)
    tornado.ioloop.IOLoop.instance().start()


#
# __main__:  main code.
#
if __name__ == "__main__":
    sys.path.append(get_libs_path())
    start_tornado()

