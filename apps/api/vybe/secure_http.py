"""Outbound HTTP transport without implicit proxies or redirects."""
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def build_secure_opener():
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        NoRedirect(),
    )
