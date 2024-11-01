import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.group_wallet_topup import GroupWalletTopup


# (TODO) Added another model : Group wallet transactions
class GroupWallet(SQLModel, table=True):
    __tablename__ = "group_wallet"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    group_id: uuid.UUID = Field(foreign_key="group.id", nullable=False, unique=True)
    balance: float = Field(default=0.0, nullable=False)

    # Relationships
    group: Optional["Group"] = Relationship(back_populates="wallet")
    topups: list["GroupWalletTopup"] = Relationship(back_populates="group_wallet")
