from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, List
from datetime import date


class BrandScoreDataPoint(BaseModel):
    period_start: date
    period_end: date
    brand_score: float  # 0-100 composite score
    visibility_score: float
    ranking_score: float
    engagement_score: float
    trend_score: float
    components: dict


class BrandScoreResponse(BaseModel):
    brand_name: str
    start_date: date
    end_date: date
    aggregation: str
    overall_score: float
    data: List[BrandScoreDataPoint]