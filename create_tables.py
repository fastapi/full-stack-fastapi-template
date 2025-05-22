import psycopg2
from backend.app.core.config import settings

# Create database connection
POSTGRES_SERVER = settings.POSTGRES_SERVER
POSTGRES_USER = settings.POSTGRES_USER
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_DB = settings.POSTGRES_DB
POSTGRES_PORT = settings.POSTGRES_PORT

def create_tables():
    print("Creating database tables...")
    conn = psycopg2.connect(
        host=POSTGRES_SERVER,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
        port=POSTGRES_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create the uuid-ossp extension if it doesn't exist
    cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT true,
        is_verified BOOLEAN NOT NULL DEFAULT false,
        email_verified BOOLEAN NOT NULL DEFAULT false,
        full_name VARCHAR(255),
        role VARCHAR(20) NOT NULL DEFAULT 'user',
        last_login TIMESTAMP WITH TIME ZONE,
        sso_provider VARCHAR(20),
        sso_id VARCHAR(255),
        hashed_password VARCHAR(255)
    );
    """)
    
    print("Users table created successfully!")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
