import queue

import requests.adapters
import urllib3
import urllib3.connection

from .. import constants
from .basehttpadapter import BaseHTTPAdapter
from .npipesocket import NpipeSocket

RecentlyUsedContainer = urllib3._collections.RecentlyUsedContainer


class NpipeHTTPConnection(urllib3.connection.HTTPConnection):
    def __init__(self, npipe_path, timeout=60):
        super().__init__(
            'localhost', timeout=timeout
        )
        self.npipe_path = npipe_path
        self.timeout = timeout

    def connect(self):
        sock = NpipeSocket()
        sock.settimeout(self.timeout)
        sock.connect(self.npipe_path)
        self.sock = sock


class NpipeHTTPConnectionPool(urllib3.connectionpool.HTTPConnectionPool):
    def __init__(self, npipe_path, timeout=60, maxsize=10):
        super().__init__(
            'localhost', timeout=timeout, maxsize=maxsize
        )
        self.npipe_path = npipe_path
        self.timeout = timeout

    def _new_conn(self):
        return NpipeHTTPConnection(
            self.npipe_path, self.timeout
        )

    # When re-using connections, urllib3 tries to call select() on our
    # NpipeSocket instance, causing a crash. To circumvent this, we override
    # _get_conn, where that check happens.
    def _get_conn(self, timeout):
        conn = None
        try:
            conn = self.pool.get(block=self.block, timeout=timeout)
        except AttributeError as ae:  # self.pool is None
            raise urllib3.exceptions.ClosedPoolError(self, "Pool is closed.") from ae

        except queue.Empty:
            if self.block:
                raise urllib3.exceptions.EmptyPoolError(
                    self,
                    "Pool reached maximum size and no more "
                    "connections are allowed."
                ) from None
            # Oh well, we'll create a new connection then

        return conn or self._new_conn()


class NpipeHTTPAdapter(BaseHTTPAdapter):

    __attrs__ = requests.adapters.HTTPAdapter.__attrs__ + ['npipe_path',
                                                           'pools',
                                                           'timeout',
                                                           'max_pool_size']

    def __init__(self, base_url, timeout=60,
                 pool_connections=constants.DEFAULT_NUM_POOLS,
                 max_pool_size=constants.DEFAULT_MAX_POOL_SIZE):
        self.npipe_path = base_url.replace('npipe://', '')
        self.timeout = timeout
        self.max_pool_size = max_pool_size
        self.pools = RecentlyUsedContainer(
            pool_connections, dispose_func=lambda p: p.close()
        )
        super().__init__()

    def get_connection(self, url, proxies=None):
        with self.pools.lock:
            pool = self.pools.get(url)
            if pool:
                return pool

            pool = NpipeHTTPConnectionPool(
                self.npipe_path, self.timeout,
                maxsize=self.max_pool_size
            )
            self.pools[url] = pool

        return pool

    def request_url(self, request, proxies):
        # The select_proxy utility in requests errors out when the provided URL
        # doesn't have a hostname, like is the case when using a UNIX socket.
        # Since proxies are an irrelevant notion in the case of UNIX sockets
        # anyway, we simply return the path URL directly.
        # See also: https://github.com/docker/docker-sdk-python/issues/811
        return request.path_url
