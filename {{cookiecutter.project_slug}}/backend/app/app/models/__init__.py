# WATCH OUT
#
# load SQLalchemy classes, to avoid exception further down, such as:
# sqlalchemy.exc.InvalidRequestError: When initializing mapper mapped class User->users,
# expression 'APIKey' failed to locate a name ("name 'APIKey' is not defined"). If this is a class name,
# consider adding this relationship() to the <class 'models_user.User'>
# class after both dependent classes have been defined.
from app.db import base  # noqa
