import urlparse
from collections import namedtuple
import datetime


Record = namedtuple('Record', ['requested_at', 'outcome'])


class Proxy:
    def __init__(self, host, port, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        # use these attributes to keep track of how the proxy has performed.
        self.successes = 0
        self.failures = 0
        self.history = []

    def __hash__(self):
        return hash("%s:%s:%s:%s" % (self.host, self.port, self.username,
            self.password))

    def __lt__(self, other):
        return self.score() < other.score()

    def score(self):
        return (1.0 + self.successes) / (1.0 + self.successes + self.failures)

    def mark_success(self):
        self.successes += 1
        self.history.append(Record(requested_at=datetime.datetime.now(),
            outcome=1))

    def mark_failure(self):
        self.failures += 1
        self.history.append(Record(requested_at=datetime.datetime.now(),
            outcome=0))

    @property
    def connection_attrs(self):
        d = {
            'proxy_host': self.host,
            'proxy_port': int(self.port)
        }
        if self.username:
            d['proxy_username'] = self.username
        if self.password:
            d['proxy_password'] = self.password
        return d
