from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class GroupWalletTopup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    group_wallet_id: int = Field(foreign_key="group_wallet.id", nullable=False)
    amount: float = Field(nullable=False)
    topup_time: datetime = Field(nullable=False)

    # Relationships
    group_wallet: Optional["GroupWallet"] = Relationship(back_populates="topups")