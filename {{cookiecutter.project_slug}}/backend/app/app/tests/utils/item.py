from app import crud
from app.core import config
from app.db.session import db_session
from app.models.item import ItemCreate
from app.tests.utils.user import create_random_user
from faker import Faker

fake = Faker(config.LOCALE_FOR_TESTS)


def create_random_item(owner_id: int = None):
    if owner_id is None:
        user = create_random_user()
        owner_id = user.id
    title = fake.sentence(nb_words=6, variable_nb_words=True)
    description = ' '.join(fake.paragraphs(nb=3))
    item_in = ItemCreate(title=title, description=description, id=id)
    return crud.item.create(
        db_session=db_session, item_in=item_in, owner_id=owner_id
    )
