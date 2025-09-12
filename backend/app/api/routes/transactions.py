"""Transaction management API endpoints."""

import uuid

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.constants import NOT_FOUND_CODE
from app.crud import create_transaction, get_wallet_by_id, get_wallet_transactions
from app.models import (
    TransactionCreate,
    TransactionPublic,
    TransactionsPublic,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/")
def create_wallet_transaction(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    transaction_in: TransactionCreate,
) -> TransactionPublic:
    """Create a new transaction for a wallet."""
    transaction = create_transaction(
        session=session,
        transaction_in=transaction_in,
        user_id=current_user.id,
    )
    return TransactionPublic.model_validate(transaction)


@router.get("/wallet/{wallet_id}")
def read_wallet_transactions(
    session: SessionDep,
    current_user: CurrentUser,
    wallet_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> TransactionsPublic:
    """Get transactions for a specific wallet."""
    # Verify wallet belongs to user (this is also checked in get_wallet_transactions)
    wallet = get_wallet_by_id(session=session, wallet_id=wallet_id)
    if not wallet:
        raise HTTPException(status_code=NOT_FOUND_CODE, detail="Wallet not found")

    if wallet.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this wallet",
        )

    transactions = get_wallet_transactions(
        session=session,
        wallet_id=wallet_id,
        skip=skip,
        limit=limit,
    )
    transaction_data = [
        TransactionPublic.model_validate(transaction) for transaction in transactions
    ]
    return TransactionsPublic(
        transaction_data=transaction_data,
        count=len(transaction_data),
    )
