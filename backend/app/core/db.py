from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, Task, TaskDifficulty
from datetime import datetime

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)

def init_tasks(session: Session):
    task = session.exec(
        select(Task).where(Task.illumination_type == "interview")
    ).first()

    if not task:
        initial_tasks = [
                Task(
                    title="Сумма чисел",
                    description="Напишите программу, которая считает сумму двух чисел.",
                    test_cases='[{"input": "2 3", "output": "5"}, {"input": "10 15", "output": "25"}]',
                    constraints='{"time_limit": "1s", "memory_limit": "256MB"}',
                    difficulty=TaskDifficulty.ONE_STAR,
                    tags='["interview"]',
                    illumination_type='interview',
                    category='Числа',
                    hint="Попробуйте использовать встроенные арифметические операции.",
                    created_at=datetime.now(),
                    is_active=True
                ),
                Task(
                    title="Фибоначчи",
                    description="Определите n-е число Фибоначчи.",
                    test_cases='[{"input": "10", "output": "55"}, {"input": "20", "output": "6765"}]',
                    constraints='{"time_limit": "2s", "memory_limit": "256MB"}',
                    difficulty=TaskDifficulty.TWO_STAR,
                    tags='["interview"]',
                    illumination_type='interview',
                    category='Числа',
                    hint="Используйте рекурсию или динамическое программирование для оптимизации.",
                    created_at=datetime.now(),
                    is_active=True
                ),
                Task(
                    title="Обратная строка",
                    description="Напишити функцию, которая переворачивает строку.",
                    test_cases='[{"input": "10", "output": "55"}, {"input": "20", "output": "6765"}]',
                    constraints='{"time_limit": "2s", "memory_limit": "256MB"}',
                    difficulty=TaskDifficulty.THREE_STAR,
                    tags='["interview"]',
                    illumination_type='interview',
                    category='Строки',
                    hint="Используйте метод двух указателей.",
                    created_at=datetime.now(),
                    is_active=True
                )
            ]
        session.add_all(initial_tasks)
        session.commit()