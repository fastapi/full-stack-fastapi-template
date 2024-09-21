from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class GroupMembers(SQLModel, table=True):
    group_id: int = Field(foreign_key="group.id", primary_key=True)
    user_id: int = Field(foreign_key="user_public.id", primary_key=True)

class GroupNightclubOrderLink(SQLModel, table=True):
    __tablename__ = "group_nightclub_order_link"
    
    group_id: Optional[int] = Field(default=None, foreign_key="group.id", primary_key=True)
    nightclub_order_id: Optional[int] = Field(default=None, foreign_key="nightclub_order.id", primary_key=True)

class Group(SQLModel, table=True):
    __tablename__ = "group"
    
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nightclub_id: Optional[int] = Field(default=None, foreign_key="nightclub.id")
    created_at: datetime = Field(default=datetime.utcnow)
    admin_user_id: int = Field(foreign_key="user_public.id", nullable=False)
    table_number: Optional[str] = Field(default=None)

    # Relationships
    admin_user: Optional["UserPublic"] = Relationship(back_populates="managed_groups")
    wallet: Optional["GroupWallet"] = Relationship(back_populates="group")
    members: List["UserPublic"] = Relationship(back_populates="groups", link_model=GroupMembers)
    club_visits: List["ClubVisit"] = Relationship(back_populates="group")
    nightclub_orders: List["NightclubOrder"] = Relationship(back_populates="groups", link_model=GroupNightclubOrderLink)
    nightclubs: List["Nightclub"] = Relationship(back_populates="group")