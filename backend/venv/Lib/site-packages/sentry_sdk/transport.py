from __future__ import print_function

import io
import gzip
import socket
import time
from datetime import timedelta
from collections import defaultdict

import urllib3
import certifi

from sentry_sdk.utils import Dsn, logger, capture_internal_exceptions, json_dumps
from sentry_sdk.worker import BackgroundWorker
from sentry_sdk.envelope import Envelope, Item, PayloadRef
from sentry_sdk._compat import datetime_utcnow
from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    from typing import Any
    from typing import Callable
    from typing import Dict
    from typing import Iterable
    from typing import List
    from typing import Optional
    from typing import Tuple
    from typing import Type
    from typing import Union
    from typing import DefaultDict

    from urllib3.poolmanager import PoolManager
    from urllib3.poolmanager import ProxyManager

    from sentry_sdk._types import Event, EndpointType

    DataCategory = Optional[str]

try:
    from urllib.request import getproxies
except ImportError:
    from urllib import getproxies  # type: ignore


KEEP_ALIVE_SOCKET_OPTIONS = []
for option in [
    (socket.SOL_SOCKET, lambda: getattr(socket, "SO_KEEPALIVE"), 1),  # noqa: B009
    (socket.SOL_TCP, lambda: getattr(socket, "TCP_KEEPIDLE"), 45),  # noqa: B009
    (socket.SOL_TCP, lambda: getattr(socket, "TCP_KEEPINTVL"), 10),  # noqa: B009
    (socket.SOL_TCP, lambda: getattr(socket, "TCP_KEEPCNT"), 6),  # noqa: B009
]:
    try:
        KEEP_ALIVE_SOCKET_OPTIONS.append((option[0], option[1](), option[2]))
    except AttributeError:
        # a specific option might not be available on specific systems,
        # e.g. TCP_KEEPIDLE doesn't exist on macOS
        pass


class Transport(object):
    """Baseclass for all transports.

    A transport is used to send an event to sentry.
    """

    parsed_dsn = None  # type: Optional[Dsn]

    def __init__(
        self, options=None  # type: Optional[Dict[str, Any]]
    ):
        # type: (...) -> None
        self.options = options
        if options and options["dsn"] is not None and options["dsn"]:
            self.parsed_dsn = Dsn(options["dsn"])
        else:
            self.parsed_dsn = None

    def capture_event(
        self, event  # type: Event
    ):
        # type: (...) -> None
        """
        This gets invoked with the event dictionary when an event should
        be sent to sentry.
        """
        raise NotImplementedError()

    def capture_envelope(
        self, envelope  # type: Envelope
    ):
        # type: (...) -> None
        """
        Send an envelope to Sentry.

        Envelopes are a data container format that can hold any type of data
        submitted to Sentry. We use it for transactions and sessions, but
        regular "error" events should go through `capture_event` for backwards
        compat.
        """
        raise NotImplementedError()

    def flush(
        self,
        timeout,  # type: float
        callback=None,  # type: Optional[Any]
    ):
        # type: (...) -> None
        """Wait `timeout` seconds for the current events to be sent out."""
        pass

    def kill(self):
        # type: () -> None
        """Forcefully kills the transport."""
        pass

    def record_lost_event(
        self,
        reason,  # type: str
        data_category=None,  # type: Optional[str]
        item=None,  # type: Optional[Item]
    ):
        # type: (...) -> None
        """This increments a counter for event loss by reason and
        data category.
        """
        return None

    def is_healthy(self):
        # type: () -> bool
        return True

    def __del__(self):
        # type: () -> None
        try:
            self.kill()
        except Exception:
            pass


def _parse_rate_limits(header, now=None):
    # type: (Any, Optional[datetime]) -> Iterable[Tuple[DataCategory, datetime]]
    if now is None:
        now = datetime_utcnow()

    for limit in header.split(","):
        try:
            parameters = limit.strip().split(":")
            retry_after, categories = parameters[:2]

            retry_after = now + timedelta(seconds=int(retry_after))
            for category in categories and categories.split(";") or (None,):
                if category == "metric_bucket":
                    try:
                        namespaces = parameters[4].split(";")
                    except IndexError:
                        namespaces = []

                    if not namespaces or "custom" in namespaces:
                        yield category, retry_after

                else:
                    yield category, retry_after
        except (LookupError, ValueError):
            continue


class HttpTransport(Transport):
    """The default HTTP transport."""

    def __init__(
        self, options  # type: Dict[str, Any]
    ):
        # type: (...) -> None
        from sentry_sdk.consts import VERSION

        Transport.__init__(self, options)
        assert self.parsed_dsn is not None
        self.options = options  # type: Dict[str, Any]
        self._worker = BackgroundWorker(queue_size=options["transport_queue_size"])
        self._auth = self.parsed_dsn.to_auth("sentry.python/%s" % VERSION)
        self._disabled_until = {}  # type: Dict[DataCategory, datetime]
        self._retry = urllib3.util.Retry()
        self._discarded_events = defaultdict(
            int
        )  # type: DefaultDict[Tuple[str, str], int]
        self._last_client_report_sent = time.time()

        compresslevel = options.get("_experiments", {}).get(
            "transport_zlib_compression_level"
        )
        self._compresslevel = 9 if compresslevel is None else int(compresslevel)

        num_pools = options.get("_experiments", {}).get("transport_num_pools")
        self._num_pools = 2 if num_pools is None else int(num_pools)

        self._pool = self._make_pool(
            self.parsed_dsn,
            http_proxy=options["http_proxy"],
            https_proxy=options["https_proxy"],
            ca_certs=options["ca_certs"],
            proxy_headers=options["proxy_headers"],
        )

        from sentry_sdk import Hub

        self.hub_cls = Hub

    def record_lost_event(
        self,
        reason,  # type: str
        data_category=None,  # type: Optional[str]
        item=None,  # type: Optional[Item]
    ):
        # type: (...) -> None
        if not self.options["send_client_reports"]:
            return

        quantity = 1
        if item is not None:
            data_category = item.data_category
            if data_category == "attachment":
                # quantity of 0 is actually 1 as we do not want to count
                # empty attachments as actually empty.
                quantity = len(item.get_bytes()) or 1

        elif data_category is None:
            raise TypeError("data category not provided")

        self._discarded_events[data_category, reason] += quantity

    def _update_rate_limits(self, response):
        # type: (urllib3.BaseHTTPResponse) -> None

        # new sentries with more rate limit insights.  We honor this header
        # no matter of the status code to update our internal rate limits.
        header = response.headers.get("x-sentry-rate-limits")
        if header:
            logger.warning("Rate-limited via x-sentry-rate-limits")
            self._disabled_until.update(_parse_rate_limits(header))

        # old sentries only communicate global rate limit hits via the
        # retry-after header on 429.  This header can also be emitted on new
        # sentries if a proxy in front wants to globally slow things down.
        elif response.status == 429:
            logger.warning("Rate-limited via 429")
            self._disabled_until[None] = datetime_utcnow() + timedelta(
                seconds=self._retry.get_retry_after(response) or 60
            )

    def _send_request(
        self,
        body,  # type: bytes
        headers,  # type: Dict[str, str]
        endpoint_type="store",  # type: EndpointType
        envelope=None,  # type: Optional[Envelope]
    ):
        # type: (...) -> None

        def record_loss(reason):
            # type: (str) -> None
            if envelope is None:
                self.record_lost_event(reason, data_category="error")
            else:
                for item in envelope.items:
                    self.record_lost_event(reason, item=item)

        headers.update(
            {
                "User-Agent": str(self._auth.client),
                "X-Sentry-Auth": str(self._auth.to_header()),
            }
        )
        try:
            response = self._pool.request(
                "POST",
                str(self._auth.get_api_url(endpoint_type)),
                body=body,
                headers=headers,
            )
        except Exception:
            self.on_dropped_event("network")
            record_loss("network_error")
            raise

        try:
            self._update_rate_limits(response)

            if response.status == 429:
                # if we hit a 429.  Something was rate limited but we already
                # acted on this in `self._update_rate_limits`.  Note that we
                # do not want to record event loss here as we will have recorded
                # an outcome in relay already.
                self.on_dropped_event("status_429")
                pass

            elif response.status >= 300 or response.status < 200:
                logger.error(
                    "Unexpected status code: %s (body: %s)",
                    response.status,
                    response.data,
                )
                self.on_dropped_event("status_{}".format(response.status))
                record_loss("network_error")
        finally:
            response.close()

    def on_dropped_event(self, reason):
        # type: (str) -> None
        return None

    def _fetch_pending_client_report(self, force=False, interval=60):
        # type: (bool, int) -> Optional[Item]
        if not self.options["send_client_reports"]:
            return None

        if not (force or self._last_client_report_sent < time.time() - interval):
            return None

        discarded_events = self._discarded_events
        self._discarded_events = defaultdict(int)
        self._last_client_report_sent = time.time()

        if not discarded_events:
            return None

        return Item(
            PayloadRef(
                json={
                    "timestamp": time.time(),
                    "discarded_events": [
                        {"reason": reason, "category": category, "quantity": quantity}
                        for (
                            (category, reason),
                            quantity,
                        ) in discarded_events.items()
                    ],
                }
            ),
            type="client_report",
        )

    def _flush_client_reports(self, force=False):
        # type: (bool) -> None
        client_report = self._fetch_pending_client_report(force=force, interval=60)
        if client_report is not None:
            self.capture_envelope(Envelope(items=[client_report]))

    def _check_disabled(self, category):
        # type: (str) -> bool
        def _disabled(bucket):
            # type: (Any) -> bool

            # The envelope item type used for metrics is statsd
            # whereas the rate limit category is metric_bucket
            if bucket == "statsd":
                bucket = "metric_bucket"

            ts = self._disabled_until.get(bucket)

            return ts is not None and ts > datetime_utcnow()

        return _disabled(category) or _disabled(None)

    def _is_rate_limited(self):
        # type: () -> bool
        return any(ts > datetime_utcnow() for ts in self._disabled_until.values())

    def _is_worker_full(self):
        # type: () -> bool
        return self._worker.full()

    def is_healthy(self):
        # type: () -> bool
        return not (self._is_worker_full() or self._is_rate_limited())

    def _send_event(
        self, event  # type: Event
    ):
        # type: (...) -> None

        if self._check_disabled("error"):
            self.on_dropped_event("self_rate_limits")
            self.record_lost_event("ratelimit_backoff", data_category="error")
            return None

        body = io.BytesIO()
        if self._compresslevel == 0:
            body.write(json_dumps(event))
        else:
            with gzip.GzipFile(
                fileobj=body, mode="w", compresslevel=self._compresslevel
            ) as f:
                f.write(json_dumps(event))

        assert self.parsed_dsn is not None
        logger.debug(
            "Sending event, type:%s level:%s event_id:%s project:%s host:%s"
            % (
                event.get("type") or "null",
                event.get("level") or "null",
                event.get("event_id") or "null",
                self.parsed_dsn.project_id,
                self.parsed_dsn.host,
            )
        )

        headers = {
            "Content-Type": "application/json",
        }
        if self._compresslevel > 0:
            headers["Content-Encoding"] = "gzip"

        self._send_request(body.getvalue(), headers=headers)
        return None

    def _send_envelope(
        self, envelope  # type: Envelope
    ):
        # type: (...) -> None

        # remove all items from the envelope which are over quota
        new_items = []
        for item in envelope.items:
            if self._check_disabled(item.data_category):
                if item.data_category in ("transaction", "error", "default", "statsd"):
                    self.on_dropped_event("self_rate_limits")
                self.record_lost_event("ratelimit_backoff", item=item)
            else:
                new_items.append(item)

        # Since we're modifying the envelope here make a copy so that others
        # that hold references do not see their envelope modified.
        envelope = Envelope(headers=envelope.headers, items=new_items)

        if not envelope.items:
            return None

        # since we're already in the business of sending out an envelope here
        # check if we have one pending for the stats session envelopes so we
        # can attach it to this enveloped scheduled for sending.  This will
        # currently typically attach the client report to the most recent
        # session update.
        client_report_item = self._fetch_pending_client_report(interval=30)
        if client_report_item is not None:
            envelope.items.append(client_report_item)

        body = io.BytesIO()
        if self._compresslevel == 0:
            envelope.serialize_into(body)
        else:
            with gzip.GzipFile(
                fileobj=body, mode="w", compresslevel=self._compresslevel
            ) as f:
                envelope.serialize_into(f)

        assert self.parsed_dsn is not None
        logger.debug(
            "Sending envelope [%s] project:%s host:%s",
            envelope.description,
            self.parsed_dsn.project_id,
            self.parsed_dsn.host,
        )

        headers = {
            "Content-Type": "application/x-sentry-envelope",
        }
        if self._compresslevel > 0:
            headers["Content-Encoding"] = "gzip"

        self._send_request(
            body.getvalue(),
            headers=headers,
            endpoint_type="envelope",
            envelope=envelope,
        )
        return None

    def _get_pool_options(self, ca_certs):
        # type: (Optional[Any]) -> Dict[str, Any]
        options = {
            "num_pools": self._num_pools,
            "cert_reqs": "CERT_REQUIRED",
            "ca_certs": ca_certs or certifi.where(),
        }

        socket_options = None  # type: Optional[List[Tuple[int, int, int | bytes]]]

        if self.options["socket_options"] is not None:
            socket_options = self.options["socket_options"]

        if self.options["keep_alive"]:
            if socket_options is None:
                socket_options = []

            used_options = {(o[0], o[1]) for o in socket_options}
            for default_option in KEEP_ALIVE_SOCKET_OPTIONS:
                if (default_option[0], default_option[1]) not in used_options:
                    socket_options.append(default_option)

        if socket_options is not None:
            options["socket_options"] = socket_options

        return options

    def _in_no_proxy(self, parsed_dsn):
        # type: (Dsn) -> bool
        no_proxy = getproxies().get("no")
        if not no_proxy:
            return False
        for host in no_proxy.split(","):
            host = host.strip()
            if parsed_dsn.host.endswith(host) or parsed_dsn.netloc.endswith(host):
                return True
        return False

    def _make_pool(
        self,
        parsed_dsn,  # type: Dsn
        http_proxy,  # type: Optional[str]
        https_proxy,  # type: Optional[str]
        ca_certs,  # type: Optional[Any]
        proxy_headers,  # type: Optional[Dict[str, str]]
    ):
        # type: (...) -> Union[PoolManager, ProxyManager]
        proxy = None
        no_proxy = self._in_no_proxy(parsed_dsn)

        # try HTTPS first
        if parsed_dsn.scheme == "https" and (https_proxy != ""):
            proxy = https_proxy or (not no_proxy and getproxies().get("https"))

        # maybe fallback to HTTP proxy
        if not proxy and (http_proxy != ""):
            proxy = http_proxy or (not no_proxy and getproxies().get("http"))

        opts = self._get_pool_options(ca_certs)

        if proxy:
            if proxy_headers:
                opts["proxy_headers"] = proxy_headers

            if proxy.startswith("socks"):
                use_socks_proxy = True
                try:
                    # Check if PySocks depencency is available
                    from urllib3.contrib.socks import SOCKSProxyManager
                except ImportError:
                    use_socks_proxy = False
                    logger.warning(
                        "You have configured a SOCKS proxy (%s) but support for SOCKS proxies is not installed. Disabling proxy support. Please add `PySocks` (or `urllib3` with the `[socks]` extra) to your dependencies.",
                        proxy,
                    )

                if use_socks_proxy:
                    return SOCKSProxyManager(proxy, **opts)
                else:
                    return urllib3.PoolManager(**opts)
            else:
                return urllib3.ProxyManager(proxy, **opts)
        else:
            return urllib3.PoolManager(**opts)

    def capture_event(
        self, event  # type: Event
    ):
        # type: (...) -> None
        hub = self.hub_cls.current

        def send_event_wrapper():
            # type: () -> None
            with hub:
                with capture_internal_exceptions():
                    self._send_event(event)
                    self._flush_client_reports()

        if not self._worker.submit(send_event_wrapper):
            self.on_dropped_event("full_queue")
            self.record_lost_event("queue_overflow", data_category="error")

    def capture_envelope(
        self, envelope  # type: Envelope
    ):
        # type: (...) -> None
        hub = self.hub_cls.current

        def send_envelope_wrapper():
            # type: () -> None
            with hub:
                with capture_internal_exceptions():
                    self._send_envelope(envelope)
                    self._flush_client_reports()

        if not self._worker.submit(send_envelope_wrapper):
            self.on_dropped_event("full_queue")
            for item in envelope.items:
                self.record_lost_event("queue_overflow", item=item)

    def flush(
        self,
        timeout,  # type: float
        callback=None,  # type: Optional[Any]
    ):
        # type: (...) -> None
        logger.debug("Flushing HTTP transport")

        if timeout > 0:
            self._worker.submit(lambda: self._flush_client_reports(force=True))
            self._worker.flush(timeout, callback)

    def kill(self):
        # type: () -> None
        logger.debug("Killing HTTP transport")
        self._worker.kill()


class _FunctionTransport(Transport):
    def __init__(
        self, func  # type: Callable[[Event], None]
    ):
        # type: (...) -> None
        Transport.__init__(self)
        self._func = func

    def capture_event(
        self, event  # type: Event
    ):
        # type: (...) -> None
        self._func(event)
        return None


def make_transport(options):
    # type: (Dict[str, Any]) -> Optional[Transport]
    ref_transport = options["transport"]

    # If no transport is given, we use the http transport class
    if ref_transport is None:
        transport_cls = HttpTransport  # type: Type[Transport]
    elif isinstance(ref_transport, Transport):
        return ref_transport
    elif isinstance(ref_transport, type) and issubclass(ref_transport, Transport):
        transport_cls = ref_transport
    elif callable(ref_transport):
        return _FunctionTransport(ref_transport)

    # if a transport class is given only instantiate it if the dsn is not
    # empty or None
    if options["dsn"]:
        return transport_cls(options)

    return None
