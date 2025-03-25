import os
import mimetypes

from sentry_sdk._types import TYPE_CHECKING
from sentry_sdk.envelope import Item, PayloadRef

if TYPE_CHECKING:
    from typing import Optional, Union, Callable


class Attachment(object):
    def __init__(
        self,
        bytes=None,  # type: Union[None, bytes, Callable[[], bytes]]
        filename=None,  # type: Optional[str]
        path=None,  # type: Optional[str]
        content_type=None,  # type: Optional[str]
        add_to_transactions=False,  # type: bool
    ):
        # type: (...) -> None
        if bytes is None and path is None:
            raise TypeError("path or raw bytes required for attachment")
        if filename is None and path is not None:
            filename = os.path.basename(path)
        if filename is None:
            raise TypeError("filename is required for attachment")
        if content_type is None:
            content_type = mimetypes.guess_type(filename)[0]
        self.bytes = bytes
        self.filename = filename
        self.path = path
        self.content_type = content_type
        self.add_to_transactions = add_to_transactions

    def to_envelope_item(self):
        # type: () -> Item
        """Returns an envelope item for this attachment."""
        payload = None  # type: Union[None, PayloadRef, bytes]
        if self.bytes is not None:
            if callable(self.bytes):
                payload = self.bytes()
            else:
                payload = self.bytes
        else:
            payload = PayloadRef(path=self.path)
        return Item(
            payload=payload,
            type="attachment",
            content_type=self.content_type,
            filename=self.filename,
        )

    def __repr__(self):
        # type: () -> str
        return "<Attachment %r>" % (self.filename,)
