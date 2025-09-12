"""CRUD operations for database models."""

import uuid
from decimal import Decimal

from sqlmodel import Session, desc, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    CurrencyType,
    Item,
    ItemCreate,
    Transaction,
    TransactionCreate,
    TransactionType,
    User,
    UserCreate,
    UserUpdate,
    Wallet,
    WalletCreate,
)


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


# Exchange rates for currency conversion (hardcoded as per requirements)
EXCHANGE_RATES = {
    (CurrencyType.USD, CurrencyType.EUR): Decimal("0.85"),
    (CurrencyType.EUR, CurrencyType.USD): Decimal("1.18"),
    (CurrencyType.USD, CurrencyType.RUB): Decimal("75.0"),
    (CurrencyType.RUB, CurrencyType.USD): Decimal("0.013"),
    (CurrencyType.EUR, CurrencyType.RUB): Decimal("88.0"),
    (CurrencyType.RUB, CurrencyType.EUR): Decimal("0.011"),
}

# Transaction fee percentage
TRANSACTION_FEE_RATE = Decimal("0.02")  # 2% fee for cross-currency transactions

# Wallet constraints
MAX_WALLETS_PER_USER = 3

# Error messages
WALLET_LIMIT_EXCEEDED = "User cannot have more than 3 wallets"
WALLET_NOT_FOUND = "Wallet not found"
INSUFFICIENT_BALANCE = "Insufficient balance for debit transaction"


def create_wallet(
    *,
    session: Session,
    wallet_in: WalletCreate,
    user_id: uuid.UUID,
) -> Wallet:
    """Create a new wallet for a user."""
    # Check if user already has 3 wallets
    existing_wallets = session.exec(
        select(Wallet).where(Wallet.user_id == user_id),
    ).all()

    if len(existing_wallets) >= MAX_WALLETS_PER_USER:
        raise ValueError(WALLET_LIMIT_EXCEEDED)

    # Check if user already has a wallet with this currency
    for wallet in existing_wallets:
        if wallet.currency == wallet_in.currency:
            msg = f"User already has a {wallet_in.currency} wallet"
            raise ValueError(msg)

    db_wallet = Wallet.model_validate(
        wallet_in,
        update={"user_id": user_id, "balance": Decimal("0.00")},
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
    statement = select(Wallet).where(Wallet.user_id == user_id)
    return list(session.exec(statement).all())


def create_transaction(
    *,
    session: Session,
    transaction_in: TransactionCreate,
    wallet_id: uuid.UUID,
) -> Transaction:
    """Create a new transaction for a wallet."""
    # Get the wallet
    wallet = get_wallet_by_id(session=session, wallet_id=wallet_id)
    if not wallet:
        raise ValueError(WALLET_NOT_FOUND)

    # Determine transaction currency (default to wallet currency if not specified)
    transaction_currency = transaction_in.currency or wallet.currency
    amount = transaction_in.amount

    # Handle currency conversion and fees if needed
    if transaction_currency != wallet.currency:
        if (transaction_currency, wallet.currency) not in EXCHANGE_RATES:
            msg = (
                f"Currency conversion from {transaction_currency} "
                f"to {wallet.currency} not supported"
            )
            raise ValueError(msg)

        # Convert amount to wallet currency
        rate = EXCHANGE_RATES[(transaction_currency, wallet.currency)]
        amount = amount * rate

        # Apply transaction fee
        fee = amount * TRANSACTION_FEE_RATE
        amount = amount - fee

    # Check balance for debit transactions
    if transaction_in.transaction_type == TransactionType.DEBIT:
        if wallet.balance < amount:
            raise ValueError(INSUFFICIENT_BALANCE)
        new_balance = wallet.balance - amount
    else:  # Credit transaction
        new_balance = wallet.balance + amount

    # Update wallet balance
    wallet.balance = new_balance.quantize(Decimal("0.01"))
    session.add(wallet)

    # Create transaction record
    db_transaction = Transaction.model_validate(
        transaction_in,
        update={
            "wallet_id": wallet_id,
            "amount": amount.quantize(Decimal("0.01")),
            "currency": transaction_currency,
        },
    )
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


def get_wallet_transactions(
    *,
    session: Session,
    wallet_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[Transaction]:
    """Get transactions for a wallet."""
    statement = (
        select(Transaction)
        .where(Transaction.wallet_id == wallet_id)
        .order_by(desc(Transaction.timestamp))
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())
