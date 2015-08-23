# Finders

When crawling a large website, one often has to pull proxies together from
various proxy lists. I've taken a simple approach to this and have a construct
called a proxy `Finder`. Finders live in the `finders` directory.

Finders must implement the `get_all` method, as this is how Waldo pulls the
list of proxies from it.

Currently, we use two proxy finders -- one is from ProxySpy, the other is to
pull proxies from a flatfile.
