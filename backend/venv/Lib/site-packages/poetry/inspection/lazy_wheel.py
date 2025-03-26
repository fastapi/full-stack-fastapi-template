"""Lazy ZIP over HTTP"""

from __future__ import annotations

import io
import logging
import re

from bisect import bisect_left
from bisect import bisect_right
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from typing import IO
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from urllib.parse import urlparse
from zipfile import BadZipFile
from zipfile import ZipFile

from packaging.metadata import parse_email
from requests.models import CONTENT_CHUNK_SIZE
from requests.models import HTTPError
from requests.models import Response
from requests.status_codes import codes


if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Iterator
    from types import TracebackType

    from packaging.metadata import RawMetadata
    from requests import Session
    from typing_extensions import Self

    from poetry.utils.authenticator import Authenticator


logger = logging.getLogger(__name__)


class LazyWheelUnsupportedError(Exception):
    """Raised when a lazy wheel is unsupported."""


class HTTPRangeRequestUnsupportedError(LazyWheelUnsupportedError):
    """Raised when the remote server appears unable to support byte ranges."""


class HTTPRangeRequestNotRespectedError(LazyWheelUnsupportedError):
    """Raised when the remote server tells us that it supports byte ranges
    but does not respect a respective request."""


class UnsupportedWheelError(LazyWheelUnsupportedError):
    """Unsupported wheel."""


class InvalidWheelError(LazyWheelUnsupportedError):
    """Invalid (e.g. corrupt) wheel."""

    def __init__(self, location: str, name: str) -> None:
        self.location = location
        self.name = name

    def __str__(self) -> str:
        return f"Wheel {self.name} located at {self.location} is invalid."


def metadata_from_wheel_url(
    name: str, url: str, session: Session | Authenticator
) -> RawMetadata:
    """Fetch metadata from the given wheel URL.

    This uses HTTP range requests to only fetch the portion of the wheel
    containing metadata, just enough for the object to be constructed.

    :raises HTTPRangeRequestUnsupportedError: if range requests are unsupported for ``url``.
    :raises InvalidWheelError: if the zip file contents could not be parsed.
    """
    try:
        # After context manager exit, wheel.name will point to a deleted file path.
        # Add `delete_backing_file=False` to disable this for debugging.
        with LazyWheelOverHTTP(url, session) as lazy_file:
            metadata_bytes = lazy_file.read_metadata(name)

        metadata, _ = parse_email(metadata_bytes)
        return metadata

    except (BadZipFile, UnsupportedWheelError):
        # We assume that these errors have occurred because the wheel contents
        # themselves are invalid, not because we've messed up our bookkeeping
        # and produced an invalid file.
        raise InvalidWheelError(url, name)
    except Exception as e:
        if isinstance(e, LazyWheelUnsupportedError):
            # this is expected when the code handles issues with lazy wheel metadata retrieval correctly
            raise e

        logger.debug(
            "There was an unexpected %s when handling lazy wheel metadata retrieval for %s from %s: %s",
            type(e).__name__,
            name,
            url,
            e,
        )

        # Catch all exception to handle any issues that may have occurred during
        # attempts to use Lazy Wheel.
        raise LazyWheelUnsupportedError(
            f"Attempts to use lazy wheel metadata retrieval for {name} from {url} failed"
        ) from e


class MergeIntervals:
    """Stateful bookkeeping to merge interval graphs."""

    def __init__(self, *, left: Iterable[int] = (), right: Iterable[int] = ()) -> None:
        self._left = list(left)
        self._right = list(right)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}"
            f"(left={tuple(self._left)}, right={tuple(self._right)})"
        )

    def _merge(
        self, start: int, end: int, left: int, right: int
    ) -> Iterator[tuple[int, int]]:
        """Return an iterator of intervals to be fetched.

        Args:
            start: Start of needed interval
            end: End of needed interval
            left: Index of first overlapping downloaded data
            right: Index after last overlapping downloaded data
        """
        lslice, rslice = self._left[left:right], self._right[left:right]
        i = start = min([start] + lslice[:1])
        end = max([end] + rslice[-1:])
        for j, k in zip(lslice, rslice):
            if j > i:
                yield i, j - 1
            i = k + 1
        if i <= end:
            yield i, end
        self._left[left:right], self._right[left:right] = [start], [end]

    def minimal_intervals_covering(
        self, start: int, end: int
    ) -> Iterator[tuple[int, int]]:
        """Provide the intervals needed to cover from ``start <= x <= end``.

        This method mutates internal state so that later calls only return intervals not
        covered by prior calls. The first call to this method will always return exactly
        one interval, which was exactly the one requested. Later requests for
        intervals overlapping that first requested interval will yield only the ranges
        not previously covered (which may be empty, e.g. if the same interval is
        requested twice).

        This may be used e.g. to download substrings of remote files on demand.
        """
        left = bisect_left(self._right, start)
        right = bisect_right(self._left, end)
        yield from self._merge(start, end, left, right)


class ReadOnlyIOWrapper(IO[bytes]):
    """Implement read-side ``IO[bytes]`` methods wrapping an inner ``IO[bytes]``.

    This wrapper is useful because Python currently does not distinguish read-only
    streams at the type level.
    """

    def __init__(self, inner: IO[bytes]) -> None:
        self._file = inner

    def __enter__(self) -> Self:
        self._file.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._file.__exit__(exc_type, exc_value, traceback)

    def __iter__(self) -> Iterator[bytes]:
        raise NotImplementedError

    def __next__(self) -> bytes:
        raise NotImplementedError

    @property
    def mode(self) -> str:
        """Opening mode, which is always rb."""
        return "rb"

    @property
    def name(self) -> str:
        """Path to the underlying file."""
        return self._file.name

    def seekable(self) -> bool:
        """Return whether random access is supported, which is True."""
        return True

    def close(self) -> None:
        """Close the file."""
        self._file.close()

    @property
    def closed(self) -> bool:
        """Whether the file is closed."""
        return self._file.closed

    def fileno(self) -> int:
        return self._file.fileno()

    def flush(self) -> None:
        self._file.flush()

    def isatty(self) -> bool:
        return False

    def readable(self) -> bool:
        """Return whether the file is readable, which is True."""
        return True

    def read(self, size: int = -1) -> bytes:
        """Read up to size bytes from the object and return them.

        As a convenience, if size is unspecified or -1,
        all bytes until EOF are returned.  Fewer than
        size bytes may be returned if EOF is reached.
        """
        return self._file.read(size)

    def readline(self, limit: int = -1) -> bytes:
        # Explicit impl needed to satisfy mypy.
        raise NotImplementedError

    def readlines(self, hint: int = -1) -> list[bytes]:
        raise NotImplementedError

    def seek(self, offset: int, whence: int = 0) -> int:
        """Change stream position and return the new absolute position.

        Seek to offset relative position indicated by whence:
        * 0: Start of stream (the default).  pos should be >= 0;
        * 1: Current position - pos may be negative;
        * 2: End of stream - pos usually negative.
        """
        return self._file.seek(offset, whence)

    def tell(self) -> int:
        """Return the current position."""
        return self._file.tell()

    def truncate(self, size: int | None = None) -> int:
        """Resize the stream to the given size in bytes.

        If size is unspecified resize to the current position.
        The current stream position isn't changed.

        Return the new file size.
        """
        return self._file.truncate(size)

    def writable(self) -> bool:
        """Return False."""
        return False

    def write(self, s: Any) -> int:
        raise NotImplementedError

    def writelines(self, lines: Iterable[Any]) -> None:
        raise NotImplementedError


class LazyFileOverHTTP(ReadOnlyIOWrapper):
    """File-like object representing a fixed-length file over HTTP.

    This uses HTTP range requests to lazily fetch the file's content into a temporary
    file. If such requests are not supported by the server, raises
    ``HTTPRangeRequestUnsupportedError`` in the ``__enter__`` method."""

    def __init__(
        self,
        url: str,
        session: Session | Authenticator,
        delete_backing_file: bool = True,
    ) -> None:
        inner = NamedTemporaryFile(delete=delete_backing_file)  # noqa: SIM115
        super().__init__(inner)

        self._merge_intervals: MergeIntervals | None = None
        self._length: int | None = None

        self._request_count = 0
        self._session = session
        self._url = url

    def __enter__(self) -> Self:
        super().__enter__()
        self._setup_content()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._reset_content()
        super().__exit__(exc_type, exc_value, traceback)

    def read(self, size: int = -1) -> bytes:
        """Read up to size bytes from the object and return them.

        As a convenience, if size is unspecified or -1,
        all bytes until EOF are returned.  Fewer than
        size bytes may be returned if EOF is reached.

        :raises ValueError: if ``__enter__`` was not called beforehand.
        """
        if self._length is None:
            raise ValueError(".__enter__() must be called to set up content length")
        cur = self.tell()
        logger.debug("read size %d at %d from lazy file %s", size, cur, self.name)
        if size < 0:
            assert cur <= self._length
            download_size = self._length - cur
        elif size == 0:
            return b""
        else:
            download_size = size
        stop = min(cur + download_size, self._length)
        self._ensure_downloaded(cur, stop)
        return super().read(download_size)

    @classmethod
    def _uncached_headers(cls) -> dict[str, str]:
        """HTTP headers to bypass any HTTP caching.

        The requests we perform in this file are intentionally small, and any caching
        should be done at a higher level.

        Further, caching partial requests might cause issues:
        https://github.com/pypa/pip/pull/8716
        """
        # "no-cache" is the correct value for "up to date every time", so this will also
        # ensure we get the most recent value from the server:
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching#provide_up-to-date_content_every_time
        return {"Accept-Encoding": "identity", "Cache-Control": "no-cache"}

    def _setup_content(self) -> None:
        """Initialize the internal length field and other bookkeeping.

        Ensure ``self._merge_intervals`` is initialized.

        After parsing the remote file length with ``self._fetch_content_length()``,
        this method will truncate the underlying file from parent abstract class
        ``ReadOnlyIOWrapper`` to that size in order to support seek operations against
        ``io.SEEK_END`` in ``self.read()``.

        Called in ``__enter__``, and should make recursive invocations into a no-op.
        Subclasses may override this method."""
        if self._merge_intervals is None:
            self._merge_intervals = MergeIntervals()

        if self._length is None:
            logger.debug("begin fetching content length")
            self._length = self._fetch_content_length()
            logger.debug("done fetching content length (is: %d)", self._length)
            # Enable us to seek and write anywhere in the backing file up to this
            # known length.
            self.truncate(self._length)
        else:
            logger.debug("content length already fetched (is: %d)", self._length)

    def _reset_content(self) -> None:
        """Unset the internal length field and merge intervals.

        Called in ``__exit__``, and should make recursive invocations into a no-op.
        Subclasses may override this method."""
        if self._merge_intervals is not None:
            logger.debug(
                "unsetting merge intervals (were: %s)", repr(self._merge_intervals)
            )
            self._merge_intervals = None

        if self._length is not None:
            logger.debug("unsetting content length (was: %d)", self._length)
            self._length = None

    def _content_length_from_head(self) -> int:
        """Performs a HEAD request to extract the Content-Length.

        :raises HTTPRangeRequestUnsupportedError: if the response fails to indicate support
                                             for "bytes" ranges."""
        self._request_count += 1
        head = self._session.head(
            self._url, headers=self._uncached_headers(), allow_redirects=True
        )
        head.raise_for_status()
        assert head.status_code == codes.ok
        accepted_range = head.headers.get("Accept-Ranges", None)
        if accepted_range != "bytes":
            raise HTTPRangeRequestUnsupportedError(
                f"server does not support byte ranges: header was '{accepted_range}'"
            )
        return int(head.headers["Content-Length"])

    def _fetch_content_length(self) -> int:
        """Get the remote file's length."""
        # NB: This is currently dead code, as _fetch_content_length() is overridden
        #     again in LazyWheelOverHTTP.
        return self._content_length_from_head()

    def _stream_response(self, start: int, end: int) -> Response:
        """Return streaming HTTP response to a range request from start to end."""
        headers = self._uncached_headers()
        headers["Range"] = f"bytes={start}-{end}"
        logger.debug("streamed bytes request: %s", headers["Range"])
        self._request_count += 1

        response = self._session.get(self._url, headers=headers, stream=True)
        try:
            response.raise_for_status()
            if int(response.headers["Content-Length"]) != (end - start + 1):
                raise HTTPRangeRequestNotRespectedError(
                    f"server did not respect byte range request: "
                    f"requested {end - start + 1} bytes, got "
                    f"{response.headers['Content-Length']} bytes"
                )
            return response
        except BaseException:
            response.close()
            raise

    def _fetch_content_range(self, start: int, end: int) -> Iterator[bytes]:
        """Perform a series of HTTP range requests to cover the specified byte range.

        NB: For compatibility with HTTP range requests, the range provided to this
        method must *include* the byte indexed at argument ``end`` (so e.g. ``0-1`` is 2
        bytes long, and the range can never be empty).
        """
        with self._stream_response(start, end) as response:
            yield from response.iter_content(CONTENT_CHUNK_SIZE)

    @contextmanager
    def _stay(self) -> Iterator[None]:
        """Return a context manager keeping the position.

        At the end of the block, seek back to original position.
        """
        pos = self.tell()
        try:
            yield
        finally:
            self.seek(pos)

    def _ensure_downloaded(self, start: int, end: int) -> None:
        """Ensures bytes start to end (inclusive) have been downloaded and written to
        the backing file.

        :raises ValueError: if ``__enter__`` was not called beforehand.
        """
        if self._merge_intervals is None:
            raise ValueError(".__enter__() must be called to set up merge intervals")
        # Reducing by 1 to get an inclusive end range.
        end -= 1
        with self._stay():
            for (
                range_start,
                range_end,
            ) in self._merge_intervals.minimal_intervals_covering(start, end):
                self.seek(start)
                for chunk in self._fetch_content_range(range_start, range_end):
                    self._file.write(chunk)


class LazyWheelOverHTTP(LazyFileOverHTTP):
    """File-like object mapped to a ZIP file over HTTP.

    This uses HTTP range requests to lazily fetch the file's content, which should be
    provided as the first argument to a ``ZipFile``.
    """

    # Cache this on the type to avoid trying and failing our initial lazy wheel request
    # multiple times in the same invocation against an index without this support.
    _domains_without_negative_range: ClassVar[set[str]] = set()

    _metadata_regex = re.compile(r"^[^/]*\.dist-info/METADATA$")

    def read_metadata(self, name: str) -> bytes:
        """Download and read the METADATA file from the remote wheel."""
        with ZipFile(self) as zf:
            # prefetch metadata to reduce the number of range requests
            filename = self._prefetch_metadata(name)
            return zf.read(filename)

    @classmethod
    def _initial_chunk_length(cls) -> int:
        """Return the size of the chunk (in bytes) to download from the end of the file.

        This method is called in ``self._fetch_content_length()``. As noted in that
        method's docstring, this should be set high enough to cover the central
        directory sizes of the *average* wheels you expect to see, in order to avoid
        further requests before being able to process the zip file's contents at all.
        If we choose a small number, we need one more range request for larger wheels.
        If we choose a big number, we download unnecessary data from smaller wheels.
        If the chunk size from this method is larger than the size of an entire wheel,
        that may raise an HTTP error, but this is gracefully handled in
        ``self._fetch_content_length()`` with a small performance penalty.
        """
        return 10_000

    def _fetch_content_length(self) -> int:
        """Get the total remote file length, but also download a chunk from the end.

        This method is called within ``__enter__``. In an attempt to reduce
        the total number of requests needed to populate this lazy file's contents, this
        method will also attempt to fetch a chunk of the file's actual content. This
        chunk will be ``self._initial_chunk_length()`` bytes in size, or just the remote
        file's length if that's smaller, and the chunk will come from the *end* of
        the file.

        This method will first attempt to download with a negative byte range request,
        i.e. a GET with the headers ``Range: bytes=-N`` for ``N`` equal to
        ``self._initial_chunk_length()``. If negative offsets are unsupported, it will
        instead fall back to making a HEAD request first to extract the length, followed
        by a GET request with the double-ended range header ``Range: bytes=X-Y`` to
        extract the final ``N`` bytes from the remote resource.
        """
        initial_chunk_size = self._initial_chunk_length()
        ret_length, tail = self._extract_content_length(initial_chunk_size)

        # Need to explicitly truncate here in order to perform the write and seek
        # operations below when we write the chunk of file contents to disk.
        self.truncate(ret_length)

        if tail is None:
            # If we could not download any file contents yet (e.g. if negative byte
            # ranges were not supported, or the requested range was larger than the file
            # size), then download all of this at once, hopefully pulling in the entire
            # central directory.
            initial_start = max(0, ret_length - initial_chunk_size)
            self._ensure_downloaded(initial_start, ret_length)
        else:
            # If we *could* download some file contents, then write them to the end of
            # the file and set up our bisect boundaries by hand.
            with self._stay(), tail:
                response_length = int(tail.headers["Content-Length"])
                assert response_length == min(initial_chunk_size, ret_length)
                self.seek(-response_length, io.SEEK_END)
                # Default initial chunk size is currently 1MB, but streaming content
                # here allows it to be set arbitrarily large.
                for chunk in tail.iter_content(CONTENT_CHUNK_SIZE):
                    self._file.write(chunk)

                # We now need to update our bookkeeping to cover the interval we just
                # wrote to file so we know not to do it in later read()s.
                init_chunk_start = ret_length - response_length
                # MergeIntervals uses inclusive boundaries i.e. start <= x <= end.
                init_chunk_end = ret_length - 1
                assert self._merge_intervals is not None
                assert ((init_chunk_start, init_chunk_end),) == tuple(
                    # NB: We expect LazyRemoteResource to reset `self._merge_intervals`
                    # just before it calls the current method, so our assertion here
                    # checks that indeed no prior overlapping intervals have
                    # been covered.
                    self._merge_intervals.minimal_intervals_covering(
                        init_chunk_start, init_chunk_end
                    )
                )
        return ret_length

    @staticmethod
    def _parse_full_length_from_content_range(arg: str) -> int:
        """Parse the file's full underlying length from the Content-Range header.

        This supports both * and numeric ranges, from success or error responses:
        https://www.rfc-editor.org/rfc/rfc9110#field.content-range.
        """
        m = re.match(r"bytes [^/]+/([0-9]+)", arg)
        if m is None:
            raise HTTPRangeRequestUnsupportedError(
                f"could not parse Content-Range: '{arg}'"
            )
        return int(m.group(1))

    def _try_initial_chunk_request(
        self, initial_chunk_size: int
    ) -> tuple[int, Response]:
        """Attempt to fetch a chunk from the end of the file with a negative offset."""
        headers = self._uncached_headers()
        # Perform a negative range index, which is not supported by some servers.
        headers["Range"] = f"bytes=-{initial_chunk_size}"
        logger.debug("initial bytes request: %s", headers["Range"])

        self._request_count += 1
        tail = self._session.get(self._url, headers=headers, stream=True)
        try:
            tail.raise_for_status()

            code = tail.status_code
            if code != codes.partial_content:
                # According to
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests,
                # a 200 OK implies that range requests are not supported,
                # regardless of the requested size.
                # However, some servers that support negative range requests also return a
                # 200 OK if the requested range from the end was larger than the file size.
                if code == codes.ok:
                    accept_ranges = tail.headers.get("Accept-Ranges", None)
                    content_length = int(tail.headers["Content-Length"])
                    if (
                        accept_ranges == "bytes"
                        and content_length <= initial_chunk_size
                    ):
                        return content_length, tail

                raise HTTPRangeRequestUnsupportedError(
                    f"did not receive partial content: got code {code}"
                )

            if "Content-Range" not in tail.headers:
                raise LazyWheelUnsupportedError(
                    f"file length cannot be determined for {self._url}, "
                    f"did not receive content range header from server"
                )

            file_length = self._parse_full_length_from_content_range(
                tail.headers["Content-Range"]
            )
            return (file_length, tail)
        except BaseException:
            tail.close()
            raise

    def _extract_content_length(
        self, initial_chunk_size: int
    ) -> tuple[int, Response | None]:
        """Get the Content-Length of the remote file, and possibly a chunk of it."""
        domain = urlparse(self._url).netloc
        if domain in self._domains_without_negative_range:
            return (self._content_length_from_head(), None)

        tail: Response | None
        try:
            # Initial range request for just the end of the file.
            file_length, tail = self._try_initial_chunk_request(initial_chunk_size)
        except HTTPError as e:
            # Our initial request using a negative byte range was not supported.
            resp = e.response
            code = resp.status_code if resp is not None else None

            # This indicates that the requested range from the end was larger than the
            # actual file size: https://www.rfc-editor.org/rfc/rfc9110#status.416.
            if (
                code == codes.requested_range_not_satisfiable
                and resp is not None
                and "Content-Range" in resp.headers
            ):
                # In this case, we don't have any file content yet, but we do know the
                # size the file will be, so we can return that and exit here.
                file_length = self._parse_full_length_from_content_range(
                    resp.headers["Content-Range"]
                )
                return file_length, None

            # pypi notably does not support negative byte ranges: see
            # https://github.com/pypi/warehouse/issues/12823.
            logger.debug(
                "Negative byte range not supported for domain '%s': "
                "using HEAD request before lazy wheel from now on (code: %s)",
                domain,
                code,
            )
            # Avoid trying a negative byte range request against this domain for the
            # rest of the resolve.
            self._domains_without_negative_range.add(domain)
            # Apply a HEAD request to get the real size, and nothing else for now.
            return self._content_length_from_head(), None

        # Some servers that do not support negative offsets,
        # handle a negative offset like "-10" as "0-10"...
        # ... or behave even more strangely, see
        # https://github.com/python-poetry/poetry/issues/9056#issuecomment-1973273721
        if int(tail.headers["Content-Length"]) > initial_chunk_size or tail.headers.get(
            "Content-Range", ""
        ).startswith("bytes -"):
            tail.close()
            tail = None
            self._domains_without_negative_range.add(domain)
        return file_length, tail

    def _prefetch_metadata(self, name: str) -> str:
        """Locate the *.dist-info/METADATA entry from a temporary ``ZipFile`` wrapper,
        and download it.

        This method assumes that the *.dist-info directory (containing e.g. METADATA) is
        contained in a single contiguous section of the zip file in order to ensure it
        can be downloaded in a single ranged GET request."""
        logger.debug("begin prefetching METADATA for %s", name)

        start: int | None = None
        end: int | None = None

        # This may perform further requests if __init__() did not pull in the entire
        # central directory at the end of the file (although _initial_chunk_length()
        # should be set large enough to avoid this).
        zf = ZipFile(self)

        filename = ""
        for info in zf.infolist():
            if start is None:
                if self._metadata_regex.search(info.filename):
                    filename = info.filename
                    start = info.header_offset
                    continue
            else:
                # The last .dist-info/ entry may be before the end of the file if the
                # wheel's entries are sorted lexicographically (which is unusual).
                if not self._metadata_regex.search(info.filename):
                    end = info.header_offset
                    break
        if start is None:
            raise UnsupportedWheelError(
                f"no {self._metadata_regex!r} found for {name} in {self.name}"
            )
        # If it is the last entry of the zip, then give us everything
        # until the start of the central directory.
        if end is None:
            end = zf.start_dir
        logger.debug(f"fetch {filename}")
        self._ensure_downloaded(start, end)
        logger.debug("done prefetching METADATA for %s", name)

        return filename
