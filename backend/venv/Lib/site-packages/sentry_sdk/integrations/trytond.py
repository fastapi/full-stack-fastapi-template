import sentry_sdk.hub
import sentry_sdk.utils
import sentry_sdk.integrations
import sentry_sdk.integrations.wsgi
from sentry_sdk._types import TYPE_CHECKING

from trytond.exceptions import TrytonException  # type: ignore
from trytond.wsgi import app  # type: ignore

if TYPE_CHECKING:
    from typing import Any


# TODO: trytond-worker, trytond-cron and trytond-admin intergations


class TrytondWSGIIntegration(sentry_sdk.integrations.Integration):
    identifier = "trytond_wsgi"

    def __init__(self):  # type: () -> None
        pass

    @staticmethod
    def setup_once():  # type: () -> None
        app.wsgi_app = sentry_sdk.integrations.wsgi.SentryWsgiMiddleware(app.wsgi_app)

        def error_handler(e):  # type: (Exception) -> None
            hub = sentry_sdk.hub.Hub.current

            if hub.get_integration(TrytondWSGIIntegration) is None:
                return
            elif isinstance(e, TrytonException):
                return
            else:
                # If an integration is there, a client has to be there.
                client = hub.client  # type: Any
                event, hint = sentry_sdk.utils.event_from_exception(
                    e,
                    client_options=client.options,
                    mechanism={"type": "trytond", "handled": False},
                )
                hub.capture_event(event, hint=hint)

        # Expected error handlers signature was changed
        # when the error_handler decorator was introduced
        # in Tryton-5.4
        if hasattr(app, "error_handler"):

            @app.error_handler
            def _(app, request, e):  # type: ignore
                error_handler(e)

        else:
            app.error_handlers.append(error_handler)
