import requests.adapters


class BaseHTTPAdapter(requests.adapters.HTTPAdapter):
    def close(self):
        super().close()
        if hasattr(self, 'pools'):
            self.pools.clear()

    # Fix for requests 2.32.2+:
    # https://github.com/psf/requests/commit/c98e4d133ef29c46a9b68cd783087218a8075e05
    def get_connection_with_tls_context(self, request, verify, proxies=None, cert=None):
        return self.get_connection(request.url, proxies)
