from proxy import Proxy
import urllib2
import re

class ProxySpy:
    def is_valid_proxy(self, x):
        """ProxySpy has a special way of describing proxies:

        IP:Port Country-Anonymity(Noa/Anm/Hia)-SSL_support(S)-Google_passed(+)

        We only want proxies that are Google_passed, meaning they can reach
        google.com and are not blocked. ProxySpy denotes this with a trailing
        plus sign, and (sometimes) whitespace.
        """
        return re.search('\+\s?$', x) is not None

    def parse_proxy(self, x):
        """Given a proxy string, convert it into a proxy object. 

        A proxy string from ProxySpy looks like this:

        89.108.87.203:8118 RU-H! -"""
        host, port = x.split(' ')[0].split(':')
        return Proxy(host=host, port=int(port))

    def get_all(self):
        response = urllib2.urlopen("http://txt.proxyspy.net/proxy.txt")
        if response.getcode() == 200:
            is_proxy = lambda x: re.search(r'^\d', x.strip()) is not None
            # Remove comment lines that are not proxy servers.
            proxies = filter(is_proxy, response.read().splitlines())
            return [self.parse_proxy(x) for x in proxies if 
                    self.is_valid_proxy(x)]
        else:
            raise Exception("ProxySpy Finder returned a non-200 status code: %s" 
                    % response.getcode())
