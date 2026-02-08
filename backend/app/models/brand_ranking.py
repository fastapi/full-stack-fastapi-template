from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class RankingDataPoint(BaseModel):
    period_start: date
    period_end: date
    median_ranking: float
    avg_ranking: float
    best_ranking: int  # lowest number = best
    worst_ranking: int
    data_points_count: int
    rank_improvement: Optional[float]  # Compared to previous period


class RankingResponse(BaseModel):
    brand_name: str
    start_date: date
    end_date: date
    aggregation: str
    data: List[RankingDataPoint]