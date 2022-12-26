from neomodel import (
    StructuredRel,
    BooleanProperty,
    DateTimeProperty,
)
from datetime import datetime
import pytz


class ResourceRelationship(StructuredRel):
    created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    isActive = BooleanProperty(default=True)
