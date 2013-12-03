waldo
=====

Waldo is a proxy server that routes web traffic through other proxy servers. 


## HTTP Headers

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
