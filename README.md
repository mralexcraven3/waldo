# waldo

Waldo is a proxy server that routes web traffic through other proxy servers.

## Motivation

I found myself constantly re-writing proxy balancing code to manage outbound
proxy servers. This process, while necessary, got a little bit tedious, so I
decided to factor out the proxying logic into a separate meta-proxy server.

[How it works]: Graphics/How-It-Works.png

Waldo's advantges are:

### Concurrency

Waldo is written with Tornado, which is a highly scalable web server. I've been
able to handle ~ 1,000 concurrent connections with Waldo, and I suspect it can
handle significantly more than that.

### Coordination

With a sufficiently large proxy list, keeping track of proxies becomes difficult.
Proxies often die, or need to be put in a "cool off" box so that they don't get
burnt out from too much traffic. Waldo handles all of this for you.

### Simple

Waldo implements the standard HTTP Proxy spec, so just connect it to it like you
would any other proxy server, and it'll handle the rest for you.

## Custom Headers

The following HTTP headers are supported:

`Waldo-Timeout`: Timeout time (in seconds) before an individual HTTP request times out.

`Waldo-Max-Retries`: The maximum number of retries allowed before the proxy fails.

`Waldo-Must-Succeed`: `1` if the request must succeed - else `0`. Currently, `Waldo-Must-Succeed` sets `Waldo-Max-Retries` to `100` retries.

To test, try this:

```bash
curl -x http://localhost:1234/ --header "Waldo-Timeout: 1" --header "Waldo-Max-Retries: 1" --verbose http://omarish.com
```

## Setup

First, install the python dependencies:

```bash
pip install -r requirements.txt
```

## Run

To run the server:

```bash
python -m web.server
```

By default, waldo listens on port 1234 on all network interfaces.

To make sure it's working, try this:

```bash
curl -XGET http://omarish.com -x http://localhost:1234
```

## Doctests

```bash
python -m doctest server.py
```

## TODO

[] Support SOCKS.
[] Smarter proxy balancing.
