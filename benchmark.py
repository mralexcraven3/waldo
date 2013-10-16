import gevent
from gevent import monkey; monkey.patch_all()
import time, random
import urllib2

waldo_proxy = urllib2.ProxyHandler({'http': 'http://localhost:1234'})
waldo_opener = urllib2.build_opener(waldo_proxy)

def make_request(index):
    time.sleep(random.randint(1,3))
    url = "http://whatismyip.com"
    req = urllib2.Request(url)
    response = waldo_opener.open(req)
    data = response.read()
    print "%s: %s" % (index, len(data))

jobs = [gevent.spawn(make_request, i) for i in range(100)]
gevent.joinall(jobs)
