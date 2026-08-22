from typing import Annotated

from fastapi import Query

# Shared pagination query parameters. Bounds are enforced at the API layer so
# invalid values return 422 instead of reaching Postgres OFFSET/LIMIT (which
# rejects negative values and would otherwise surface as a 500).
SkipQuery = Annotated[int, Query(ge=0)]
LimitQuery = Annotated[int, Query(ge=1, le=100)]
