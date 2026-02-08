from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class VisibilityDataPoint(BaseModel):
    period_start: date
    period_end: date
    median_visibility: float
    avg_visibility: float
    min_visibility: float
    max_visibility: float
    data_points_count: int
    total_impressions: int
    avg_position: Optional[float]


class VisibilityResponse(BaseModel):
    brand_name: str
    start_date: date
    end_date: date
    aggregation: str
    data: List[VisibilityDataPoint]
