from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

# (TODO) Added another model : Group wallet transactions 
class GroupWallet(SQLModel, table=True):
    __tablename__ = "group_wallet"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    group_id: int = Field(foreign_key="group.id", nullable=False, unique=True)
    balance: float = Field(default=0.0, nullable=False)

    # Relationships
    group: Optional["Group"] = Relationship(back_populates="wallet")
    topups: List["GroupWalletTopup"] = Relationship(back_populates="group_wallet")
