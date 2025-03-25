from sentry_sdk.consts import TYPE_CHECKING
from sentry_sdk.db.explain_plan import cache_statement, should_run_explain_plan

if TYPE_CHECKING:
    from typing import Any
    from typing import Callable

    from sentry_sdk.tracing import Span


def attach_explain_plan_to_span(
    span, connection, statement, parameters, mogrify, options
):
    # type: (Span, Any, str, Any, Callable[[str, Any], bytes], dict[str, Any]) -> None
    """
    Run EXPLAIN or EXPLAIN ANALYZE on the given statement and attach the explain plan to the span data.

    Usage:
    ```
    sentry_sdk.init(
        dsn="...",
        _experiments={
            "attach_explain_plans": {
                "explain_cache_size": 1000,  # Run explain plan for the 1000 most run queries
                "explain_cache_timeout_seconds": 60 * 60 * 24,  # Run the explain plan for each statement only every 24 hours
                "use_explain_analyze": True,  # Run "explain analyze" instead of only "explain"
            }
        }
    ```
    """
    if not statement.strip().upper().startswith("SELECT"):
        return

    if not should_run_explain_plan(statement, options):
        return

    analyze = "ANALYZE" if options.get("use_explain_analyze", False) else ""
    explain_statement = ("EXPLAIN %s " % analyze) + mogrify(
        statement, parameters
    ).decode("utf-8")

    with connection.cursor() as cursor:
        cursor.execute(explain_statement)
        explain_plan = [row for row in cursor.fetchall()]

        span.set_data("db.explain_plan", explain_plan)
        cache_statement(statement, options)
