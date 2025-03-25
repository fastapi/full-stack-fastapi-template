from __future__ import absolute_import
import copy

from sentry_sdk import Hub
from sentry_sdk.consts import SPANDATA
from sentry_sdk.hub import _should_send_default_pii
from sentry_sdk.integrations import DidNotEnable, Integration
from sentry_sdk.tracing import Span
from sentry_sdk.utils import capture_internal_exceptions

from sentry_sdk._types import TYPE_CHECKING

try:
    from pymongo import monitoring
except ImportError:
    raise DidNotEnable("Pymongo not installed")

if TYPE_CHECKING:
    from typing import Any, Dict, Union

    from pymongo.monitoring import (
        CommandFailedEvent,
        CommandStartedEvent,
        CommandSucceededEvent,
    )


SAFE_COMMAND_ATTRIBUTES = [
    "insert",
    "ordered",
    "find",
    "limit",
    "singleBatch",
    "aggregate",
    "createIndexes",
    "indexes",
    "delete",
    "findAndModify",
    "renameCollection",
    "to",
    "drop",
]


def _strip_pii(command):
    # type: (Dict[str, Any]) -> Dict[str, Any]
    for key in command:
        is_safe_field = key in SAFE_COMMAND_ATTRIBUTES
        if is_safe_field:
            # Skip if safe key
            continue

        update_db_command = key == "update" and "findAndModify" not in command
        if update_db_command:
            # Also skip "update" db command because it is save.
            # There is also an "update" key in the "findAndModify" command, which is NOT safe!
            continue

        # Special stripping for documents
        is_document = key == "documents"
        if is_document:
            for doc in command[key]:
                for doc_key in doc:
                    doc[doc_key] = "%s"
            continue

        # Special stripping for dict style fields
        is_dict_field = key in ["filter", "query", "update"]
        if is_dict_field:
            for item_key in command[key]:
                command[key][item_key] = "%s"
            continue

        # For pipeline fields strip the `$match` dict
        is_pipeline_field = key == "pipeline"
        if is_pipeline_field:
            for pipeline in command[key]:
                for match_key in pipeline["$match"] if "$match" in pipeline else []:
                    pipeline["$match"][match_key] = "%s"
            continue

        # Default stripping
        command[key] = "%s"

    return command


def _get_db_data(event):
    # type: (Any) -> Dict[str, Any]
    data = {}

    data[SPANDATA.DB_SYSTEM] = "mongodb"

    db_name = event.database_name
    if db_name is not None:
        data[SPANDATA.DB_NAME] = db_name

    server_address = event.connection_id[0]
    if server_address is not None:
        data[SPANDATA.SERVER_ADDRESS] = server_address

    server_port = event.connection_id[1]
    if server_port is not None:
        data[SPANDATA.SERVER_PORT] = server_port

    return data


class CommandTracer(monitoring.CommandListener):
    def __init__(self):
        # type: () -> None
        self._ongoing_operations = {}  # type: Dict[int, Span]

    def _operation_key(self, event):
        # type: (Union[CommandFailedEvent, CommandStartedEvent, CommandSucceededEvent]) -> int
        return event.request_id

    def started(self, event):
        # type: (CommandStartedEvent) -> None
        hub = Hub.current
        if hub.get_integration(PyMongoIntegration) is None:
            return
        with capture_internal_exceptions():
            command = dict(copy.deepcopy(event.command))

            command.pop("$db", None)
            command.pop("$clusterTime", None)
            command.pop("$signature", None)

            op = "db.query"

            tags = {
                "db.name": event.database_name,
                SPANDATA.DB_SYSTEM: "mongodb",
                SPANDATA.DB_OPERATION: event.command_name,
            }

            try:
                tags["net.peer.name"] = event.connection_id[0]
                tags["net.peer.port"] = str(event.connection_id[1])
            except TypeError:
                pass

            data = {"operation_ids": {}}  # type: Dict[str, Any]
            data["operation_ids"]["operation"] = event.operation_id
            data["operation_ids"]["request"] = event.request_id

            data.update(_get_db_data(event))

            try:
                lsid = command.pop("lsid")["id"]
                data["operation_ids"]["session"] = str(lsid)
            except KeyError:
                pass

            if not _should_send_default_pii():
                command = _strip_pii(command)

            query = "{} {}".format(event.command_name, command)
            span = hub.start_span(op=op, description=query)

            for tag, value in tags.items():
                span.set_tag(tag, value)

            for key, value in data.items():
                span.set_data(key, value)

            with capture_internal_exceptions():
                hub.add_breadcrumb(message=query, category="query", type=op, data=tags)

            self._ongoing_operations[self._operation_key(event)] = span.__enter__()

    def failed(self, event):
        # type: (CommandFailedEvent) -> None
        hub = Hub.current
        if hub.get_integration(PyMongoIntegration) is None:
            return

        try:
            span = self._ongoing_operations.pop(self._operation_key(event))
            span.set_status("internal_error")
            span.__exit__(None, None, None)
        except KeyError:
            return

    def succeeded(self, event):
        # type: (CommandSucceededEvent) -> None
        hub = Hub.current
        if hub.get_integration(PyMongoIntegration) is None:
            return

        try:
            span = self._ongoing_operations.pop(self._operation_key(event))
            span.set_status("ok")
            span.__exit__(None, None, None)
        except KeyError:
            pass


class PyMongoIntegration(Integration):
    identifier = "pymongo"

    @staticmethod
    def setup_once():
        # type: () -> None
        monitoring.register(CommandTracer())
