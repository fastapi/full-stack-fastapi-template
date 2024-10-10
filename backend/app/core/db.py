from datetime import datetime
from sqlmodel import Session, create_engine
from app.models.user import  UserBusiness
from app.core.config import settings

print("SQLALCHEMY_DATABASE_URI : ", str(settings.SQLALCHEMY_DATABASE_URI))
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
print("engine created : ")

connection = engine.connect()
print("Connection successful!")
connection.close()

def init_db() -> None:
    """
    Initialize the database with the necessary default data.
    Assumes that database schema is up-to-date due to Alembic migrations.
    """
    # Example: Create the superuser if it does not exist
    with Session(engine) as session:
        print("here")
        # Check for existing superuser
        # superuser = session.exec(
        #     select(UserBusiness).where(UserBusiness.email == settings.FIRST_SUPERUSER)
        # ).first()
        # print("heree")

        # if not superuser:
        #     print("here1")
        #     user_in = UserBusiness(
        #         email=settings.FIRST_SUPERUSER,
        #         phone_number=None,
        #         is_active=True,
        #         is_superuser=True,
        #         full_name="Superuser",
        #         registration_date=datetime.utcnow()
        #     )
        #     print("here2")
        #     # Create superuser in the database
        #     session.add(user_in)
        #     print("here3")
        #     session.commit()
        #     print("here4")
        #     session.refresh(user_in)
            
        # Other initial setup tasks can go here
        # Example: Create default Nightclub, Foodcourt, etc.
        # ...

    print("Database initialization complete.")