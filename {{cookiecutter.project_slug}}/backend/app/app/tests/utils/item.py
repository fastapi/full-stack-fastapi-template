from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.schemas.item import ItemCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


async def create_random_item(
    db: AsyncSession, *, owner_id: Optional[int] = None
) -> models.Item:
    if owner_id is None:
        user = await create_random_user(db)
        owner_id = user.id
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description, id=id)
    return await crud.item.create_with_owner(db=db, obj_in=item_in, owner_id=owner_id)
