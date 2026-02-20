from sqlmodel import SQLModel

# Import all models so "from app.models import *" works.
import app.items.models  # noqa: F401 # pyright: ignore[reportUnusedImport]
import app.users.models  # noqa: F401 # pyright: ignore[reportUnusedImport]


# Generic message
class Message(SQLModel):
    message: str
