from proxy import Proxy

class FlatfileFinder(object):
    def get_all(self):
        def _makeproxy(s):
            r = s.split(':')
            return Proxy(host=r[0], port=r[1])
        with open('finders/proxies.txt') as f:
            return map(_makeproxy, f.readlines())
