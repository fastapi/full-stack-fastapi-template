"""
Dashboard Pydantic schemas for API request/response models.

This module defines the data transfer objects (DTOs) used by the dashboard API endpoints.
These schemas handle validation and serialization of dashboard-related data.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date


class AwarenessScoreResponse(BaseModel):
    """
    Response schema for brand awareness score data.

    This schema represents the current and previous awareness scores
    retrieved from the BrandAwarenessWeeklyPerformanceTable.

    Attributes:
        brand_id: Unique identifier for the brand
        brand_name: Display name of the brand
        current_score: The latest awareness score (0-100 scale from database)
        previous_score: The previous period's awareness score for trend calculation
        normalized_score: Score converted to 0-10 scale for gauge display
        previous_normalized_score: Previous score on 0-10 scale
        current_date: Date of the current score measurement
        previous_date: Date of the previous score measurement
        has_previous: Whether previous period data exists for trend calculation
    """
    brand_id: str = Field(..., description="Unique identifier for the brand")
    brand_name: str = Field(..., description="Display name of the brand")
    current_score: float = Field(..., description="Current awareness score (0-100 scale)")
    previous_score: Optional[float] = Field(None, description="Previous awareness score")
    normalized_score: float = Field(..., description="Score normalized to 0-10 scale")
    previous_normalized_score: Optional[float] = Field(None, description="Previous score on 0-10 scale")
    current_date: date = Field(..., description="Date of current score")
    previous_date: Optional[date] = Field(None, description="Date of previous score")
    has_previous: bool = Field(False, description="Whether previous data exists")

    model_config = ConfigDict(from_attributes=True)


class ConsistencyIndexResponse(BaseModel):
    """
    Response schema for brand consistency index data.

    Similar to AwarenessScoreResponse but for the consistency index metric.

    Attributes:
        brand_id: Unique identifier for the brand
        brand_name: Display name of the brand
        current_index: The latest consistency index (0-100 scale from database)
        previous_index: The previous period's consistency index
        normalized_index: Index converted to 0-10 scale for gauge display
        previous_normalized_index: Previous index on 0-10 scale
        current_date: Date of the current index measurement
        previous_date: Date of the previous index measurement
        has_previous: Whether previous period data exists
    """
    brand_id: str = Field(..., description="Unique identifier for the brand")
    brand_name: str = Field(..., description="Display name of the brand")
    current_index: float = Field(..., description="Current consistency index (0-100 scale)")
    previous_index: Optional[float] = Field(None, description="Previous consistency index")
    normalized_index: float = Field(..., description="Index normalized to 0-10 scale")
    previous_normalized_index: Optional[float] = Field(None, description="Previous index on 0-10 scale")
    current_date: date = Field(..., description="Date of current index")
    previous_date: Optional[date] = Field(None, description="Date of previous index")
    has_previous: bool = Field(False, description="Whether previous data exists")

    model_config = ConfigDict(from_attributes=True)


class DashboardMetricsResponse(BaseModel):
    """
    Combined response schema for all dashboard metrics.

    This schema aggregates awareness score and consistency index
    into a single response for efficient data fetching.

    Attributes:
        awareness: Brand awareness score data
        consistency: Brand consistency index data
    """
    awareness: Optional[AwarenessScoreResponse] = Field(None, description="Awareness score data")
    consistency: Optional[ConsistencyIndexResponse] = Field(None, description="Consistency index data")

    model_config = ConfigDict(from_attributes=True)


class HistoricalDataPoint(BaseModel):
    """
    A single data point in the historical trend.

    Attributes:
        date: The date of this data point (ISO format string for JSON serialization)
        awareness_score: Brand awareness score (0-10 normalized scale)
        consistency_index: Brand consistency index (0-10 normalized scale)
    """
    date: str = Field(..., description="Date of this data point (YYYY-MM-DD format)")
    awareness_score: float = Field(..., description="Awareness score on 0-10 scale")
    consistency_index: float = Field(..., description="Consistency index on 0-10 scale")

    model_config = ConfigDict(from_attributes=True)


class MetricStatistics(BaseModel):
    """
    Statistical summary for a metric over a time period.

    Attributes:
        average: Average value over the period
        highest: Maximum value in the period
        lowest: Minimum value in the period
        median: Median value in the period
        average_growth: Average week-over-week growth rate (percentage)
    """
    average: float = Field(..., description="Average value")
    highest: float = Field(..., description="Highest value")
    lowest: float = Field(..., description="Lowest value")
    median: float = Field(..., description="Median value")
    average_growth: float = Field(..., description="Average growth rate (%)")

    model_config = ConfigDict(from_attributes=True)


class HistoricalTrendsResponse(BaseModel):
    """
    Response schema for historical trends data.

    Contains time series data points plus statistical summaries
    for both awareness score and consistency index.

    Attributes:
        brand_id: Brand identifier
        brand_name: Brand display name
        data_points: List of historical data points
        awareness_stats: Statistical summary for awareness scores
        consistency_stats: Statistical summary for consistency indices
        start_date: Start of the queried period
        end_date: End of the queried period
    """
    brand_id: str = Field(..., description="Brand identifier")
    brand_name: str = Field(..., description="Brand display name")
    data_points: list[HistoricalDataPoint] = Field(default_factory=list, description="Historical data points")
    awareness_stats: Optional[MetricStatistics] = Field(None, description="Awareness score statistics")
    consistency_stats: Optional[MetricStatistics] = Field(None, description="Consistency index statistics")
    start_date: str = Field(..., description="Start date of the query period")
    end_date: str = Field(..., description="End date of the query period")

    model_config = ConfigDict(from_attributes=True)


class UserBrand(BaseModel):
    """
    Schema for a brand accessible by the user.

    Attributes:
        brand_id: Unique identifier for the brand
        brand_name: Display name of the brand
        project_id: Project this brand belongs to
        project_name: Display name of the project
        user_role: User's role in the project (owner or monitor)
    """
    brand_id: str = Field(..., description="Unique identifier for the brand")
    brand_name: str = Field(..., description="Display name of the brand")
    project_id: str = Field(..., description="Project this brand belongs to")
    project_name: str = Field(..., description="Display name of the project")
    user_role: str = Field(..., description="User's role in the project")

    model_config = ConfigDict(from_attributes=True)


class UserBrandsResponse(BaseModel):
    """
    Response schema for user's accessible brands.

    This schema returns all brands the user can view based on
    their project memberships (as owner or monitor).

    Attributes:
        brands: List of accessible brands
        total_count: Total number of brands
    """
    brands: list[UserBrand] = Field(default_factory=list, description="List of accessible brands")
    total_count: int = Field(0, description="Total number of brands")

    model_config = ConfigDict(from_attributes=True)


class DetailMetricsDataPoint(BaseModel):
    """A single data point for detail metrics (visibility + ranking)."""
    date: str = Field(..., description="Date of this data point (YYYY-MM-DD format)")
    visibility_rate: float = Field(..., description="Visibility rate as percentage (0-100)")
    avg_ranking: float = Field(..., description="Average ranking for the day")

    model_config = ConfigDict(from_attributes=True)


class DetailMetricsResponse(BaseModel):
    """Response schema for detail metrics (visibility + ranking trends)."""
    brand_id: str = Field(..., description="Brand identifier")
    brand_name: str = Field(..., description="Brand display name")
    data_points: list[DetailMetricsDataPoint] = Field(default_factory=list, description="Time series data points")
    visibility_stats: Optional[MetricStatistics] = Field(None, description="Visibility rate statistics")
    ranking_stats: Optional[MetricStatistics] = Field(None, description="Ranking statistics")
    start_date: str = Field(..., description="Start date of the query period")
    end_date: str = Field(..., description="End date of the query period")

    model_config = ConfigDict(from_attributes=True)


class CompetitorBrand(BaseModel):
    """A competitor brand associated with a user's brand."""
    brand_id: str = Field(..., description="The user's brand ID (search_target_brand_id)")
    competitor_brand_name: str = Field(..., description="Competitor brand name")

    model_config = ConfigDict(from_attributes=True)


class CompetitorListResponse(BaseModel):
    """Response schema for listing competitors of a brand."""
    brand_id: str = Field(..., description="The user's brand ID")
    competitors: list[CompetitorBrand] = Field(default_factory=list, description="List of competitors")
    total_count: int = Field(0, description="Total number of competitors")

    model_config = ConfigDict(from_attributes=True)


class CompetitorMetricsDataPoint(BaseModel):
    """A single data point for competitor metrics (visibility + ranking)."""
    date: str = Field(..., description="Date of this data point (YYYY-MM-DD format)")
    visibility_rate: float = Field(..., description="Competitor visibility rate as percentage (0-100)")
    avg_ranking: float = Field(..., description="Average ranking for the day")

    model_config = ConfigDict(from_attributes=True)


class CompetitorMetricsResponse(BaseModel):
    """Response schema for competitor metrics (visibility + ranking trends)."""
    brand_id: str = Field(..., description="The user's brand ID")
    competitor_brand_name: str = Field(..., description="Competitor brand name")
    data_points: list[CompetitorMetricsDataPoint] = Field(default_factory=list, description="Time series data points")
    visibility_stats: Optional[MetricStatistics] = Field(None, description="Visibility rate statistics")
    ranking_stats: Optional[MetricStatistics] = Field(None, description="Ranking statistics")
    start_date: str = Field(..., description="Start date of the query period")
    end_date: str = Field(..., description="End date of the query period")

    model_config = ConfigDict(from_attributes=True)


class BrandSegmentsResponse(BaseModel):
    """Response schema for listing segments of a brand."""
    brand_id: str = Field(..., description="Brand identifier")
    segments: list[str] = Field(default_factory=list, description="List of segment names")

    model_config = ConfigDict(from_attributes=True)


class BrandOverviewDataPoint(BaseModel):
    """A single data point for brand overview time series."""
    date: str = Field(..., description="Date of this data point (YYYY-MM-DD format)")
    awareness_score: float = Field(..., description="Brand awareness score (0-100 scale)")
    share_of_visibility: float = Field(0.0, description="Share of visibility (0-1)")
    search_share_index: float = Field(0.0, description="Search share index (0-1)")
    position_strength: float = Field(0.0, description="Position strength (0-1)")
    search_momentum: float = Field(0.0, description="Search momentum (0-1)")

    model_config = ConfigDict(from_attributes=True)


class BrandOverviewMetricSummary(BaseModel):
    """Summary for a single metric with current value and change."""
    current_value: float = Field(..., description="Current metric value")
    previous_value: Optional[float] = Field(None, description="Previous period value")
    change: Optional[float] = Field(None, description="Change from previous period")
    has_previous: bool = Field(False, description="Whether previous data exists")

    model_config = ConfigDict(from_attributes=True)


class BrandOverviewSummary(BaseModel):
    """Summary of all 5 metrics with current values and changes."""
    awareness_score: BrandOverviewMetricSummary = Field(..., description="Brand awareness score summary")
    share_of_visibility: BrandOverviewMetricSummary = Field(..., description="Share of visibility summary")
    search_share_index: BrandOverviewMetricSummary = Field(..., description="Search share index summary")
    position_strength: BrandOverviewMetricSummary = Field(..., description="Position strength summary")
    search_momentum: BrandOverviewMetricSummary = Field(..., description="Search momentum summary")

    model_config = ConfigDict(from_attributes=True)


class BrandOverviewResponse(BaseModel):
    """Response schema for brand overview with metric summaries and time series."""
    brand_id: str = Field(..., description="Brand identifier")
    brand_name: str = Field(..., description="Brand display name")
    summary: BrandOverviewSummary = Field(..., description="Metric summaries with current/previous values")
    data_points: list[BrandOverviewDataPoint] = Field(default_factory=list, description="Time series data points")
    start_date: str = Field(..., description="Start date of the query period")
    end_date: str = Field(..., description="End date of the query period")

    model_config = ConfigDict(from_attributes=True)


class SegmentMetricsRow(BaseModel):
    """A single segment's latest metrics."""
    segment: str = Field(..., description="Segment name")
    awareness_score: float = Field(0.0, description="Awareness score (0-100)")
    share_of_visibility: float = Field(0.0, description="Share of visibility (0-1)")
    search_share_index: float = Field(0.0, description="Search share index (0-1)")
    position_strength: float = Field(0.0, description="Position strength (0-1)")
    search_momentum: float = Field(0.0, description="Search momentum (0-1)")
    consistency_index: float = Field(0.0, description="Consistency index (0-100)")

    model_config = ConfigDict(from_attributes=True)


class SegmentMetricsResponse(BaseModel):
    """Response schema for per-segment metrics breakdown."""
    brand_id: str = Field(..., description="Brand identifier")
    brand_name: str = Field(..., description="Brand display name")
    segments: list[SegmentMetricsRow] = Field(default_factory=list, description="Per-segment metric rows")

    model_config = ConfigDict(from_attributes=True)


class PerformanceDetailRow(BaseModel):
    """A single row in the performance detail table with date."""
    segment: str = Field(..., description="Segment name")
    awareness_score: float = Field(0.0, description="Awareness score (0-100)")
    share_of_visibility: float = Field(0.0, description="Share of visibility (0-1)")
    search_share_index: float = Field(0.0, description="Search share index (0-1)")
    position_strength: float = Field(0.0, description="Position strength (0-1)")
    search_momentum: float = Field(0.0, description="Search momentum (0-1)")
    date: str = Field(..., description="Search date (YYYY-MM-DD format)")

    model_config = ConfigDict(from_attributes=True)


class PerformanceDetailTableResponse(BaseModel):
    """Response schema for performance detail table with all segment rows and dates."""
    brand_id: str = Field(..., description="Brand identifier")
    brand_name: str = Field(..., description="Brand display name")
    rows: list[PerformanceDetailRow] = Field(default_factory=list, description="All segment metric rows with dates")

    model_config = ConfigDict(from_attributes=True)


class CompetitorAwarenessDataPoint(BaseModel):
    """A single data point for competitor awareness time series."""
    date: str = Field(..., description="Date of this data point (YYYY-MM-DD format)")
    awareness_score: float = Field(0.0, description="Competitor awareness score (0-100)")
    share_of_visibility: float = Field(0.0, description="Share of visibility (0-1)")
    search_share_index: float = Field(0.0, description="Search share index (0-1)")
    position_strength: float = Field(0.0, description="Position strength (0-1)")
    search_momentum: float = Field(0.0, description="Search momentum (0-1)")

    model_config = ConfigDict(from_attributes=True)


class CompetitorAwarenessResponse(BaseModel):
    """Response schema for competitor awareness time series."""
    brand_id: str = Field(..., description="Target brand identifier")
    competitor_brand_name: str = Field(..., description="Competitor brand name")
    data_points: list[CompetitorAwarenessDataPoint] = Field(default_factory=list, description="Time series data points")
    start_date: str = Field(..., description="Start date of the query period")
    end_date: str = Field(..., description="End date of the query period")

    model_config = ConfigDict(from_attributes=True)


class CompetitorDetailRow(BaseModel):
    """A single row in the competitor detail table with segment gap."""
    segment: str = Field(..., description="Segment name")
    awareness_score: float = Field(0.0, description="Competitor awareness score (0-100)")
    share_of_visibility: float = Field(0.0, description="Share of visibility (0-1)")
    search_share_index: float = Field(0.0, description="Search share index (0-1)")
    position_strength: float = Field(0.0, description="Position strength (0-1)")
    search_momentum: float = Field(0.0, description="Search momentum (0-1)")
    date: str = Field(..., description="Search date (YYYY-MM-DD format)")
    segment_gap: Optional[float] = Field(None, description="Brand awareness - competitor awareness gap")

    model_config = ConfigDict(from_attributes=True)


class CompetitorDetailTableResponse(BaseModel):
    """Response schema for competitor detail table with segment gap."""
    brand_id: str = Field(..., description="Target brand identifier")
    brand_name: str = Field(..., description="Target brand display name")
    competitor_brand_name: str = Field(..., description="Competitor brand name")
    rows: list[CompetitorDetailRow] = Field(default_factory=list, description="All competitor metric rows with dates and gap")

    model_config = ConfigDict(from_attributes=True)


class TopCompetitorResponse(BaseModel):
    """Response schema for top competitor by awareness score."""
    brand_id: str = Field(..., description="Target brand identifier")
    segment: str = Field(..., description="Segment name")
    top_competitor_name: Optional[str] = Field(None, description="Top competitor brand name by avg awareness")
    avg_awareness_score: Optional[float] = Field(None, description="Average awareness score of the top competitor")

    model_config = ConfigDict(from_attributes=True)
