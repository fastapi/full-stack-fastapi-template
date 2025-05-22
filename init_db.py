from sqlmodel import SQLModel
from sqlalchemy import create_engine, text
from backend.app.core.config import settings

# Create database URL
POSTGRES_SERVER = settings.POSTGRES_SERVER
POSTGRES_USER = settings.POSTGRES_USER
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_DB = settings.POSTGRES_DB
POSTGRES_PORT = settings.POSTGRES_PORT

# Use psycopg2 driver explicitly
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Import all models to ensure they're registered with SQLModel
from backend.app.models import User, Item, RefreshToken

def init_db():
    print("Creating database tables...")
    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
    
    # First create a connection to enable the uuid-ossp extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
        conn.commit()
    
    # Then create the tables
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
