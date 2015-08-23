# waldo

Waldo is a proxy server that routes web traffic through other proxy servers. It's
basically a meta-proxy server that tries to best route your traffic so that you
do not get blocked.

## Motivation

Large scale web crawling can be difficult if you're crawling a single website.
Most sites will block you before long, so you'll have to write some logic to
pull a list of available proxy servers, handle connection pooling across those proxies,
and keep track of which proxies are still alive, and which are no longer responding to
your requests.

I found myself constantly re-writing this code in various projects to manage outbound
proxying. This process, while necessary, got a little bit tedious, so I
decided to factor out the proxying logic into a separate proxy server to handle the load
balancing.

![How it works](https://github.com/omarish/waldo/blob/master/doc/Graphics/How-It-Works.png)

## Advantages

### Concurrency

Waldo is written with Tornado, which is a highly scalable web server. I've been
able to handle ~ 1,000 concurrent connections with Waldo, and I suspect it can
handle significantly more than that.

### Coordination

With a sufficiently large proxy list, keeping track of proxies becomes difficult.
Proxies often die, or need to be put in a "cool off" box so that they don't get
burnt out from too much traffic. Waldo handles all of this for you.

### Simplicity

Waldo implements the standard HTTP Proxy spec, so just connect it to it like you
would any other proxy server, and it'll handle the rest for you.

### Diverse Proxies

When crawling a large website, you'll often find yourself stitching together various
proxy server lists. Waldo has the concept of a `Finder`, which is basically a class
that pulls in a list of proxy servers for you.

## Setup

First, make sure redis is installed. Then, install the python dependencies:

```bash
pip install -r requirements.txt
```

## Run

To run the server:

```bash
$ python server.py --port=1234
```

By default, waldo listens on port 1234 on all network interfaces.

To make sure it's working, try this:

```bash
$ curl -XGET http://omarish.com -x http://localhost:1234
```

## Stats Monitor

![Stats Monitor](https://github.com/omarish/waldo/blob/master/doc/Graphics/Stats-Page.png)

To run the accompanying monitoring page, run the monitoring server:

```bash
$ python monitor.py
```

The monitoring page by default listens on port 1235.

## Testing and Benchmarking

I've been using a benchmarking utility
in `benchmark.py` to will simulate heavy requests. Additionally,
[Apache Bench](http://httpd.apache.org/docs/2.2/programs/ab.html)
and [Siege](https://www.joedog.org/siege-home/) have been very helpful.  

To run the benchmarking script:

```bash
$ python benchmark.py
```
