from .user import user
from .item import item

# For a new basic set of CRUD operations, on a new object, let's say 'SubItem',
# you could also simply add the following lines:

from .base import CrudBase
from app.models import subitem as models_subitem
from app.schemas import subitem as schemas_subitem

subitem = CrudBase(models_subitem.SubItem, schemas_subitem.SubItem)
