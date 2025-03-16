from datetime import datetime
from typing import List, Optional, Any

from bson import ObjectId
from pydantic import BaseModel, Field

from app.db.schemas.social_post import PyObjectId


class PoliticalEntity(BaseModel):
    """
    Schema for political entities stored in MongoDB.
    
    This model represents a political entity such as a politician, political party, or organization.
    """
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    entity_type: str  # "politician", "party", "organization", etc.
    description: Optional[str] = None
    country: str
    social_accounts: List[dict[str, str]] = []  # List of {platform: string, username: string}
    political_stance: Optional[str] = None
    tags: List[str] = []
    related_entities: List[PyObjectId] = []
    metadata: Optional[dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class EntityAnalytics(BaseModel):
    """
    Schema for entity analytics stored in MongoDB.
    
    This model represents analytics for political entities.
    """
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    entity_id: PyObjectId
    total_mentions: int = 0
    sentiment_distribution: dict[str, float] = {}  # e.g., {"positive": 0.3, "neutral": 0.5, "negative": 0.2}
    engagement_metrics: dict[str, int] = {}  # e.g., {"comments": 1000, "likes": 5000, "shares": 2000}
    trending_topics: List[dict[str, Any]] = []  # List of {topic: string, count: number, sentiment: number}
    time_period: str  # e.g., "last_24h", "last_week", "last_month"
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} 