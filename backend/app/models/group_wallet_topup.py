import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.group_wallet import GroupWallet


class GroupWalletTopup(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    group_wallet_id: uuid.UUID = Field(foreign_key="group_wallet.id", nullable=False)
    amount: float = Field(nullable=False)
    topup_time: datetime = Field(nullable=False)

    # Relationships
    group_wallet: Optional["GroupWallet"] = Relationship(back_populates="topups")
