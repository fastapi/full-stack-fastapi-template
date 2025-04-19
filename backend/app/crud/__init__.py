from . import characters
from . import conversations

# Import functions from the original crud file (now named base.py)
from .base import (
    create_user,
    update_user,
    get_user_by_email,
    authenticate,
    create_item,
)

# Now, when other modules do 'from app import crud',
# they can access crud.create_user, crud.authenticate,
# crud.characters.create_character, etc.

# You can also import specific functions if preferred, e.g.:
# from .users import get_user_by_email, create_user, authenticate, update_user # Assuming users crud is also needed
# from .items import create_item # Assuming items crud is also needed

# We need to import the existing user and item crud functions as well
# Check where user/item crud functions are defined (likely crud.py initially)
# Let's assume they are in a top-level crud.py that needs to be refactored or imported here
# For now, just importing the new modules: 