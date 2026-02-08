from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, List
from datetime import date


class TimeRangeQuery(BaseModel):
    brand_name: str = Field(..., description="Brand name to query")
    start_date: date = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: date = Field(..., description="End date (YYYY-MM-DD)")
    aggregation: Literal['week', 'month', 'quarter', 'year'] = Field(
        default='week',
        description="Aggregation level"
    )

    @field_validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
