import uuid
from typing import Any

from sqlmodel import Session, func, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    ItemCreate,
    Order,
    OrderCreate,
    Payment,
    PaymentCreate,
    User,
    UserCreate,
    UserUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# Payment CRUD functions
def create_order(
    *, session: Session, order_in: OrderCreate, user_id: uuid.UUID, razorpay_order_id: str
) -> Order:
    """
    Create an order in the database.

    Args:
        session: Database session
        order_in: Order creation data
        user_id: User ID who created the order
        razorpay_order_id: Razorpay order ID

    Returns:
        Created Order object
    """
    db_order = Order.model_validate(
        order_in, update={"user_id": user_id, "razorpay_order_id": razorpay_order_id, "status": "created"}
    )
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order


def get_order_by_id(*, session: Session, order_id: uuid.UUID) -> Order | None:
    """
    Get order by UUID.

    Args:
        session: Database session
        order_id: Order UUID

    Returns:
        Order object or None if not found
    """
    return session.get(Order, order_id)


def get_order_by_razorpay_id(
    *, session: Session, razorpay_order_id: str
) -> Order | None:
    """
    Get order by Razorpay order ID.

    Args:
        session: Database session
        razorpay_order_id: Razorpay order ID

    Returns:
        Order object or None if not found
    """
    statement = select(Order).where(Order.razorpay_order_id == razorpay_order_id)
    return session.exec(statement).first()


def update_order_status(
    *, session: Session, order: Order, status: str
) -> Order:
    """
    Update order status.

    Args:
        session: Database session
        order: Order object to update
        status: New status

    Returns:
        Updated Order object
    """
    from datetime import datetime
    order.status = status
    order.updated_at = datetime.utcnow()
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def create_payment(*, session: Session, payment_in: PaymentCreate) -> Payment:
    """
    Create a payment record in the database.

    Args:
        session: Database session
        payment_in: Payment creation data

    Returns:
        Created Payment object
    """
    db_payment = Payment.model_validate(payment_in)
    session.add(db_payment)
    session.commit()
    session.refresh(db_payment)
    return db_payment


def get_payments_by_order(*, session: Session, order_id: uuid.UUID) -> list[Payment]:
    """
    Get all payments for an order.

    Args:
        session: Database session
        order_id: Order UUID

    Returns:
        List of Payment objects
    """
    statement = select(Payment).where(Payment.order_id == order_id)
    return list(session.exec(statement).all())


def get_user_orders(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> tuple[list[Order], int]:
    """
    Get paginated list of orders for a user.

    Args:
        session: Database session
        user_id: User UUID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of Order objects, total count)
    """
    count_statement = (
        select(func.count())
        .select_from(Order)
        .where(Order.user_id == user_id)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    orders = list(session.exec(statement).all())

    return orders, count
