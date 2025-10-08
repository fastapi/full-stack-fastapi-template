from .unixconn import UnixHTTPAdapter

try:
    from .npipeconn import NpipeHTTPAdapter
    from .npipesocket import NpipeSocket
except ImportError:
    pass

try:
    from .sshconn import SSHHTTPAdapter
except ImportError:
    pass
