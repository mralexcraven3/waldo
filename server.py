#!/usr/bin/env python

import random
import os
import datetime as D
import ujson as json
from smarthat import SmartHat
import time
import tornado.options
import tornado.httpclient
from tornado.options import define, options, parse_command_line
from tornado.httpserver import HTTPServer
from collections import deque
import tornado.gen
import logging
logger = logging.getLogger(__name__)
from finders.flatfile import FlatfileFinder


tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

define("debug", default=False, type=bool, help="debug mode?")
define("port", default=1234, type=int, help="expose waldo on which port?")
# define("user_agents", default="user_agents.txt", type=str,
#       help="list of user agents.")
define("loglevel", default='INFO', type=str, help='logging level')

pth = lambda x: os.path.join(os.path.dirname(__file__), x)

class ProxyServer(HTTPServer):
    supported_headers = (
        'Waldo-Timeout',
        'Waldo-Max-Retries',
        'Waldo-Must-Complete'
    )
    http_client = tornado.httpclient.AsyncHTTPClient()
    fatal_error_codes = (502, 503, 407, 403, 599)

    def __init__(self, *args, **kwargs):
        self.user_agents = open(pth('user_agents.txt')).readlines()
        self.debug = kwargs.pop("debug", False)
        self.proxies = SmartHat(self.get_proxies())
        self.history = deque(maxlen=20)
        super(ProxyServer, self).__init__(self.handle_request, **kwargs)

    def get_proxies(self, finders=[FlatfileFinder]):
        proxies = set()
        for finder in finders:
            new_proxies = finder().get_all()
            proxies.update(new_proxies)
            logging.info("%s discovered %s proxies." % (finder.__name__,
                len(new_proxies)))
        logging.info("Added %s new proxies." % len(proxies))
        return list(proxies)

    def get_proxy(self):
        return self.proxies.pop()

    def restore_proxy(self, proxy):
        self.proxies.push(proxy)

    @tornado.gen.engine
    def handle_request(self, request):
        if not 'User-Agent' in request.headers:
            request.headers['User-Agent'] = random.choice(self.user_agents)

        success, tries, status_code = False, 10, 200
        while (not success and tries > 0):
            try:
                proxy = self.get_proxy()
                response = yield self.http_client.fetch(request.uri,
                    headers=request.headers,
                    request_timeout=10,
                    **proxy.connection_attrs
                )
            except tornado.httpclient.HTTPError as e:
                logging.error(e)
                status_code = e.code
                tries -= 1
                proxy.mark_failure()
                self.history.append(0)
                if not status_code in self.fatal_error_codes:
                    self.restore_proxy(proxy)
            else:
                logging.info("Success")
                success = True
                proxy.mark_success()
                self.restore_proxy(proxy)
                self.history.append(1)

        if not success:
            # HTTP 417 is not to be confused with HTTP 418.
            status_code = 417
            msg = "Too many retries for %s." % request.uri
            request.write("HTTP/1.1 %s\r\nContent-Length: %d\r\n\r\n%s" %
                          (status_code, len(msg), msg))
            logging.info("%s failed" % request.uri)
        else:
            request.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%s" %
                          (len(response.body), response.body))
        request.finish()


if __name__ == '__main__':
    io_loop = tornado.ioloop.IOLoop.instance()
    parse_command_line()
    http_server = ProxyServer(io_loop=io_loop, debug=options.debug)
    http_server.listen(options.port)
    logging.basicConfig(level=getattr(logging, options.loglevel))
    io_loop.start()
