# Import all the models, so that Base has them before being
# imported by Alembic
from app.app.db.base_class import Base  # noqa
from app.app.models.item import Item  # noqa
from app.app.models.user import User  # noqa
