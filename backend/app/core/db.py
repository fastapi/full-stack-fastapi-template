from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# Configurar argumentos de conexión para PostgreSQL local (sin SSL)
connect_args = {}
if settings.ENVIRONMENT == "local":
    connect_args = {
        "sslmode": "disable",
        "application_name": "genius_industries_backend"
    }

# 🚀 Railway PostgreSQL Engine con configuración optimizada
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    connect_args=connect_args,
    echo=settings.LOG_LEVEL == "DEBUG",  # Mostrar SQL queries en debug
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_recycle=settings.POSTGRES_POOL_RECYCLE,
    pool_size=settings.POSTGRES_POOL_SIZE,
    max_overflow=settings.POSTGRES_MAX_OVERFLOW,
    pool_timeout=settings.POSTGRES_POOL_TIMEOUT
)

# Crear todas las tablas (usar solo para desarrollo)
def create_db_and_tables():
    """Crear base de datos y tablas"""
    SQLModel.metadata.create_all(engine)

# Obtener una sesión de base de datos
def get_session():
    """Obtener sesión de base de datos"""
    with Session(engine) as session:
        yield session

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    """Initialize database - Simplified version"""
    # Tables should be created with Alembic migrations
    # Use: alembic upgrade head
    print("✅ Database initialization - Use alembic upgrade head for migrations")
    pass

