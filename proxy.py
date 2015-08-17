import urlparse

class Proxy:
    def __init__(self, host, port, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def __hash__(self):
        return hash("%s:%s:%s:%s" % (self.host, self.port, self.username,
            self.password))
