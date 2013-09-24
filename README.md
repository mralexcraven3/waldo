waldo
=====

Waldo is a proxy server that routes web traffic through other proxy servers. 


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
