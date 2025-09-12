"""CRUD operations for database models."""

import uuid
from decimal import Decimal

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    CurrencyEnum,
    Item,
    ItemCreate,
    Transaction,
    TransactionCreate,
    TransactionTypeEnum,
    User,
    UserCreate,
    UserUpdate,
    Wallet,
    WalletCreate,
)


# Exchange rates (hardcoded for simplicity)
EXCHANGE_RATES = {
    ("USD", "EUR"): Decimal("0.85"),
    ("USD", "RUB"): Decimal("75.00"),
    ("EUR", "USD"): Decimal("1.18"),
    ("EUR", "RUB"): Decimal("88.24"),
    ("RUB", "USD"): Decimal("0.013"),
    ("RUB", "EUR"): Decimal("0.011"),
}

# Transaction fees (2% for currency conversion)
CONVERSION_FEE_RATE = Decimal("0.02")

# Maximum wallets per user
MAX_WALLETS_PER_USER = 3


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create a new user."""
    db_obj = User.model_validate(
        user_create,
        update={"hashed_password": get_password_hash(user_create.password)},
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    """Update an existing user."""
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if password := user_data.get("password"):
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """Get user by email address."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """Authenticate user with email and password."""
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    """Create a new item."""
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# Wallet CRUD operations


def create_wallet(
    *,
    session: Session,
    wallet_in: WalletCreate,
    user_id: uuid.UUID,
) -> Wallet:
    """Create a new wallet for a user."""
    # Check if user already has 3 wallets
    existing_wallets = session.exec(
        select(Wallet).where(Wallet.user_id == user_id)
    ).all()

    if len(existing_wallets) >= MAX_WALLETS_PER_USER:
        raise HTTPException(
            status_code=400, detail="User cannot have more than 3 wallets"
        )

    # Check if user already has wallet with this currency
    existing_currency_wallet = session.exec(
        select(Wallet).where(
            Wallet.user_id == user_id, Wallet.currency == wallet_in.currency
        )
    ).first()

    if existing_currency_wallet:
        raise HTTPException(
            status_code=400, detail=f"User already has a {wallet_in.currency} wallet"
        )

    db_wallet = Wallet.model_validate(
        wallet_in, update={"user_id": user_id, "balance": Decimal("0.00")}
    )
    session.add(db_wallet)
    session.commit()
    session.refresh(db_wallet)
    return db_wallet


def get_wallet_by_id(*, session: Session, wallet_id: uuid.UUID) -> Wallet | None:
    """Get wallet by ID."""
    return session.get(Wallet, wallet_id)


def get_user_wallets(*, session: Session, user_id: uuid.UUID) -> list[Wallet]:
    """Get all wallets for a user."""
    return session.exec(select(Wallet).where(Wallet.user_id == user_id)).all()


# Transaction CRUD operations


def convert_currency(
    amount: Decimal, from_currency: CurrencyEnum, to_currency: CurrencyEnum
) -> tuple[Decimal, Decimal]:
    """Convert amount between currencies and return (converted_amount, fee)."""
    if from_currency == to_currency:
        return amount, Decimal("0.00")

    rate_key = (from_currency.value, to_currency.value)
    if rate_key not in EXCHANGE_RATES:
        raise HTTPException(
            status_code=400,
            detail=f"Exchange rate not available for {from_currency} to {to_currency}",
        )

    rate = EXCHANGE_RATES[rate_key]
    converted_amount = amount * rate
    fee = converted_amount * CONVERSION_FEE_RATE
    final_amount = converted_amount - fee

    return final_amount, fee


def create_transaction(
    *, session: Session, transaction_in: TransactionCreate, user_id: uuid.UUID
) -> Transaction:
    """Create a new transaction."""
    # Get the wallet
    wallet = session.get(Wallet, transaction_in.wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Check if wallet belongs to user
    if wallet.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this wallet"
        )

    # Convert currency if needed
    transaction_amount = transaction_in.amount
    if transaction_in.currency != wallet.currency:
        converted_amount, _ = convert_currency(
            transaction_in.amount, transaction_in.currency, wallet.currency
        )
        transaction_amount = converted_amount

    # Calculate new balance
    if transaction_in.type == TransactionTypeEnum.CREDIT:
        new_balance = wallet.balance + transaction_amount
    else:  # DEBIT
        new_balance = wallet.balance - transaction_amount

        # Check for negative balance
        if new_balance < 0:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds: transaction would result in negative balance",
            )

    # Create transaction
    db_transaction = Transaction.model_validate(transaction_in)
    session.add(db_transaction)

    # Update wallet balance
    wallet.balance = new_balance
    session.add(wallet)

    session.commit()
    session.refresh(db_transaction)
    return db_transaction


def get_wallet_transactions(
    *, session: Session, wallet_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Transaction]:
    """Get transactions for a wallet."""
    return session.exec(
        select(Transaction)
        .where(Transaction.wallet_id == wallet_id)
        .offset(skip)
        .limit(limit)
        .order_by(Transaction.timestamp.desc())
    ).all()
