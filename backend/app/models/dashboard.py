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


class InsightSignalSeverity(BaseModel):
    """A single signal's latest severity for the risk overview cards."""
    signal_type: str = Field(..., description="Signal type identifier")
    signal_name: str = Field(..., description="Human-readable signal display name")
    severity: str = Field(..., description="Severity level: Low, Medium, or High")
    signal_score: float = Field(..., description="Numeric signal score")
    business_meaning: str = Field(..., description="Human-readable business meaning")

    model_config = ConfigDict(from_attributes=True)


class BrandRiskOverviewResponse(BaseModel):
    """Response schema for brand risk overview with 5 signal severities."""
    brand_id: str = Field(..., description="Brand identifier")
    segment: str = Field(..., description="Segment name")
    signals: list[InsightSignalSeverity] = Field(default_factory=list, description="List of signal severities")

    model_config = ConfigDict(from_attributes=True)


class RiskHistoryDataPoint(BaseModel):
    """A single date row for risk history chart with severity values mapped to integers."""
    date: str = Field(..., description="Date of this data point (YYYY-MM-DD format)")
    competitive_dominance: Optional[int] = Field(None, description="Severity: Low=1, Medium=2, High=4")
    competitive_erosion: Optional[int] = Field(None, description="Severity: Low=1, Medium=2, High=4")
    competitor_breakthrough: Optional[int] = Field(None, description="Severity: Low=1, Medium=2, High=4")
    growth_deceleration: Optional[int] = Field(None, description="Severity: Low=1, Medium=2, High=4")
    position_weakness: Optional[int] = Field(None, description="Severity: Low=1, Medium=2, High=4")

    model_config = ConfigDict(from_attributes=True)


class RiskHistoryResponse(BaseModel):
    """Response schema for risk history time series chart."""
    brand_id: str = Field(..., description="Brand identifier")
    segment: str = Field(..., description="Segment name")
    data_points: list[RiskHistoryDataPoint] = Field(default_factory=list, description="Time series data points")

    model_config = ConfigDict(from_attributes=True)


class BrandImpressionMetric(BaseModel):
    """A single metric for the brand impression summary card."""
    current_value: Optional[float] = Field(None, description="Current metric value")
    previous_value: Optional[float] = Field(None, description="Previous metric value (7 days prior)")
    change: Optional[float] = Field(None, description="Absolute change: current - previous")
    trend: str = Field("no_data", description="Trend direction: up, down, flat, or no_data")

    model_config = ConfigDict(from_attributes=True)


class BrandImpressionSummaryResponse(BaseModel):
    """Response schema for the brand impression summary card (3 quick metrics)."""
    brand_id: str = Field(..., description="Brand identifier")
    brand_name: str = Field(..., description="Brand display name")
    visibility: BrandImpressionMetric = Field(..., description="Visibility rate (search_visibility_count / total_search_count * 100)")
    position: BrandImpressionMetric = Field(..., description="Median ranking position (lower = better)")
    sentiment: BrandImpressionMetric = Field(..., description="Final sentiment score (0-100, NULL = no reviews)")
    current_period_end: Optional[str] = Field(None, description="End date of the current 7-day window")
    previous_period_end: Optional[str] = Field(None, description="End date of the previous 7-day window")

    model_config = ConfigDict(from_attributes=True)


class ReferenceSourceItem(BaseModel):
    """A single AI reference source entry."""
    seq: int = Field(..., description="Sequence number")
    source: str = Field(..., description="Reference source URL or name")

    model_config = ConfigDict(from_attributes=True)


class ReferenceSourcesResponse(BaseModel):
    """Response schema for AI reference sources table."""
    brand_id: str = Field(..., description="Brand identifier")
    sources: list[ReferenceSourceItem] = Field(default_factory=list, description="Deduplicated reference sources")

    model_config = ConfigDict(from_attributes=True)


class CustomerReviewItem(BaseModel):
    """A single customer review with sentiment label."""
    seq: int = Field(..., description="Sequence number")
    review: str = Field(..., description="Customer review text")
    sentiment: str = Field(..., description="Sentiment label: Positive, Neutral, or Negative")

    model_config = ConfigDict(from_attributes=True)


class CustomerReviewsResponse(BaseModel):
    """Response schema for customer reviews with sentiment table."""
    brand_id: str = Field(..., description="Brand identifier")
    reviews: list[CustomerReviewItem] = Field(default_factory=list, description="Customer reviews with sentiment")

    model_config = ConfigDict(from_attributes=True)


class BrandRankingTrendDataPoint(BaseModel):
    """A single data point for the brand ranking trend chart."""
    date: str = Field(..., description="Date (YYYY-MM-DD, equals search_date_end)")
    min_ranking: Optional[float] = Field(None, description="Minimum ranking (best position reached)")
    max_ranking: Optional[float] = Field(None, description="Maximum ranking (worst position reached)")
    median_ranking: Optional[float] = Field(None, description="Median ranking")
    avg_ranking: Optional[float] = Field(None, description="Average ranking")
    is_interpolated: bool = Field(False, description="True if brand had no visibility this day — values are linearly interpolated")

    model_config = ConfigDict(from_attributes=True)


class BrandRankingTrendResponse(BaseModel):
    """Response schema for the brand ranking historical trend chart."""
    brand_id: str = Field(..., description="Brand identifier")
    segment: str = Field(..., description="Segment name used for filtering")
    data_points: list[BrandRankingTrendDataPoint] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class BrandImpressionTrendDataPoint(BaseModel):
    """A single data point for the brand impression historical trend chart."""
    date: str = Field(..., description="Date (YYYY-MM-DD, equals search_date_end)")
    visibility: Optional[float] = Field(None, description="Visibility rate (0-100%): search_visibility_count / total_search_count * 100")
    position: Optional[float] = Field(None, description="Median ranking position (lower is better)")
    sentiment: Optional[float] = Field(None, description="Final sentiment score (0-100)")

    model_config = ConfigDict(from_attributes=True)


class BrandImpressionTrendResponse(BaseModel):
    """Response schema for the brand impression historical trend chart."""
    brand_id: str = Field(..., description="Brand identifier")
    segment: str = Field(..., description="Segment name used for filtering")
    data_points: list[BrandImpressionTrendDataPoint] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CompetitorGapMetric(BaseModel):
    """
    A single gap metric comparing my brand against a competitor.

    gap_value = my_metric - competitor_metric for visibility and sentiment.
    gap_value = competitor_median_ranking - my_median_ranking for position
                (positive = my brand is in a better position).
    previous_gap_value is the same calculation for the window ending 7 days prior.
    trend: 'up' = gap improved, 'down' = gap worsened, 'flat', or 'no_data'.
    """
    gap_value: Optional[float] = Field(None, description="Current gap value")
    previous_gap_value: Optional[float] = Field(None, description="Gap value 7 days ago")
    change: Optional[float] = Field(None, description="gap_value - previous_gap_value")
    trend: str = Field("no_data", description="up | down | flat | no_data")

    model_config = ConfigDict(from_attributes=True)


class CompetitorGapSummaryResponse(BaseModel):
    """
    Gap summary between my brand and a specific competitor for a given segment.
    Sourced from the latest two windows in brand_competitors_daily_basic_metrics
    combined with brand_search_basic_metrics_daily.
    """
    brand_id: str = Field(..., description="My brand ID")
    segment: str = Field(..., description="Segment used for the query")
    competitor_brand_name: str = Field(..., description="Competitor brand name")
    visibility_gap: CompetitorGapMetric = Field(..., description="Visibility rate gap (my% - competitor%)")
    position_gap: CompetitorGapMetric = Field(..., description="Median ranking gap (competitor_rank - my_rank; positive = I rank better)")
    sentiment_gap: CompetitorGapMetric = Field(..., description="Final sentiment score gap (my_score - competitor_score)")
    current_period_end: Optional[str] = Field(None, description="End date of the current aggregation window")
    previous_period_end: Optional[str] = Field(None, description="End date of the previous aggregation window (7 days prior)")

    model_config = ConfigDict(from_attributes=True)


class CompetitorsBySegmentResponse(BaseModel):
    """Competitor names for a brand filtered by segment."""
    brand_id: str = Field(..., description="My brand ID")
    segment: str = Field(..., description="Segment used for filtering")
    competitor_names: list[str] = Field(default_factory=list, description="Ordered list of competitor brand names")

    model_config = ConfigDict(from_attributes=True)


class CompetitorGapTrendDataPoint(BaseModel):
    """A single time-series point of gap metrics between my brand and a competitor."""
    date: str = Field(..., description="ISO date string (search_date_end)")
    # Raw values
    brand_visibility: Optional[float] = Field(None, description="My visibility rate (%)")
    comp_visibility: Optional[float] = Field(None, description="Competitor visibility rate (%)")
    brand_median_ranking: Optional[float] = Field(None, description="My median ranking position")
    comp_median_ranking: Optional[float] = Field(None, description="Competitor median ranking position")
    brand_sentiment: Optional[float] = Field(None, description="My sentiment score (0–100)")
    comp_sentiment: Optional[float] = Field(None, description="Competitor sentiment score (0–100)")
    # Gaps
    visibility_gap: Optional[float] = Field(None, description="My visibility% minus competitor visibility%")
    position_gap: Optional[float] = Field(None, description="Competitor median rank minus my median rank (positive = I rank better)")
    sentiment_gap: Optional[float] = Field(None, description="My sentiment score minus competitor sentiment score")

    model_config = ConfigDict(from_attributes=True)


class CompetitorGapTrendResponse(BaseModel):
    """Time series of gap metrics for a brand vs competitor over a date range."""
    brand_id: str = Field(..., description="My brand ID")
    segment: str = Field(..., description="Segment used for the query")
    competitor_brand_name: str = Field(..., description="Competitor brand name")
    data_points: list[CompetitorGapTrendDataPoint] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CompetitorRankingDetailDataPoint(BaseModel):
    """
    One date window of brand vs competitor ranking stats.
    All ranking values: lower number = better position (#1 is best).
    Zero from the DB means the brand had no visibility → returned as None.
    Gap = comp_value - brand_value; positive means brand ranks better (lower number).
    """
    date: str = Field(..., description="ISO date string (search_date_end)")
    # Raw values
    brand_best: Optional[int] = Field(None, description="Brand best (min) ranking in window")
    brand_worst: Optional[int] = Field(None, description="Brand worst (max) ranking in window")
    brand_avg: Optional[float] = Field(None, description="Brand average ranking in window")
    comp_best: Optional[int] = Field(None, description="Competitor best (high_ranking) in window")
    comp_worst: Optional[int] = Field(None, description="Competitor worst (low_ranking) in window")
    comp_avg: Optional[float] = Field(None, description="Competitor average ranking in window")
    # Gaps (comp - brand; positive = brand ranks better)
    best_gap: Optional[float] = Field(None, description="comp_best - brand_best (positive = brand's best rank is higher)")
    worst_gap: Optional[float] = Field(None, description="comp_worst - brand_worst (positive = brand's worst rank is higher)")
    avg_gap: Optional[float] = Field(None, description="comp_avg - brand_avg (positive = brand's avg rank is higher)")

    model_config = ConfigDict(from_attributes=True)


class CompetitorRankingDetailResponse(BaseModel):
    """Time series of brand vs competitor ranking stats."""
    brand_id: str
    segment: str
    competitor_brand_name: str
    data_points: list[CompetitorRankingDetailDataPoint] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SentimentComparisonRow(BaseModel):
    """One row of brand vs competitor customer review comparison, grouped by sentiment."""
    sentiment: str = Field(..., description="Sentiment label: Positive | Neutral | Negative | Unknown")
    brand_review: str = Field("", description="Brand customer review text (empty string if none for this slot)")
    comp_review: str = Field("", description="Competitor customer review text (empty string if none for this slot)")

    model_config = ConfigDict(from_attributes=True)


class SentimentComparisonResponse(BaseModel):
    """Side-by-side brand vs competitor customer review comparison table."""
    brand_id: str
    segment: str
    competitor_brand_name: str
    rows: list[SentimentComparisonRow] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ReferenceSourceComparisonRow(BaseModel):
    """One row in the reference source comparison table."""
    seq: int = Field(..., description="Row sequence number")
    category: str = Field(..., description="common | brand_only | comp_only")
    brand_source: str = Field("", description="Brand reference source URL (empty if brand_only=False)")
    comp_source: str = Field("", description="Competitor reference source URL (empty if comp_only=False)")

    model_config = ConfigDict(from_attributes=True)


class ReferenceSourceComparisonResponse(BaseModel):
    """Side-by-side brand vs competitor reference source comparison."""
    brand_id: str
    segment: str
    competitor_brand_name: str
    rows: list[ReferenceSourceComparisonRow] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class MarketDynamicDataPoint(BaseModel):
    """One date's metrics for a single brand in the market dynamic view."""
    date: str
    visibility_share: Optional[float] = None
    search_momentum: Optional[float] = None
    position_strength: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class MarketDynamicBrandData(BaseModel):
    """Market dynamic time-series data for one brand (target or competitor)."""
    brand_name: str
    is_target: bool
    data_points: list[MarketDynamicDataPoint] = Field(default_factory=list)
    avg_visibility_share: float = 0.0
    median_position_strength: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class MarketDynamicResponse(BaseModel):
    """Full market dynamic response for the target brand and all competitors."""
    brands: list[MarketDynamicBrandData] = Field(default_factory=list)
    start_date: str
    end_date: str

    model_config = ConfigDict(from_attributes=True)
