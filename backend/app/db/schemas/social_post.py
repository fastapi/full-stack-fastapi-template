from datetime import datetime
from typing import List, Optional, Any

from bson import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(str):
    """Custom type for handling MongoDB ObjectId."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return str(v)


class SocialPost(BaseModel):
    """
    Schema for social media posts stored in MongoDB.
    
    This model represents a social media post from various platforms.
    """
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    platform: str
    content: str
    author: str
    author_username: str
    published_at: datetime
    likes: int = 0
    shares: int = 0
    comments: int = 0
    url: Optional[str] = None
    media_urls: List[str] = []
    hashtags: List[str] = []
    mentions: List[str] = []
    metadata: Optional[dict[str, Any]] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class SocialAnalytics(BaseModel):
    """
    Schema for social media analytics stored in MongoDB.
    
    This model represents analytics for social media data.
    """
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    post_id: PyObjectId
    sentiment_score: float
    topic_classification: List[str] = []
    engagement_rate: float
    political_leaning: Optional[str] = None
    key_entities: List[str] = []
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} 