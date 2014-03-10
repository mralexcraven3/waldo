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
import tornado.gen
import logging
logger = logging.getLogger(__name__)

tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

source_url = "http://ec2-204-236-128-163.us-west-1.compute.amazonaws.com:1234"
pth = lambda x: os.path.join(os.path.dirname(__file__), x)


define("debug", default=False, type=bool, help="debug mode?")
define("port", default=12345, type=int, help="which port?")
define("user_agents", default="user_agents.txt", type=str,
       help="list of user agents.")
define("loglevel", default='INFO', type=str, help='logging level')
define("warmup", default=False, type=bool, help="warmup server?")


def parse_proxy(p):
    """Parse a proxy into its component parts.

    This should eventually use httplib to support usernames and passwords.

    >>> resp = parse_proxy('127.0.0.1:1234')
    >>> resp['proxy_host']
    '127.0.0.1'
    >>> resp['proxy_port']
    1234
    """
    _p = p.split(':')
    # curl_httpclient requires proxy_host to be a string
    return dict(
        proxy_host=str(_p[0]),
        proxy_port=int(_p[1])
    )


class ProxyServer(HTTPServer):

    supported_headers = (
        'Waldo-Timeout',
        'Waldo-Max-Retries',
        'Waldo-Must-Complete'
    )

    http_client = tornado.httpclient.AsyncHTTPClient()
    blocking_http_client = tornado.httpclient.HTTPClient()
    last_proxy_update = D.datetime(year=1970, month=1, day=1)

    max_connections = 20
    active_connections = 0

    successes = 0
    failures = 0

    def __init__(self, *args, **kwargs):
        self.application = None
        self.user_agents = self._get_user_agents()
        self.refresh_proxies()
        super(ProxyServer, self).__init__(self.handle_request, **kwargs)

    def _get_user_agents(self, fname=pth("user_agents.txt")):
        with open(fname, 'r') as f:
            return f.readlines()

    def refresh_proxies(self, source_url=source_url):
        logging.info("Fetching proxy list")
        while 1:
            try:
                response = self.blocking_http_client.fetch(source_url)
                logging.info("Fetched proxy list.")
                values = map(parse_proxy, json.loads(response.body)['values'])
            except Exception, e:
                print "Exception ", e
                time.sleep(10)
            else:
                self.proxies = SmartHat(values)
                self.last_proxy_update = D.datetime.now()
                break

    def needs_proxy_refresh(self):
        return D.datetime.now() > (self.last_proxy_update +
                D.timedelta(seconds=86400))

    def get_proxy(self):
        if self.needs_proxy_refresh():
            print "Refresh proxies"
            self.refresh_proxies()
        return self.proxies.pop()

    def feign_user_agent(self):
        return random.choice(self.user_agents)

    @tornado.gen.engine
    def handle_request(self, request):
        request.headers['User-Agent'] = self.feign_user_agent()
        try:
            request_timeout = int(request.headers.get('Waldo-Timeout', 5))
        except ValueError:
            request_timeout = 5

        try:
            max_retries = int(request.headers.get('Waldo-Max-Retries', 10))
        except ValueError:
            max_retries = 10

        try:
            must_succeed = int(request.headers.get('Waldo-Must-Complete', '0'))
        except ValueError:
            must_succeed = 0
        finally:
            if must_succeed > 0:
                max_retries = 100

        # Remove Waldo HTTP headers
        for header in self.supported_headers:
            try:
                del request.headers[header]
            except:
                pass

        success, tries = False, max_retries
        while not success and tries > 0:
            try:
                proxy = self.get_proxy()
                response = yield self.http_client.fetch(request.uri,
                                                        headers=request.headers,
                                                        request_timeout=request_timeout,
                                                        **proxy.obj)
            except tornado.httpclient.HTTPError as e:
                logging.error(e)
                if e.code in (400, 404, 599):
                    # wtf pycurl
                    status_code = e.code
                    if e.code == 599:
                        status_code = 404
                proxy.fail()
                tries -= 1
                self.failures += 1
            except:
                print "Strange http bug."
                proxy.fail()
                self.failures += 1
            else:
                self.successes += 1
                proxy.success()
                success = True

            finally:
                try:
                    self.proxies.push(proxy)
                except:
                    print "Something is going on."
                if self.successes + self.failures > 0:
                    ratio = 100 * float(self.successes) / (self.successes + self.failures)
                    logging.info("%s / %s  - (%.2f%% success) - %s" % (
                        self.successes,
                        self.successes + self.failures,
                        ratio,
                        len(self.proxies)))

        if not success:
            # HTTP 417 is not to be confused with HTTP 418.
            msg = "Too many retries for %s." % request.uri
            request.write("HTTP/1.1 %s\r\nContent-Length: %d\r\n\r\n%s" %
                          (status_code, len(msg), msg))
            logging.info("%s failed" % request.uri)
        else:
            # logging.info("Success: %s" % request.uri)
            request.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%s" %
                          (len(response.body), response.body))
        request.finish()


if __name__ == '__main__':
    io_loop = tornado.ioloop.IOLoop.instance()
    http_server = ProxyServer(io_loop=io_loop)
    parse_command_line()
    http_server.listen(options.port)
    logging.basicConfig(level=getattr(logging, options.loglevel))
    io_loop.start()
