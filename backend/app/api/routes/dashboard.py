"""
Dashboard API routes for retrieving brand performance metrics.

This module provides API endpoints for the dashboard functionality,
including awareness scores and consistency indices retrieved from
the weekly performance tables.

Endpoints:
    GET /dashboard/user-brands - Get brands accessible by the current user
    GET /dashboard/awareness-score - Get latest brand awareness score
    GET /dashboard/consistency-index - Get latest brand consistency index
    GET /dashboard/metrics - Get all dashboard metrics in one call
    GET /dashboard/historical-trends - Get historical trends data
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, distinct
from typing import Optional
from datetime import date, timedelta
from enum import Enum
import logging
import statistics

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.dashboard import (
    AwarenessScoreResponse,
    ConsistencyIndexResponse,
    DashboardMetricsResponse,
    HistoricalTrendsResponse,
    HistoricalDataPoint,
    MetricStatistics,
    UserBrand,
    UserBrandsResponse,
    DetailMetricsDataPoint,
    DetailMetricsResponse,
    CompetitorBrand,
    CompetitorListResponse,
    CompetitorMetricsDataPoint,
    CompetitorMetricsResponse,
    BrandSegmentsResponse,
    BrandOverviewDataPoint,
    BrandOverviewMetricSummary,
    BrandOverviewSummary,
    BrandOverviewResponse,
    SegmentMetricsRow,
    SegmentMetricsResponse,
    PerformanceDetailRow,
    PerformanceDetailTableResponse,
    CompetitorAwarenessDataPoint,
    CompetitorAwarenessResponse,
    CompetitorDetailRow,
    CompetitorDetailTableResponse,
    TopCompetitorResponse,
    InsightSignalSeverity,
    BrandRiskOverviewResponse,
    RiskHistoryDataPoint,
    RiskHistoryResponse,
    BrandImpressionMetric,
    BrandImpressionSummaryResponse,
    BrandSegmentsResponse,
    ReferenceSourceItem,
    ReferenceSourcesResponse,
    CustomerReviewItem,
    CustomerReviewsResponse,
    BrandImpressionTrendDataPoint,
    BrandImpressionTrendResponse,
    BrandRankingTrendDataPoint,
    BrandRankingTrendResponse,
    CompetitorGapMetric,
    CompetitorGapSummaryResponse,
    CompetitorsBySegmentResponse,
    CompetitorGapTrendDataPoint,
    CompetitorGapTrendResponse,
    CompetitorRankingDetailDataPoint,
    CompetitorRankingDetailResponse,
    SentimentComparisonRow,
    SentimentComparisonResponse,
    ReferenceSourceComparisonRow,
    ReferenceSourceComparisonResponse,
    MarketDynamicDataPoint,
    MarketDynamicBrandData,
    MarketDynamicResponse,
)
from kila_models.models import (
    UsersTable,
    BrandAwarenessDailyPerformanceTable,
    ProjectUserTable,
    ProjectsRecord,
    BrandUserTable,
    BrandsTable,
    BrandPromptTable,
    BrandCompetitorsTable,
    BrandCompetitorsAwarenessDailyPerformanceTable,
    BrandSearchCompetitorDailyBasicMetricsTable,
    BrandPerformanceInsightTable,
    BrandSearchDailyBasicMetricsTable,
    BrandSearchResultTable,
)
import json as json_module


class TimeRange(str, Enum):
    """Predefined time ranges for historical data queries."""
    ONE_MONTH = "1month"
    ONE_QUARTER = "1quarter"
    ONE_YEAR = "1year"
    YEAR_TO_DATE = "ytd"
    CUSTOM = "custom"

# Initialize logger for this module
logger = logging.getLogger(__name__)

# Create router with prefix and tags for OpenAPI documentation
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def normalize_score_to_ten_scale(score: float) -> float:
    """
    Convert a score from 0-100 scale to 0-10 scale.

    The database stores scores on a 0-100 scale, but the frontend
    gauge displays scores on a 0-10 scale. This function performs
    the conversion.

    Args:
        score: The original score on 0-100 scale

    Returns:
        The normalized score on 0-10 scale, rounded to 2 decimal places

    Example:
        >>> normalize_score_to_ten_scale(75.5)
        7.55
    """
    # Ensure score is within valid range
    clamped_score = max(0, min(100, score))
    # Convert to 0-10 scale
    normalized = clamped_score / 10.0
    # Round to 2 decimal places for display
    return round(normalized, 2)


@router.get("/user-brands", response_model=UserBrandsResponse)
async def get_user_brands(
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Get all brands accessible by the current user.

    Queries BrandUserTable to find brands where the user is OWNER or Monitor,
    then returns brand details from BrandsTable.
    """
    logger.info(f"Fetching accessible brands for user: {current_user.user_id}")

    try:
        # Get all brand_user rows for this user
        brand_user_query = select(BrandUserTable).where(
            BrandUserTable.user_id == current_user.user_id
        )
        brand_user_result = await db.execute(brand_user_query)
        brand_users = brand_user_result.scalars().all()

        if not brand_users:
            logger.info(f"No brands found for user: {current_user.user_id}")
            return UserBrandsResponse(brands=[], total_count=0)

        # Build brand_id -> user_role map
        brand_roles = {bu.brand_id: bu.user_role.value for bu in brand_users}
        brand_ids = list(brand_roles.keys())

        logger.info(f"Found {len(brand_ids)} brand memberships for user")

        # Get active brands
        brands_query = select(BrandsTable).where(
            BrandsTable.brand_id.in_(brand_ids),
            BrandsTable.is_active == True
        )
        brands_result = await db.execute(brands_query)
        brands = brands_result.scalars().all()

        user_brands = [
            UserBrand(
                brand_id=b.brand_id,
                brand_name=b.brand_name,
                project_id=b.brand_id,       # kept for backward compat with frontend
                project_name=b.brand_name,    # kept for backward compat with frontend
                user_role=brand_roles.get(b.brand_id, "monitor"),
            )
            for b in brands
        ]

        logger.info(f"Found {len(user_brands)} accessible brands for user")

        return UserBrandsResponse(brands=user_brands, total_count=len(user_brands))

    except Exception as e:
        logger.error(f"Failed to fetch user brands: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user brands: {str(e)}"
        )


@router.get("/brand-segments", response_model=BrandSegmentsResponse)
async def get_brand_segments(
    brand_id: str = Query(..., description="Brand ID to get segments for"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Return distinct segment names for a brand that have actual metrics data,
    excluding the 'all-segment' rollup row.
    """
    logger.info(f"Fetching segments for user: {current_user.user_id}, brand_id: {brand_id}")

    query = (
        select(distinct(BrandSearchDailyBasicMetricsTable.segment))
        .where(
            BrandSearchDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchDailyBasicMetricsTable.segment != "all-segment",
        )
        .order_by(BrandSearchDailyBasicMetricsTable.segment)
    )
    result = await db.execute(query)
    segments = [row[0] for row in result.fetchall() if row[0]]

    logger.info(f"Found {len(segments)} segments for brand_id: {brand_id}")
    return BrandSegmentsResponse(brand_id=brand_id, segments=segments)


@router.get("/awareness-score", response_model=Optional[AwarenessScoreResponse])
async def get_awareness_score(
    brand_id: Optional[str] = Query(None, description="Filter by specific brand ID"),
    segment: str = Query("All-Segment", description="Segment name to filter by"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve the latest brand awareness score.

    This endpoint queries the BrandAwarenessDailyPerformanceTable to get
    the most recent awareness score data. It returns both the current score
    and the previous period's score for trend calculation.

    The scores are normalized from 0-100 scale (database) to 0-10 scale
    (frontend gauge display).

    Args:
        brand_id: Optional brand ID to filter results. If not provided,
                  returns the first brand's data (for demo purposes).
        segment: Segment name to filter by (default: "All-Segment")
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        AwarenessScoreResponse with current and previous scores,
        or None if no data exists.

    Raises:
        HTTPException 401: If user is not authenticated
    """
    logger.info(f"Fetching awareness score for user: {current_user.user_id}, brand_id: {brand_id}, segment: {segment}")

    # Build query to get the two most recent records for trend calculation
    # We order by created_date descending to get the latest first
    query = (
        select(BrandAwarenessDailyPerformanceTable)
        .where(BrandAwarenessDailyPerformanceTable.segment == segment)
        .order_by(desc(BrandAwarenessDailyPerformanceTable.search_date))
        .limit(2)  # Get current and previous for trend
    )

    # Apply brand_id filter if provided
    if brand_id:
        query = query.where(BrandAwarenessDailyPerformanceTable.brand_id == brand_id)

    # Execute query
    result = await db.execute(query)
    records = result.scalars().all()

    # Return None if no data exists
    if not records:
        logger.warning(f"No awareness score data found for brand_id: {brand_id}")
        return None

    # Get current (most recent) record
    current_record = records[0]

    # Get previous record if it exists
    previous_record = records[1] if len(records) > 1 else None

    # Build response with normalized scores
    response = AwarenessScoreResponse(
        brand_id=current_record.brand_id,
        brand_name=current_record.brand_name,
        current_score=current_record.awareness_score,
        previous_score=previous_record.awareness_score if previous_record else None,
        normalized_score=normalize_score_to_ten_scale(current_record.awareness_score),
        previous_normalized_score=(
            normalize_score_to_ten_scale(previous_record.awareness_score)
            if previous_record else None
        ),
        current_date=current_record.search_date,
        previous_date=previous_record.search_date if previous_record else None,
        has_previous=previous_record is not None
    )

    logger.info(
        f"Returning awareness score: {response.normalized_score} "
        f"for brand: {response.brand_name}"
    )

    return response


@router.get("/consistency-index", response_model=Optional[ConsistencyIndexResponse])
async def get_consistency_index(
    brand_id: Optional[str] = Query(None, description="Filter by specific brand ID"),
    segment: str = Query("All-Segment", description="Segment name to filter by"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve the latest brand consistency index.

    This endpoint queries the BrandAwarenessDailyPerformanceTable to get
    the most recent consistency index data. It returns both the current index
    and the previous period's index for trend calculation.

    The indices are normalized from 0-100 scale (database) to 0-10 scale
    (frontend gauge display).

    Args:
        brand_id: Optional brand ID to filter results. If not provided,
                  returns the first brand's data (for demo purposes).
        segment: Segment name to filter by (default: "All-Segment")
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        ConsistencyIndexResponse with current and previous indices,
        or None if no data exists.

    Raises:
        HTTPException 401: If user is not authenticated
    """
    logger.info(f"Fetching consistency index for user: {current_user.user_id}, brand_id: {brand_id}, segment: {segment}")

    # Build query to get the two most recent records for trend calculation
    query = (
        select(BrandAwarenessDailyPerformanceTable)
        .where(BrandAwarenessDailyPerformanceTable.segment == segment)
        .order_by(desc(BrandAwarenessDailyPerformanceTable.search_date))
        .limit(2)
    )

    # Apply brand_id filter if provided
    if brand_id:
        query = query.where(BrandAwarenessDailyPerformanceTable.brand_id == brand_id)

    # Execute query
    result = await db.execute(query)
    records = result.scalars().all()

    # Return None if no data exists
    if not records:
        logger.warning(f"No consistency index data found for brand_id: {brand_id}")
        return None

    # Get current (most recent) record
    current_record = records[0]

    # Get previous record if it exists
    previous_record = records[1] if len(records) > 1 else None

    # Build response with normalized indices
    response = ConsistencyIndexResponse(
        brand_id=current_record.brand_id,
        brand_name=current_record.brand_name,
        current_index=current_record.consistency_index,
        previous_index=previous_record.consistency_index if previous_record else None,
        normalized_index=normalize_score_to_ten_scale(current_record.consistency_index),
        previous_normalized_index=(
            normalize_score_to_ten_scale(previous_record.consistency_index)
            if previous_record else None
        ),
        current_date=current_record.search_date,
        previous_date=previous_record.search_date if previous_record else None,
        has_previous=previous_record is not None
    )

    logger.info(
        f"Returning consistency index: {response.normalized_index} "
        f"for brand: {response.brand_name}"
    )

    return response


@router.get("/metrics", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    brand_id: Optional[str] = Query(None, description="Filter by specific brand ID"),
    segment: str = Query("All-Segment", description="Segment name to filter by"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve all dashboard metrics in a single API call.

    This endpoint is optimized for the dashboard page load, returning
    both awareness score and consistency index data in one request
    to minimize network round trips.

    Args:
        brand_id: Optional brand ID to filter results
        segment: Segment name to filter by (default: "All-Segment")
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        DashboardMetricsResponse containing both awareness and consistency data

    Raises:
        HTTPException 401: If user is not authenticated
    """
    logger.info(f"Fetching all dashboard metrics for user: {current_user.user_id}")

    # Build query to get the two most recent records
    query = (
        select(BrandAwarenessDailyPerformanceTable)
        .where(BrandAwarenessDailyPerformanceTable.segment == segment)
        .order_by(desc(BrandAwarenessDailyPerformanceTable.search_date))
        .limit(2)
    )

    if brand_id:
        query = query.where(BrandAwarenessDailyPerformanceTable.brand_id == brand_id)

    result = await db.execute(query)
    records = result.scalars().all()

    # Initialize response with None values
    awareness_response = None
    consistency_response = None

    # Build responses if data exists
    if records:
        current_record = records[0]
        previous_record = records[1] if len(records) > 1 else None

        # Build awareness score response
        awareness_response = AwarenessScoreResponse(
            brand_id=current_record.brand_id,
            brand_name=current_record.brand_name,
            current_score=current_record.awareness_score,
            previous_score=previous_record.awareness_score if previous_record else None,
            normalized_score=normalize_score_to_ten_scale(current_record.awareness_score),
            previous_normalized_score=(
                normalize_score_to_ten_scale(previous_record.awareness_score)
                if previous_record else None
            ),
            current_date=current_record.created_date,
            previous_date=previous_record.created_date if previous_record else None,
            has_previous=previous_record is not None
        )

        # Build consistency index response
        consistency_response = ConsistencyIndexResponse(
            brand_id=current_record.brand_id,
            brand_name=current_record.brand_name,
            current_index=current_record.consistency_index,
            previous_index=previous_record.consistency_index if previous_record else None,
            normalized_index=normalize_score_to_ten_scale(current_record.consistency_index),
            previous_normalized_index=(
                normalize_score_to_ten_scale(previous_record.consistency_index)
                if previous_record else None
            ),
            current_date=current_record.created_date,
            previous_date=previous_record.created_date if previous_record else None,
            has_previous=previous_record is not None
        )

    return DashboardMetricsResponse(
        awareness=awareness_response,
        consistency=consistency_response
    )


def get_date_range_for_time_range(time_range: TimeRange) -> tuple[date, date]:
    """
    Calculate the start and end dates for a predefined time range.

    Args:
        time_range: The predefined time range enum value

    Returns:
        Tuple of (start_date, end_date)
    """
    today = date.today()

    if time_range == TimeRange.ONE_MONTH:
        # Last 4 weeks
        start_date = today - timedelta(weeks=4)
    elif time_range == TimeRange.ONE_QUARTER:
        # Last 13 weeks (approximately 3 months)
        start_date = today - timedelta(weeks=13)
    elif time_range == TimeRange.ONE_YEAR:
        # Last 52 weeks
        start_date = today - timedelta(weeks=52)
    elif time_range == TimeRange.YEAR_TO_DATE:
        # From January 1st of current year
        start_date = date(today.year, 1, 1)
    else:
        # Default to 1 month
        start_date = today - timedelta(weeks=4)

    return start_date, today


def calculate_statistics(values: list[float]) -> MetricStatistics | None:
    """
    Calculate statistical summary for a list of values.

    Args:
        values: List of numeric values

    Returns:
        MetricStatistics object or None if no values
    """
    if not values:
        return None

    # Calculate growth rates (week-over-week percentage change)
    growth_rates = []
    for i in range(1, len(values)):
        if values[i - 1] != 0:
            growth_rate = ((values[i] - values[i - 1]) / values[i - 1]) * 100
            growth_rates.append(growth_rate)

    avg_growth = statistics.mean(growth_rates) if growth_rates else 0.0

    return MetricStatistics(
        average=round(statistics.mean(values), 2),
        highest=round(max(values), 2),
        lowest=round(min(values), 2),
        median=round(statistics.median(values), 2),
        average_growth=round(avg_growth, 2)
    )


@router.get("/historical-trends", response_model=HistoricalTrendsResponse)
async def get_historical_trends(
    time_range: TimeRange = Query(
        TimeRange.ONE_MONTH,
        description="Predefined time range for the query"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Custom start date (required if time_range is 'custom')"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Custom end date (required if time_range is 'custom')"
    ),
    brand_id: Optional[str] = Query(
        None,
        description="Filter by specific brand ID"
    ),
    segment: str = Query(
        "All-Segment",
        description="Segment name to filter by"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve historical trends data for brand awareness and consistency.

    This endpoint returns time series data points along with statistical
    summaries for both awareness score and consistency index metrics.

    Time Range Options:
    - 1month: Last 4 weeks of data
    - 1quarter: Last 13 weeks (approx. 3 months) of data
    - 1year: Last 52 weeks of data
    - ytd: Year-to-date (from January 1st)
    - custom: Custom date range (requires start_date and end_date)

    Args:
        time_range: Predefined time range or 'custom'
        start_date: Start date for custom range
        end_date: End date for custom range
        brand_id: Optional brand ID filter
        db: Database session
        current_user: Authenticated user

    Returns:
        HistoricalTrendsResponse with data points and statistics

    Raises:
        HTTPException 400: If custom range is selected without dates
        HTTPException 401: If user is not authenticated
    """
    logger.info(
        f"Fetching historical trends for user: {current_user.user_id}, "
        f"time_range: {time_range}, brand_id: {brand_id}"
    )

    # Determine date range
    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range"
            )
        query_start_date = start_date
        query_end_date = end_date
    else:
        query_start_date, query_end_date = get_date_range_for_time_range(time_range)

    # Build query for historical data within date range
    query = (
        select(BrandAwarenessDailyPerformanceTable)
        .where(BrandAwarenessDailyPerformanceTable.search_date >= query_start_date)
        .where(BrandAwarenessDailyPerformanceTable.search_date <= query_end_date)
        .where(BrandAwarenessDailyPerformanceTable.segment == segment)
        .order_by(asc(BrandAwarenessDailyPerformanceTable.search_date))
    )

    # Apply brand_id filter if provided
    if brand_id:
        query = query.where(BrandAwarenessDailyPerformanceTable.brand_id == brand_id)

    # Execute query
    result = await db.execute(query)
    records = result.scalars().all()

    # If no records found, return empty response
    if not records:
        logger.warning(
            f"No historical data found for brand_id: {brand_id}, "
            f"date range: {query_start_date} to {query_end_date}"
        )
        return HistoricalTrendsResponse(
            brand_id=brand_id or "unknown",
            brand_name="Unknown",
            data_points=[],
            awareness_stats=None,
            consistency_stats=None,
            start_date=query_start_date.isoformat(),
            end_date=query_end_date.isoformat()
        )

    # Build data points list
    data_points = []
    awareness_values = []
    consistency_values = []

    for record in records:
        normalized_awareness = normalize_score_to_ten_scale(record.awareness_score)
        normalized_consistency = normalize_score_to_ten_scale(record.consistency_index)

        data_points.append(HistoricalDataPoint(
            date=record.search_date.isoformat(),
            awareness_score=normalized_awareness,
            consistency_index=normalized_consistency
        ))

        awareness_values.append(normalized_awareness)
        consistency_values.append(normalized_consistency)

    # Calculate statistics
    awareness_stats = calculate_statistics(awareness_values)
    consistency_stats = calculate_statistics(consistency_values)

    # Get brand info from first record
    first_record = records[0]

    response = HistoricalTrendsResponse(
        brand_id=first_record.brand_id,
        brand_name=first_record.brand_name,
        data_points=data_points,
        awareness_stats=awareness_stats,
        consistency_stats=consistency_stats,
        start_date=query_start_date.isoformat(),
        end_date=query_end_date.isoformat()
    )

    logger.info(
        f"Returning {len(data_points)} data points for brand: {first_record.brand_name}"
    )

    return response


@router.get("/detail-metrics", response_model=DetailMetricsResponse)
async def get_detail_metrics(
    brand_id: str = Query(..., description="Brand ID to query"),
    time_range: TimeRange = Query(
        TimeRange.ONE_MONTH,
        description="Predefined time range for the query"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Custom start date (required if time_range is 'custom')"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Custom end date (required if time_range is 'custom')"
    ),
    segment: Optional[str] = Query(
        None,
        description="Segment name to filter by. If not provided, aggregates across all segments."
    ),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve detail metrics (visibility rate and ranking) for a brand.

    Returns daily time series data points for both visibility rate
    (search_visibility_count / total_search_count as percentage) and
    average search ranking, along with statistical summaries.
    """
    logger.info(
        f"Fetching detail metrics for user: {current_user.user_id}, "
        f"brand_id: {brand_id}, time_range: {time_range}"
    )

    # Determine date range
    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range"
            )
        query_start_date = start_date
        query_end_date = end_date
    else:
        query_start_date, query_end_date = get_date_range_for_time_range(time_range)

    # ---- Query visibility data ----
    vis_query = (
        select(BrandSearchDailyBasicMetricsTable)
        .where(
            BrandSearchDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchDailyBasicMetricsTable.search_date_end >= query_start_date,
            BrandSearchDailyBasicMetricsTable.search_date_end <= query_end_date
        )
        .order_by(asc(BrandSearchDailyBasicMetricsTable.search_date_end))
    )
    if segment:
        vis_query = vis_query.where(BrandSearchDailyBasicMetricsTable.segment == segment)
    vis_result = await db.execute(vis_query)
    vis_records = vis_result.scalars().all()

    # Group by date (search_date_end is a Date column, already a date object)
    by_date: dict[str, list] = {}
    brand_name = "Unknown"
    for rec in vis_records:
        d = rec.search_date_end.isoformat()
        by_date.setdefault(d, []).append(rec)
        brand_name = rec.search_target_brand_name

    # ---- Build data points ----
    all_dates = sorted(by_date.keys())

    data_points = []
    visibility_values = []
    ranking_values = []

    for d in all_dates:
        recs = by_date[d]

        # Visibility rate: total visible / total searched across all segments for this date
        total_search = sum(r.total_search_count for r in recs)
        total_visible = sum(r.search_visibility_count for r in recs)
        vis_rate = (total_visible / total_search * 100) if total_search > 0 else 0.0

        # Average ranking: already aggregated in BrandSearchDailyBasicMetricsTable.avg_ranking
        visible_recs = [r for r in recs if r.avg_ranking > 0]
        avg_rank = sum(r.avg_ranking for r in visible_recs) / len(visible_recs) if visible_recs else 0.0

        data_points.append(DetailMetricsDataPoint(
            date=d,
            visibility_rate=round(vis_rate, 2),
            avg_ranking=round(avg_rank, 2)
        ))

        visibility_values.append(round(vis_rate, 2))
        ranking_values.append(round(avg_rank, 2))

    # ---- Calculate statistics ----
    visibility_stats = calculate_statistics(visibility_values)
    ranking_stats = calculate_statistics(ranking_values)

    if not data_points:
        logger.warning(
            f"No detail metrics data found for brand_id: {brand_id}, "
            f"date range: {query_start_date} to {query_end_date}"
        )

    response = DetailMetricsResponse(
        brand_id=brand_id,
        brand_name=brand_name,
        data_points=data_points,
        visibility_stats=visibility_stats,
        ranking_stats=ranking_stats,
        start_date=query_start_date.isoformat(),
        end_date=query_end_date.isoformat()
    )

    logger.info(
        f"Returning {len(data_points)} detail metrics data points for brand: {brand_name}"
    )

    return response


@router.get("/competitors", response_model=CompetitorListResponse)
async def get_competitors(
    brand_id: str = Query(..., description="Brand ID to get competitors for"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve the list of competitors for a brand.

    Queries BrandCompetitorsTable to find all competitor brand names
    associated with the given brand_id.
    """
    logger.info(
        f"Fetching competitors for user: {current_user.user_id}, brand_id: {brand_id}"
    )

    query = (
        select(BrandCompetitorsTable)
        .where(BrandCompetitorsTable.brand_id == brand_id)
        .order_by(asc(BrandCompetitorsTable.competitor_brand_name))
    )

    result = await db.execute(query)
    records = result.scalars().all()

    competitors = [
        CompetitorBrand(
            brand_id=rec.brand_id,
            competitor_brand_name=rec.competitor_brand_name,
        )
        for rec in records
    ]

    logger.info(f"Found {len(competitors)} competitors for brand_id: {brand_id}")

    return CompetitorListResponse(
        brand_id=brand_id,
        competitors=competitors,
        total_count=len(competitors),
    )


@router.get("/competitor-metrics", response_model=CompetitorMetricsResponse)
async def get_competitor_metrics(
    brand_id: str = Query(..., description="The user's brand ID"),
    competitor_brand_name: str = Query(..., description="Competitor brand name"),
    time_range: TimeRange = Query(
        TimeRange.ONE_MONTH,
        description="Predefined time range for the query"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Custom start date (required if time_range is 'custom')"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Custom end date (required if time_range is 'custom')"
    ),
    segment: Optional[str] = Query(
        None,
        description="Segment name to filter by. If not provided, aggregates across all segments."
    ),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve competitor metrics (visibility rate and ranking) for a specific competitor.

    Returns daily time series data for the competitor's visibility rate
    (competitor_visibility_count / total_search_count as percentage) and
    average ranking, along with statistical summaries.
    """
    logger.info(
        f"Fetching competitor metrics for user: {current_user.user_id}, "
        f"brand_id: {brand_id}, competitor: {competitor_brand_name}, "
        f"time_range: {time_range}"
    )

    # Determine date range
    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range"
            )
        query_start_date = start_date
        query_end_date = end_date
    else:
        query_start_date, query_end_date = get_date_range_for_time_range(time_range)

    # ---- Query competitor metrics (visibility + ranking already aggregated) ----
    metrics_query = (
        select(BrandSearchCompetitorDailyBasicMetricsTable)
        .where(
            BrandSearchCompetitorDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchCompetitorDailyBasicMetricsTable.competitor_brand_name == competitor_brand_name,
            BrandSearchCompetitorDailyBasicMetricsTable.search_date_end >= query_start_date,
            BrandSearchCompetitorDailyBasicMetricsTable.search_date_end <= query_end_date,
        )
        .order_by(asc(BrandSearchCompetitorDailyBasicMetricsTable.search_date_end))
    )
    if segment:
        metrics_query = metrics_query.where(BrandSearchCompetitorDailyBasicMetricsTable.segment == segment)
    metrics_result = await db.execute(metrics_query)
    metrics_records = metrics_result.scalars().all()

    # Group by date
    by_date: dict[str, list] = {}
    for rec in metrics_records:
        d = rec.search_date_end.isoformat()
        by_date.setdefault(d, []).append(rec)

    # ---- Build data points ----
    all_dates = sorted(by_date.keys())

    data_points = []
    visibility_values = []
    ranking_values = []

    for d in all_dates:
        recs = by_date[d]

        # Visibility rate: already aggregated in BrandSearchCompetitorDailyBasicMetricsTable
        total_search = sum(r.total_search_count for r in recs)
        total_visible = sum(r.competitor_visibility_count for r in recs)
        vis_rate = (total_visible / total_search * 100) if total_search > 0 else 0.0

        # Average ranking: already aggregated in BrandSearchCompetitorDailyBasicMetricsTable.avg_ranking
        visible_recs = [r for r in recs if r.avg_ranking > 0]
        avg_rank = sum(r.avg_ranking for r in visible_recs) / len(visible_recs) if visible_recs else 0.0

        data_points.append(CompetitorMetricsDataPoint(
            date=d,
            visibility_rate=round(vis_rate, 2),
            avg_ranking=round(avg_rank, 2)
        ))

        visibility_values.append(round(vis_rate, 2))
        ranking_values.append(round(avg_rank, 2))

    # ---- Calculate statistics ----
    visibility_stats = calculate_statistics(visibility_values)
    ranking_stats = calculate_statistics(ranking_values)

    if not data_points:
        logger.warning(
            f"No competitor metrics data found for brand_id: {brand_id}, "
            f"competitor: {competitor_brand_name}, "
            f"date range: {query_start_date} to {query_end_date}"
        )

    response = CompetitorMetricsResponse(
        brand_id=brand_id,
        competitor_brand_name=competitor_brand_name,
        data_points=data_points,
        visibility_stats=visibility_stats,
        ranking_stats=ranking_stats,
        start_date=query_start_date.isoformat(),
        end_date=query_end_date.isoformat()
    )

    logger.info(
        f"Returning {len(data_points)} competitor metrics data points "
        f"for competitor: {competitor_brand_name}"
    )

    return response


@router.get("/brand-overview", response_model=BrandOverviewResponse)
async def get_brand_overview(
    brand_id: str = Query(..., description="Brand ID to query"),
    time_range: TimeRange = Query(
        TimeRange.ONE_MONTH,
        description="Predefined time range for the query"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Custom start date (required if time_range is 'custom')"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Custom end date (required if time_range is 'custom')"
    ),
    segment: str = Query(
        "All-Segment",
        description="Segment name to filter by"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve brand overview data with metric summaries and time series.

    Returns the 5 core metrics (awareness_score, share_of_visibility,
    search_share_index, position_strength, search_momentum) as:
    - Current/previous value summaries for metric cards
    - Time series data points for the chart
    """
    logger.info(
        f"Fetching brand overview for user: {current_user.user_id}, "
        f"brand_id: {brand_id}, time_range: {time_range}, segment: {segment}"
    )

    # Determine date range
    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range"
            )
        query_start_date = start_date
        query_end_date = end_date
    else:
        query_start_date, query_end_date = get_date_range_for_time_range(time_range)

    # Query weekly performance data within date range
    query = (
        select(BrandAwarenessDailyPerformanceTable)
        .where(
            BrandAwarenessDailyPerformanceTable.brand_id == brand_id,
            BrandAwarenessDailyPerformanceTable.segment == segment,
            BrandAwarenessDailyPerformanceTable.search_date >= query_start_date,
            BrandAwarenessDailyPerformanceTable.search_date <= query_end_date,
        )
        .order_by(asc(BrandAwarenessDailyPerformanceTable.search_date))
    )

    result = await db.execute(query)
    records = result.scalars().all()

    # Build empty response if no data
    if not records:
        logger.warning(f"No brand overview data found for brand_id: {brand_id}")
        empty_metric = BrandOverviewMetricSummary(current_value=0.0, has_previous=False)
        return BrandOverviewResponse(
            brand_id=brand_id,
            brand_name="Unknown",
            summary=BrandOverviewSummary(
                awareness_score=empty_metric,
                share_of_visibility=empty_metric,
                search_share_index=empty_metric,
                position_strength=empty_metric,
                search_momentum=empty_metric,
            ),
            data_points=[],
            start_date=query_start_date.isoformat(),
            end_date=query_end_date.isoformat(),
        )

    # Build time series data points
    data_points = []
    for record in records:
        data_points.append(BrandOverviewDataPoint(
            date=record.search_date.isoformat(),
            awareness_score=round(record.awareness_score or 0.0, 2),
            share_of_visibility=round(record.share_of_visibility or 0.0, 4),
            search_share_index=round(record.search_share_index or 0.0, 4),
            position_strength=round(record.position_strength or 0.0, 4),
            search_momentum=round(record.search_momentum or 0.0, 4),
        ))

    # Build metric summaries (current = last record, previous = second-to-last)
    current = records[-1]
    previous = records[-2] if len(records) > 1 else None

    def make_summary(current_val: float | None, previous_val: float | None) -> BrandOverviewMetricSummary:
        cv = round(current_val or 0.0, 4)
        if previous_val is not None:
            pv = round(previous_val, 4)
            return BrandOverviewMetricSummary(
                current_value=cv,
                previous_value=pv,
                change=round(cv - pv, 4),
                has_previous=True,
            )
        return BrandOverviewMetricSummary(current_value=cv, has_previous=False)

    summary = BrandOverviewSummary(
        awareness_score=make_summary(current.awareness_score, previous.awareness_score if previous else None),
        share_of_visibility=make_summary(current.share_of_visibility, previous.share_of_visibility if previous else None),
        search_share_index=make_summary(current.search_share_index, previous.search_share_index if previous else None),
        position_strength=make_summary(current.position_strength, previous.position_strength if previous else None),
        search_momentum=make_summary(current.search_momentum, previous.search_momentum if previous else None),
    )

    brand_name = records[0].brand_name

    logger.info(f"Returning {len(data_points)} brand overview data points for brand: {brand_name}")

    return BrandOverviewResponse(
        brand_id=brand_id,
        brand_name=brand_name,
        summary=summary,
        data_points=data_points,
        start_date=query_start_date.isoformat(),
        end_date=query_end_date.isoformat(),
    )


@router.get("/segment-metrics", response_model=SegmentMetricsResponse)
async def get_segment_metrics(
    brand_id: str = Query(..., description="Brand ID to query"),
    time_range: TimeRange = Query(
        TimeRange.ONE_MONTH,
        description="Predefined time range for the query"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Custom start date (required if time_range is 'custom')"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Custom end date (required if time_range is 'custom')"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve per-segment metrics breakdown for a brand.

    Returns the latest metric values for each segment (excluding "All-Segment"),
    within the specified time range.
    """
    logger.info(
        f"Fetching segment metrics for user: {current_user.user_id}, "
        f"brand_id: {brand_id}, time_range: {time_range}"
    )

    # Determine date range
    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range"
            )
        query_start_date = start_date
        query_end_date = end_date
    else:
        query_start_date, query_end_date = get_date_range_for_time_range(time_range)

    # Query all segment data within date range (excluding All-Segment)
    query = (
        select(BrandAwarenessDailyPerformanceTable)
        .where(
            BrandAwarenessDailyPerformanceTable.brand_id == brand_id,
            BrandAwarenessDailyPerformanceTable.segment != "All-Segment",
            BrandAwarenessDailyPerformanceTable.search_date >= query_start_date,
            BrandAwarenessDailyPerformanceTable.search_date <= query_end_date,
        )
        .order_by(
            asc(BrandAwarenessDailyPerformanceTable.segment),
            desc(BrandAwarenessDailyPerformanceTable.search_date),
        )
    )

    result = await db.execute(query)
    records = result.scalars().all()

    # Get the latest record per segment
    brand_name = "Unknown"
    seen_segments: set[str] = set()
    segment_rows: list[SegmentMetricsRow] = []

    for record in records:
        brand_name = record.brand_name
        if record.segment not in seen_segments:
            seen_segments.add(record.segment)
            segment_rows.append(SegmentMetricsRow(
                segment=record.segment,
                awareness_score=round(record.awareness_score or 0.0, 2),
                share_of_visibility=round(record.share_of_visibility or 0.0, 4),
                search_share_index=round(record.search_share_index or 0.0, 4),
                position_strength=round(record.position_strength or 0.0, 4),
                search_momentum=round(record.search_momentum or 0.0, 4),
                consistency_index=round(record.consistency_index or 0.0, 2),
            ))

    logger.info(f"Returning {len(segment_rows)} segment metrics for brand_id: {brand_id}")

    return SegmentMetricsResponse(
        brand_id=brand_id,
        brand_name=brand_name,
        segments=segment_rows,
    )


@router.get("/performance-detail-table", response_model=PerformanceDetailTableResponse)
async def get_performance_detail_table(
    brand_id: str = Query(..., description="Brand ID to query"),
    time_range: TimeRange = Query(
        TimeRange.ONE_MONTH,
        description="Predefined time range for the query"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Custom start date (required if time_range is 'custom')"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Custom end date (required if time_range is 'custom')"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve all segment metric rows with dates for the performance detail table.

    Returns all rows for all segments (excluding "All-Segment") within the
    specified time range, including the created_date as the search date.
    """
    logger.info(
        f"Fetching performance detail table for user: {current_user.user_id}, "
        f"brand_id: {brand_id}, time_range: {time_range}"
    )

    # Determine date range
    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range"
            )
        query_start_date = start_date
        query_end_date = end_date
    else:
        query_start_date, query_end_date = get_date_range_for_time_range(time_range)

    # Query all segment data within date range (excluding All-Segment)
    query = (
        select(BrandAwarenessDailyPerformanceTable)
        .where(
            BrandAwarenessDailyPerformanceTable.brand_id == brand_id,
            BrandAwarenessDailyPerformanceTable.segment != "All-Segment",
            BrandAwarenessDailyPerformanceTable.search_date >= query_start_date,
            BrandAwarenessDailyPerformanceTable.search_date <= query_end_date,
        )
        .order_by(
            asc(BrandAwarenessDailyPerformanceTable.segment),
            desc(BrandAwarenessDailyPerformanceTable.search_date),
        )
    )

    result = await db.execute(query)
    records = result.scalars().all()

    brand_name = "Unknown"
    rows: list[PerformanceDetailRow] = []

    for record in records:
        brand_name = record.brand_name
        rows.append(PerformanceDetailRow(
            segment=record.segment,
            awareness_score=round(record.awareness_score or 0.0, 2),
            share_of_visibility=round(record.share_of_visibility or 0.0, 4),
            search_share_index=round(record.search_share_index or 0.0, 4),
            position_strength=round(record.position_strength or 0.0, 4),
            search_momentum=round(record.search_momentum or 0.0, 4),
            date=record.search_date.isoformat(),
        ))

    logger.info(f"Returning {len(rows)} performance detail rows for brand_id: {brand_id}")

    return PerformanceDetailTableResponse(
        brand_id=brand_id,
        brand_name=brand_name,
        rows=rows,
    )


@router.get("/competitor-awareness", response_model=CompetitorAwarenessResponse)
async def get_competitor_awareness(
    brand_id: str = Query(..., description="Target brand ID"),
    competitor_brand_name: str = Query(..., description="Competitor brand name"),
    time_range: TimeRange = Query(
        TimeRange.ONE_MONTH,
        description="Predefined time range for the query"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Custom start date (required if time_range is 'custom')"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Custom end date (required if time_range is 'custom')"
    ),
    segment: str = Query(..., description="Segment name to filter by"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve competitor awareness metrics as a time series.

    Returns the 5 core metrics (awareness_score, share_of_visibility,
    search_share_index, position_strength, search_momentum) for a specific
    competitor filtered by segment and time range.
    """
    logger.info(
        f"Fetching competitor awareness for user: {current_user.user_id}, "
        f"brand_id: {brand_id}, competitor: {competitor_brand_name}, "
        f"segment: {segment}, time_range: {time_range}"
    )

    # Determine date range
    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range"
            )
        query_start_date = start_date
        query_end_date = end_date
    else:
        query_start_date, query_end_date = get_date_range_for_time_range(time_range)

    # Query competitor awareness data
    query = (
        select(BrandCompetitorsAwarenessDailyPerformanceTable)
        .where(
            BrandCompetitorsAwarenessDailyPerformanceTable.search_target_brand_id == brand_id,
            BrandCompetitorsAwarenessDailyPerformanceTable.competitor_brand_name == competitor_brand_name,
            BrandCompetitorsAwarenessDailyPerformanceTable.segment == segment,
            BrandCompetitorsAwarenessDailyPerformanceTable.search_date >= query_start_date,
            BrandCompetitorsAwarenessDailyPerformanceTable.search_date <= query_end_date,
        )
        .order_by(asc(BrandCompetitorsAwarenessDailyPerformanceTable.search_date))
    )

    result = await db.execute(query)
    records = result.scalars().all()

    data_points = []
    for record in records:
        data_points.append(CompetitorAwarenessDataPoint(
            date=record.search_date.isoformat(),
            awareness_score=round(record.awareness_score or 0.0, 2),
            share_of_visibility=round(record.share_of_visibility or 0.0, 4),
            search_share_index=round(record.search_share_index or 0.0, 4),
            position_strength=round(record.position_strength or 0.0, 4),
            search_momentum=round(record.search_momentum or 0.0, 4),
        ))

    logger.info(f"Returning {len(data_points)} competitor awareness data points")

    return CompetitorAwarenessResponse(
        brand_id=brand_id,
        competitor_brand_name=competitor_brand_name,
        data_points=data_points,
        start_date=query_start_date.isoformat(),
        end_date=query_end_date.isoformat(),
    )


@router.get("/competitor-detail-table", response_model=CompetitorDetailTableResponse)
async def get_competitor_detail_table(
    brand_id: str = Query(..., description="Target brand ID"),
    competitor_brand_name: str = Query(..., description="Competitor brand name"),
    time_range: TimeRange = Query(
        TimeRange.ONE_MONTH,
        description="Predefined time range for the query"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Custom start date (required if time_range is 'custom')"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Custom end date (required if time_range is 'custom')"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve competitor detail table with all segment rows, dates, and segment gap.

    Returns all rows for a competitor across all segments (excluding "All-Segment"),
    with the segment_gap calculated as: brand_awareness - competitor_awareness
    for matching segment+date pairs.
    """
    logger.info(
        f"Fetching competitor detail table for user: {current_user.user_id}, "
        f"brand_id: {brand_id}, competitor: {competitor_brand_name}, "
        f"time_range: {time_range}"
    )

    # Determine date range
    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range"
            )
        query_start_date = start_date
        query_end_date = end_date
    else:
        query_start_date, query_end_date = get_date_range_for_time_range(time_range)

    # Query competitor data (all segments except All-Segment)
    comp_query = (
        select(BrandCompetitorsAwarenessDailyPerformanceTable)
        .where(
            BrandCompetitorsAwarenessDailyPerformanceTable.search_target_brand_id == brand_id,
            BrandCompetitorsAwarenessDailyPerformanceTable.competitor_brand_name == competitor_brand_name,
            BrandCompetitorsAwarenessDailyPerformanceTable.segment != "All-Segment",
            BrandCompetitorsAwarenessDailyPerformanceTable.search_date >= query_start_date,
            BrandCompetitorsAwarenessDailyPerformanceTable.search_date <= query_end_date,
        )
        .order_by(
            asc(BrandCompetitorsAwarenessDailyPerformanceTable.segment),
            desc(BrandCompetitorsAwarenessDailyPerformanceTable.search_date),
        )
    )

    comp_result = await db.execute(comp_query)
    comp_records = comp_result.scalars().all()

    # Query brand's own awareness scores for gap calculation
    brand_query = (
        select(BrandAwarenessDailyPerformanceTable)
        .where(
            BrandAwarenessDailyPerformanceTable.brand_id == brand_id,
            BrandAwarenessDailyPerformanceTable.segment != "All-Segment",
            BrandAwarenessDailyPerformanceTable.search_date >= query_start_date,
            BrandAwarenessDailyPerformanceTable.search_date <= query_end_date,
        )
    )

    brand_result = await db.execute(brand_query)
    brand_records = brand_result.scalars().all()

    # Build lookup: (segment, date_str) -> brand_awareness_score
    brand_awareness_map: dict[tuple[str, str], float] = {}
    brand_name = "Unknown"
    for record in brand_records:
        brand_name = record.brand_name
        key = (record.segment, record.search_date.isoformat())
        brand_awareness_map[key] = record.awareness_score or 0.0

    # Build rows with segment gap
    rows: list[CompetitorDetailRow] = []
    for record in comp_records:
        if brand_name == "Unknown":
            brand_name = record.search_target_brand_name or "Unknown"

        comp_awareness = round(record.awareness_score or 0.0, 2)
        date_str = record.search_date.isoformat()
        key = (record.segment, date_str)

        # Calculate segment gap
        brand_awareness = brand_awareness_map.get(key)
        if brand_awareness is not None:
            segment_gap = round(brand_awareness - comp_awareness, 2)
        else:
            segment_gap = None

        rows.append(CompetitorDetailRow(
            segment=record.segment,
            awareness_score=comp_awareness,
            share_of_visibility=round(record.share_of_visibility or 0.0, 4),
            search_share_index=round(record.search_share_index or 0.0, 4),
            position_strength=round(record.position_strength or 0.0, 4),
            search_momentum=round(record.search_momentum or 0.0, 4),
            date=date_str,
            segment_gap=segment_gap,
        ))

    logger.info(f"Returning {len(rows)} competitor detail rows for brand_id: {brand_id}")

    return CompetitorDetailTableResponse(
        brand_id=brand_id,
        brand_name=brand_name,
        competitor_brand_name=competitor_brand_name,
        rows=rows,
    )


@router.get("/top-competitor", response_model=TopCompetitorResponse)
async def get_top_competitor(
    brand_id: str = Query(..., description="Target brand ID"),
    segment: str = Query(..., description="Segment name to filter by"),
    time_range: TimeRange = Query(
        TimeRange.ONE_MONTH,
        description="Predefined time range for the query"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Custom start date (required if time_range is 'custom')"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Custom end date (required if time_range is 'custom')"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Find the top competitor by average awareness score for a given brand,
    segment, and time range.

    Queries BrandCompetitorsAwarenessDailyPerformanceTable grouped by
    competitor_brand_name, calculates average awareness_score, and returns
    the competitor with the highest average.
    """
    logger.info(
        f"Fetching top competitor for user: {current_user.user_id}, "
        f"brand_id: {brand_id}, segment: {segment}, time_range: {time_range}"
    )

    # Determine date range
    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range"
            )
        query_start_date = start_date
        query_end_date = end_date
    else:
        query_start_date, query_end_date = get_date_range_for_time_range(time_range)

    # Query all competitor records for this brand + segment + date range
    query = (
        select(BrandCompetitorsAwarenessDailyPerformanceTable)
        .where(
            BrandCompetitorsAwarenessDailyPerformanceTable.search_target_brand_id == brand_id,
            BrandCompetitorsAwarenessDailyPerformanceTable.segment == segment,
            BrandCompetitorsAwarenessDailyPerformanceTable.search_date >= query_start_date,
            BrandCompetitorsAwarenessDailyPerformanceTable.search_date <= query_end_date,
        )
    )

    result = await db.execute(query)
    records = result.scalars().all()

    if not records:
        logger.info(f"No competitor awareness data found for brand_id: {brand_id}, segment: {segment}")
        return TopCompetitorResponse(
            brand_id=brand_id,
            segment=segment,
            top_competitor_name=None,
            avg_awareness_score=None,
        )

    # Group by competitor and calculate average awareness
    competitor_scores: dict[str, list[float]] = {}
    for record in records:
        name = record.competitor_brand_name
        score = record.awareness_score or 0.0
        competitor_scores.setdefault(name, []).append(score)

    # Find competitor with highest average awareness
    best_competitor = None
    best_avg = -1.0
    for name, scores in competitor_scores.items():
        avg = sum(scores) / len(scores)
        if avg > best_avg:
            best_avg = avg
            best_competitor = name

    logger.info(
        f"Top competitor for brand_id: {brand_id}, segment: {segment}: "
        f"{best_competitor} (avg awareness: {round(best_avg, 2)})"
    )

    return TopCompetitorResponse(
        brand_id=brand_id,
        segment=segment,
        top_competitor_name=best_competitor,
        avg_awareness_score=round(best_avg, 2),
    )


# ── Signal type constants and mappings for insight endpoints ──────

INSIGHT_SIGNAL_TYPES = [
    "competitive_dominance_signal",
    "competitive_erosion_signal",
    "competitive_breakthrough_signal",
    "deceleration_warning_signal",
    "weak_structural_position_signal",
    "rank_displacement_signal",
    "fragile_leadership_signal",
    "volatility_spike_signal",
    "new_entrant_signal",
]

SIGNAL_DISPLAY_NAMES = {
    "competitive_dominance_signal": "Competitive Dominance Risk",
    "competitive_erosion_signal": "Competitive Erosion Risk",
    "competitive_breakthrough_signal": "Competitor Breakthrough Risk",
    "deceleration_warning_signal": "Growth Deceleration Risk",
    "weak_structural_position_signal": "Position Structure Weakness Risk",
    "rank_displacement_signal": "Rank Displacement Risk",
    "fragile_leadership_signal": "Fragile Leadership Risk",
    "volatility_spike_signal": "Visibility Volatility Risk",
    "new_entrant_signal": "New Entrant Risk",
}

SEVERITY_TO_INT = {"Low": 1, "Medium": 2, "High": 4}

SIGNAL_TYPE_TO_HISTORY_KEY = {
    "competitive_dominance_signal": "competitive_dominance",
    "competitive_erosion_signal": "competitive_erosion",
    "competitive_breakthrough_signal": "competitor_breakthrough",
    "deceleration_warning_signal": "growth_deceleration",
    "weak_structural_position_signal": "position_weakness",
    "rank_displacement_signal": "rank_displacement",
    "fragile_leadership_signal": "fragile_leadership",
    "volatility_spike_signal": "volatility_spike",
    "new_entrant_signal": "new_entrant",
}


@router.get("/risk-overview", response_model=BrandRiskOverviewResponse)
async def get_risk_overview(
    brand_id: str = Query(..., description="Brand ID to get risk overview for"),
    segment: str = Query("All-Segment", description="Segment to filter by"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """Get the latest severity for each of the 5 insight signal types."""
    logger.info(f"Getting risk overview for brand_id: {brand_id}, segment: {segment}")

    signals: list[InsightSignalSeverity] = []

    for signal_type in INSIGHT_SIGNAL_TYPES:
        query = (
            select(BrandPerformanceInsightTable)
            .where(
                BrandPerformanceInsightTable.search_target_brand_id == brand_id,
                BrandPerformanceInsightTable.segment == segment,
                BrandPerformanceInsightTable.signal_type == signal_type,
            )
            .order_by(desc(BrandPerformanceInsightTable.created_date))
            .limit(1)
        )
        result = await db.execute(query)
        record = result.scalar_one_or_none()

        if record:
            signals.append(InsightSignalSeverity(
                signal_type=signal_type,
                signal_name=SIGNAL_DISPLAY_NAMES[signal_type],
                severity=record.severity,
                signal_score=record.signal_score,
                business_meaning=record.business_meaning,
            ))
        else:
            signals.append(InsightSignalSeverity(
                signal_type=signal_type,
                signal_name=SIGNAL_DISPLAY_NAMES[signal_type],
                severity="Low",
                signal_score=0.0,
                business_meaning="No data available",
            ))

    return BrandRiskOverviewResponse(
        brand_id=brand_id,
        segment=segment,
        signals=signals,
    )


@router.get("/risk-history", response_model=RiskHistoryResponse)
async def get_risk_history(
    brand_id: str = Query(..., description="Brand ID to get risk history for"),
    segment: str = Query("All-Segment", description="Segment to filter by"),
    time_range: TimeRange = Query(TimeRange.ONE_MONTH, description="Time range"),
    start_date: Optional[date] = Query(None, description="Custom start date"),
    end_date: Optional[date] = Query(None, description="Custom end date"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """Get risk history time series with severity mapped to integers for charting."""
    logger.info(
        f"Getting risk history for brand_id: {brand_id}, segment: {segment}, "
        f"time_range: {time_range}"
    )

    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date and end_date are required for custom time range",
            )
        query_start_date = start_date
        query_end_date = end_date
    else:
        query_start_date, query_end_date = get_date_range_for_time_range(time_range)

    query = (
        select(BrandPerformanceInsightTable)
        .where(
            BrandPerformanceInsightTable.search_target_brand_id == brand_id,
            BrandPerformanceInsightTable.segment == segment,
            BrandPerformanceInsightTable.signal_type.in_(INSIGHT_SIGNAL_TYPES),
            BrandPerformanceInsightTable.created_date >= query_start_date,
            BrandPerformanceInsightTable.created_date <= query_end_date,
        )
        .order_by(asc(BrandPerformanceInsightTable.created_date))
    )

    result = await db.execute(query)
    records = result.scalars().all()

    # Group by date, pivot signal types into columns
    date_map: dict[str, dict[str, int]] = {}
    for record in records:
        date_str = record.created_date.isoformat()
        if date_str not in date_map:
            date_map[date_str] = {}
        history_key = SIGNAL_TYPE_TO_HISTORY_KEY.get(record.signal_type)
        if history_key:
            date_map[date_str][history_key] = SEVERITY_TO_INT.get(record.severity, 1)

    data_points = [
        RiskHistoryDataPoint(
            date=dt,
            competitive_dominance=cols.get("competitive_dominance"),
            competitive_erosion=cols.get("competitive_erosion"),
            competitor_breakthrough=cols.get("competitor_breakthrough"),
            growth_deceleration=cols.get("growth_deceleration"),
            position_weakness=cols.get("position_weakness"),
            rank_displacement=cols.get("rank_displacement"),
            fragile_leadership=cols.get("fragile_leadership"),
            volatility_spike=cols.get("volatility_spike"),
            new_entrant=cols.get("new_entrant"),
        )
        for dt, cols in sorted(date_map.items())
    ]

    return RiskHistoryResponse(
        brand_id=brand_id,
        segment=segment,
        data_points=data_points,
    )


@router.get("/brand-impression-summary", response_model=BrandImpressionSummaryResponse)
async def get_brand_impression_summary(
    brand_id: str = Query(..., description="Brand ID to query"),
    segment: str = Query(default="all-segment", description="Segment to filter by"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Retrieve the brand impression summary with 3 quick metrics for the selector card.

    Queries BrandSearchDailyBasicMetricsTable for the given brand and segment and returns
    visibility rate, median ranking position, and final sentiment score for the latest
    7-day window, plus comparison with the prior 7-day window.

    Visibility  = search_visibility_count / total_search_count * 100
    Position    = median_ranking (lower is better; null if brand never ranked)
    Sentiment   = final_sentiment_score (0-100, NULL if brand had no visibility)
    """
    logger.info(
        f"Fetching brand impression summary for user: {current_user.user_id}, "
        f"brand_id: {brand_id}, segment: {segment}"
    )

    # ── Current record: latest search_date_end for this brand + segment ──
    current_query = (
        select(BrandSearchDailyBasicMetricsTable)
        .where(
            BrandSearchDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchDailyBasicMetricsTable.segment == segment,
        )
        .order_by(desc(BrandSearchDailyBasicMetricsTable.search_date_end))
        .limit(1)
    )
    current_result = await db.execute(current_query)
    current_record = current_result.scalar_one_or_none()

    if not current_record:
        logger.warning(f"No brand impression data found for brand_id: {brand_id}")
        empty = BrandImpressionMetric(trend="no_data")
        return BrandImpressionSummaryResponse(
            brand_id=brand_id,
            brand_name="Unknown",
            visibility=empty,
            position=empty,
            sentiment=empty,
        )

    brand_name = current_record.search_target_brand_name
    current_end = current_record.search_date_end
    previous_end = current_end - timedelta(days=7)

    # ── Previous record: 7 days before current_end ────────────────────────────
    previous_query = (
        select(BrandSearchDailyBasicMetricsTable)
        .where(
            BrandSearchDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchDailyBasicMetricsTable.segment == segment,
            BrandSearchDailyBasicMetricsTable.search_date_end == previous_end,
        )
        .limit(1)
    )
    previous_result = await db.execute(previous_query)
    previous_record = previous_result.scalar_one_or_none()

    # ── Compute metric values ─────────────────────────────────────────────────
    def compute_visibility(rec) -> Optional[float]:
        if rec is None or rec.total_search_count == 0:
            return None
        return round(rec.search_visibility_count / rec.total_search_count * 100, 2)

    def compute_position(rec) -> Optional[float]:
        if rec is None or rec.search_visibility_count == 0:
            return None
        return float(rec.median_ranking)

    def compute_sentiment(rec) -> Optional[float]:
        if rec is None:
            return None
        return rec.final_sentiment_score  # may be None (no visibility)

    def make_metric(
        current_val: Optional[float],
        previous_val: Optional[float],
        higher_is_better: bool = True,
    ) -> BrandImpressionMetric:
        if current_val is None:
            return BrandImpressionMetric(trend="no_data")
        if previous_val is None:
            return BrandImpressionMetric(current_value=current_val, trend="no_data")
        change = round(current_val - previous_val, 2)
        if change > 0:
            trend = "up" if higher_is_better else "down"
        elif change < 0:
            trend = "down" if higher_is_better else "up"
        else:
            trend = "flat"
        return BrandImpressionMetric(
            current_value=current_val,
            previous_value=previous_val,
            change=change,
            trend=trend,
        )

    current_vis = compute_visibility(current_record)
    previous_vis = compute_visibility(previous_record)

    current_pos = compute_position(current_record)
    previous_pos = compute_position(previous_record)

    current_sent = compute_sentiment(current_record)
    previous_sent = compute_sentiment(previous_record)

    # Position: lower ranking number is better → higher_is_better=False
    visibility_metric = make_metric(current_vis, previous_vis, higher_is_better=True)
    position_metric = make_metric(current_pos, previous_pos, higher_is_better=False)
    sentiment_metric = make_metric(current_sent, previous_sent, higher_is_better=True)

    logger.info(
        f"Brand impression summary for brand_id: {brand_id}: "
        f"visibility={current_vis}, position={current_pos}, sentiment={current_sent}"
    )

    return BrandImpressionSummaryResponse(
        brand_id=brand_id,
        brand_name=brand_name,
        visibility=visibility_metric,
        position=position_metric,
        sentiment=sentiment_metric,
        current_period_end=current_end.isoformat(),
        previous_period_end=previous_end.isoformat() if previous_record else None,
    )


def _parse_text_list(text: str | None) -> list[str]:
    """Parse a Text/String field that may be JSON array, newline-, or semicolon-separated."""
    if not text or not text.strip():
        return []
    try:
        parsed = json_module.loads(text)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except (json_module.JSONDecodeError, ValueError):
        pass
    for sep in ["\n", ";", "|"]:
        parts = [p.strip() for p in text.split(sep) if p.strip()]
        if len(parts) > 1:
            return parts
    return [text.strip()] if text.strip() else []


def _extract_reference_sources(raw: str | None) -> list[str]:
    """
    Extract reference source URLs from a search_return_reference_sources value.

    Handles three cases:
      - JSON array of objects: each object may have a "url" key — extract it; otherwise str(item)
      - JSON array of strings: use each string directly
      - JSON object with a "url" key: extract that URL
      - Plain text (newline / semicolon / pipe separated): split and use as-is
    """
    if not raw or not raw.strip():
        return []
    try:
        parsed = json_module.loads(raw)
        results: list[str] = []
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict):
                    url = item.get("url") or item.get("URL") or item.get("href")
                    results.append(str(url).strip() if url else str(item).strip())
                elif item:
                    results.append(str(item).strip())
            return [r for r in results if r]
        if isinstance(parsed, dict):
            url = parsed.get("url") or parsed.get("URL") or parsed.get("href")
            return [str(url).strip()] if url else [str(parsed).strip()]
        return [str(parsed).strip()] if parsed else []
    except (json_module.JSONDecodeError, ValueError):
        pass
    # Fallback: plain-text splitting
    for sep in ["\n", ";", "|"]:
        parts = [p.strip() for p in raw.split(sep) if p.strip()]
        if len(parts) > 1:
            return parts
    return [raw.strip()] if raw.strip() else []


def _extract_customer_reviews(raw: str | None) -> list[tuple[str, str]]:
    """
    Extract (review_text, sentiment) pairs from a search_return_customer_review value.

    Handles:
      - JSON object with "text" and "sentiment" keys  → single pair
      - JSON array of such objects                    → multiple pairs
      - Plain text                                    → (text, "Unknown")

    Sentiment is title-cased and normalised to Positive / Neutral / Negative / Unknown.
    """
    VALID_SENTIMENTS = {"Positive", "Neutral", "Negative"}

    def _norm_sentiment(s: str) -> str:
        title = s.strip().title() if s else "Unknown"
        return title if title in VALID_SENTIMENTS else "Unknown"

    if not raw or not raw.strip():
        return []
    try:
        parsed = json_module.loads(raw)
        results: list[tuple[str, str]] = []
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict):
                    text = item.get("text") or item.get("review") or item.get("content") or ""
                    sentiment = item.get("sentiment") or item.get("label") or "Unknown"
                    if str(text).strip():
                        results.append((str(text).strip(), _norm_sentiment(str(sentiment))))
                elif item:
                    results.append((str(item).strip(), "Unknown"))
            return results
        if isinstance(parsed, dict):
            text = parsed.get("text") or parsed.get("review") or parsed.get("content") or ""
            sentiment = parsed.get("sentiment") or parsed.get("label") or "Unknown"
            if str(text).strip():
                return [(str(text).strip(), _norm_sentiment(str(sentiment)))]
            return []
        return [(str(parsed).strip(), "Unknown")] if str(parsed).strip() else []
    except (json_module.JSONDecodeError, ValueError):
        pass
    # Plain text fallback
    text = raw.strip()
    return [(text, "Unknown")] if text else []


@router.get("/brand-reference-sources", response_model=ReferenceSourcesResponse)
async def get_brand_reference_sources(
    brand_id: str = Query(..., description="Brand ID to query"),
    segment: Optional[str] = Query(None, description="Segment filter"),
    time_range: TimeRange = Query(TimeRange.ONE_MONTH),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Return deduplicated AI reference sources for rows where the brand appeared
    under its own name (search_target_brand_name == search_return_brand_name).

    Queries BrandSearchResultTable and aggregates search_return_reference_sources.
    JSON values are parsed and the "url" field is extracted where present.
    """
    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range",
            )
        query_start, query_end = start_date, end_date
    else:
        query_start, query_end = get_date_range_for_time_range(time_range)

    filters = [
        BrandSearchResultTable.search_target_brand_id == brand_id,
        # Only rows where the brand appeared under its own name
        BrandSearchResultTable.search_target_brand_name == BrandSearchResultTable.search_return_brand_name,
        BrandSearchResultTable.search_date >= query_start,
        BrandSearchResultTable.search_date <= query_end,
        BrandSearchResultTable.search_return_reference_sources.isnot(None),
    ]
    if segment and segment != "all-segment":
        filters.append(BrandSearchResultTable.segment == segment)

    query = (
        select(BrandSearchResultTable.search_return_reference_sources)
        .where(*filters)
        .order_by(desc(BrandSearchResultTable.search_date))
        .limit(500)
    )
    result = await db.execute(query)
    rows = result.fetchall()

    def _normalize_url(url: str) -> str:
        """Return a canonical form used only for dedup comparison (not stored)."""
        u = url.lower().strip()
        # Strip protocol for comparison: http/https treated as same
        for prefix in ("https://", "http://"):
            if u.startswith(prefix):
                u = u[len(prefix):]
                break
        # Strip www.
        if u.startswith("www."):
            u = u[4:]
        # Strip trailing slash
        u = u.rstrip("/")
        return u

    seen_normalized: set[str] = set()
    sources: list[str] = []
    for (raw,) in rows:
        for src in _extract_reference_sources(raw):
            key = _normalize_url(src)
            if key and key not in seen_normalized:
                seen_normalized.add(key)
                sources.append(src)

    items = [ReferenceSourceItem(seq=i + 1, source=s) for i, s in enumerate(sources)]
    return ReferenceSourcesResponse(brand_id=brand_id, sources=items)


@router.get("/brand-customer-reviews", response_model=CustomerReviewsResponse)
async def get_brand_customer_reviews(
    brand_id: str = Query(..., description="Brand ID to query"),
    segment: Optional[str] = Query(None, description="Segment filter"),
    time_range: TimeRange = Query(TimeRange.ONE_MONTH),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Return deduplicated customer reviews with sentiment from BrandSearchResultTable
    for rows where the brand appeared under its own name
    (search_target_brand_name == search_return_brand_name).

    JSON values in search_return_customer_review are parsed; "text" maps to the
    Customer Review column and "sentiment" maps to the Sentiment column.
    """
    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range",
            )
        query_start, query_end = start_date, end_date
    else:
        query_start, query_end = get_date_range_for_time_range(time_range)

    filters = [
        BrandSearchResultTable.search_target_brand_id == brand_id,
        BrandSearchResultTable.search_target_brand_name == BrandSearchResultTable.search_return_brand_name,
        BrandSearchResultTable.search_date >= query_start,
        BrandSearchResultTable.search_date <= query_end,
        BrandSearchResultTable.search_return_customer_review.isnot(None),
    ]
    if segment and segment != "all-segment":
        filters.append(BrandSearchResultTable.segment == segment)

    query = (
        select(BrandSearchResultTable.search_return_customer_review)
        .where(*filters)
        .order_by(desc(BrandSearchResultTable.search_date))
        .limit(500)
    )
    result = await db.execute(query)
    rows = result.fetchall()

    seen_normalized: set[str] = set()
    reviews: list[CustomerReviewItem] = []
    seq = 1
    for (raw,) in rows:
        for review_text, sentiment in _extract_customer_reviews(raw):
            # Deduplicate by normalised review text (lowercase, stripped)
            key = review_text.lower().strip()
            if key and key not in seen_normalized:
                seen_normalized.add(key)
                reviews.append(CustomerReviewItem(seq=seq, review=review_text, sentiment=sentiment))
                seq += 1

    return CustomerReviewsResponse(brand_id=brand_id, reviews=reviews)


@router.get("/brand-impression-trend", response_model=BrandImpressionTrendResponse)
async def get_brand_impression_trend(
    brand_id: str = Query(..., description="Brand ID to query"),
    segment: str = Query(default="all-segment", description="Segment to filter by"),
    time_range: TimeRange = Query(TimeRange.ONE_MONTH, description="Predefined time range"),
    start_date: Optional[date] = Query(None, description="Custom start date (when time_range=custom)"),
    end_date: Optional[date] = Query(None, description="Custom end date (when time_range=custom)"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Retrieve brand impression historical trend data from BrandSearchDailyBasicMetricsTable.

    Returns a time series of 3 key metrics ordered by date:
      - visibility: search_visibility_count / total_search_count * 100  (%)
      - position:   median_ranking  (lower is better; null when brand never ranked)
      - sentiment:  final_sentiment_score  (0-100; null when no reviews)

    Null values are forward/backward interpolated using the nearest adjacent records:
      - both neighbours present → average of the two
      - only previous → use previous value
      - only next     → use next value
      - no neighbours → remains null
    """
    logger.info(
        f"Fetching brand impression trend for user: {current_user.user_id}, "
        f"brand_id: {brand_id}, segment: {segment}, time_range: {time_range}"
    )

    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range",
            )
        query_start = start_date
        query_end = end_date
    else:
        query_start, query_end = get_date_range_for_time_range(time_range)

    query = (
        select(BrandSearchDailyBasicMetricsTable)
        .where(
            BrandSearchDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchDailyBasicMetricsTable.segment == segment,
            BrandSearchDailyBasicMetricsTable.search_date_end >= query_start,
            BrandSearchDailyBasicMetricsTable.search_date_end <= query_end,
        )
        .order_by(asc(BrandSearchDailyBasicMetricsTable.search_date_end))
    )
    result = await db.execute(query)
    records = result.scalars().all()

    if not records:
        logger.warning(f"No trend data found for brand_id: {brand_id}, segment: {segment}")
        return BrandImpressionTrendResponse(brand_id=brand_id, segment=segment, data_points=[])

    # ── Compute raw metric values (None where unavailable) ────────────────────
    raw: list[dict] = []
    for rec in records:
        vis = (
            None if rec.total_search_count == 0
            else round(rec.search_visibility_count / rec.total_search_count * 100, 2)
        )
        pos = (
            None if rec.search_visibility_count == 0 or rec.median_ranking is None
            else float(rec.median_ranking)
        )
        sent = rec.final_sentiment_score  # may be None
        raw.append({"date": rec.search_date_end.isoformat(), "visibility": vis, "position": pos, "sentiment": sent})

    # ── Interpolate nulls using adjacent non-null values ─────────────────────
    def interpolate_nulls(points: list[dict], key: str) -> None:
        vals = [p[key] for p in points]
        for i in range(len(vals)):
            if vals[i] is not None:
                continue
            prev_val = next((vals[j] for j in range(i - 1, -1, -1) if vals[j] is not None), None)
            next_val = next((vals[j] for j in range(i + 1, len(vals)) if vals[j] is not None), None)
            if prev_val is not None and next_val is not None:
                vals[i] = round((prev_val + next_val) / 2, 2)
            elif prev_val is not None:
                vals[i] = prev_val
            elif next_val is not None:
                vals[i] = next_val
            # both None → remains None
        for i, p in enumerate(points):
            p[key] = vals[i]

    interpolate_nulls(raw, "visibility")
    interpolate_nulls(raw, "position")
    interpolate_nulls(raw, "sentiment")

    data_points = [
        BrandImpressionTrendDataPoint(
            date=p["date"],
            visibility=p["visibility"],
            position=p["position"],
            sentiment=p["sentiment"],
        )
        for p in raw
    ]

    logger.info(f"Returning {len(data_points)} trend data points for brand_id: {brand_id}")
    return BrandImpressionTrendResponse(brand_id=brand_id, segment=segment, data_points=data_points)


@router.get("/brand-ranking-trend", response_model=BrandRankingTrendResponse)
async def get_brand_ranking_trend(
    brand_id: str = Query(..., description="Brand ID to query"),
    segment: str = Query(default="all-segment", description="Segment to filter by"),
    time_range: TimeRange = Query(TimeRange.ONE_MONTH, description="Predefined time range"),
    start_date: Optional[date] = Query(None, description="Custom start date (when time_range=custom)"),
    end_date: Optional[date] = Query(None, description="Custom end date (when time_range=custom)"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Retrieve brand ranking trend data (min, max, median, avg) from BrandSearchDailyBasicMetricsTable.

    Days where the brand had no visibility (search_visibility_count == 0) are marked
    is_interpolated=True and their values are filled using true linear interpolation:
      - Between two known points: rank = left + t * (right - left)
      - Before the first known point: flat-extend using the first known value
      - After the last known point: flat-extend using the last known value

    The frontend renders interpolated points as connected chart segments but shows
    "No ranking data (brand not found)" in the tooltip instead of actual values.
    """
    logger.info(
        f"Fetching brand ranking trend for user: {current_user.user_id}, "
        f"brand_id: {brand_id}, segment: {segment}, time_range: {time_range}"
    )

    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range",
            )
        query_start = start_date
        query_end = end_date
    else:
        query_start, query_end = get_date_range_for_time_range(time_range)

    query = (
        select(BrandSearchDailyBasicMetricsTable)
        .where(
            BrandSearchDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchDailyBasicMetricsTable.segment == segment,
            BrandSearchDailyBasicMetricsTable.search_date_end >= query_start,
            BrandSearchDailyBasicMetricsTable.search_date_end <= query_end,
        )
        .order_by(asc(BrandSearchDailyBasicMetricsTable.search_date_end))
    )
    result = await db.execute(query)
    records = result.scalars().all()

    if not records:
        logger.warning(f"No ranking trend data for brand_id: {brand_id}, segment: {segment}")
        return BrandRankingTrendResponse(brand_id=brand_id, segment=segment, data_points=[])

    # ── Compute raw values; null when brand had no visibility ─────────────────
    raw: list[dict] = []
    for rec in records:
        has_data = rec.search_visibility_count > 0
        raw.append({
            "date": rec.search_date_end.isoformat(),
            "min_ranking": float(rec.min_ranking) if has_data and rec.min_ranking is not None else None,
            "max_ranking": float(rec.max_ranking) if has_data and rec.max_ranking is not None else None,
            "median_ranking": float(rec.median_ranking) if has_data and rec.median_ranking is not None else None,
            "avg_ranking": round(float(rec.avg_ranking), 2) if has_data and rec.avg_ranking is not None else None,
            "is_interpolated": not has_data,
        })

    # ── Linear interpolation for null-valued metrics ──────────────────────────
    def linear_interpolate(points: list[dict], key: str) -> None:
        vals = [p[key] for p in points]
        known = [i for i, v in enumerate(vals) if v is not None]
        if not known:
            return

        # Flat-extend before the first known value
        for i in range(known[0]):
            vals[i] = vals[known[0]]

        # Flat-extend after the last known value
        for i in range(known[-1] + 1, len(vals)):
            vals[i] = vals[known[-1]]

        # True linear interpolation between consecutive known pairs
        for k in range(len(known) - 1):
            left, right = known[k], known[k + 1]
            if right - left > 1:
                left_val, right_val = vals[left], vals[right]
                for i in range(left + 1, right):
                    t = (i - left) / (right - left)
                    vals[i] = round(left_val + t * (right_val - left_val), 2)

        for i, p in enumerate(points):
            p[key] = vals[i]

    linear_interpolate(raw, "min_ranking")
    linear_interpolate(raw, "max_ranking")
    linear_interpolate(raw, "median_ranking")
    linear_interpolate(raw, "avg_ranking")

    data_points = [
        BrandRankingTrendDataPoint(
            date=p["date"],
            min_ranking=p["min_ranking"],
            max_ranking=p["max_ranking"],
            median_ranking=p["median_ranking"],
            avg_ranking=p["avg_ranking"],
            is_interpolated=p["is_interpolated"],
        )
        for p in raw
    ]

    logger.info(f"Returning {len(data_points)} ranking trend points for brand_id: {brand_id}")
    return BrandRankingTrendResponse(brand_id=brand_id, segment=segment, data_points=data_points)


# ── Competitor list filtered by segment ──────────────────────────────────────

@router.get("/competitors-by-segment", response_model=CompetitorsBySegmentResponse)
async def get_competitors_by_segment(
    brand_id: str = Query(..., description="Brand ID to query"),
    segment: str = Query(..., description="Segment name; use 'all-segment' to get all competitors regardless of segment"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Return distinct competitor names for a brand filtered by segment.

    When segment == 'all-segment', returns every competitor for the brand
    regardless of segment (distinct names).  Otherwise filters by the exact
    segment value from brand_competitors.
    """
    logger.info(
        f"Fetching competitors by segment for brand_id: {brand_id}, segment: {segment}"
    )

    if segment == "all-segment":
        query = (
            select(distinct(BrandCompetitorsTable.competitor_brand_name))
            .where(BrandCompetitorsTable.brand_id == brand_id)
            .order_by(BrandCompetitorsTable.competitor_brand_name)
        )
    else:
        query = (
            select(BrandCompetitorsTable.competitor_brand_name)
            .where(
                BrandCompetitorsTable.brand_id == brand_id,
                BrandCompetitorsTable.segment == segment,
            )
            .order_by(BrandCompetitorsTable.competitor_brand_name)
        )

    result = await db.execute(query)
    competitor_names = [row[0] for row in result.all()]

    logger.info(
        f"Found {len(competitor_names)} competitors for brand_id: {brand_id}, segment: {segment}"
    )

    return CompetitorsBySegmentResponse(
        brand_id=brand_id,
        segment=segment,
        competitor_names=competitor_names,
    )


# ── Competitor gap summary (current window vs 7-day-prior window) ─────────────

def _make_gap_metric(
    current_gap: Optional[float],
    previous_gap: Optional[float],
    higher_is_better: bool = True,
) -> CompetitorGapMetric:
    """
    Build a CompetitorGapMetric from current and previous gap values.
    trend = 'up' when the gap improved, 'down' when it worsened.
    For higher_is_better metrics (visibility, sentiment): up = gap increased.
    For lower_is_better metrics (position): up = gap increased (already inverted at call site).
    """
    if current_gap is None:
        return CompetitorGapMetric(trend="no_data")

    change: Optional[float] = None
    trend = "flat"

    if previous_gap is not None:
        change = round(current_gap - previous_gap, 4)
        if abs(change) < 0.001:
            trend = "flat"
        elif higher_is_better:
            trend = "up" if change > 0 else "down"
        else:
            trend = "up" if change < 0 else "down"

    return CompetitorGapMetric(
        gap_value=round(current_gap, 4),
        previous_gap_value=round(previous_gap, 4) if previous_gap is not None else None,
        change=round(change, 4) if change is not None else None,
        trend=trend,
    )


@router.get("/competitor-gap-summary", response_model=CompetitorGapSummaryResponse)
async def get_competitor_gap_summary(
    brand_id: str = Query(..., description="My brand ID"),
    segment: str = Query(..., description="Segment; use 'all-segment' for the rollup row"),
    competitor_brand_name: str = Query(..., description="Competitor brand name"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Return visibility, position, and sentiment gap between my brand and a competitor.

    Fetches the two most recent distinct search_date_end windows from
    brand_competitors_daily_basic_metrics and brand_search_basic_metrics_daily,
    then computes:
      - visibility_gap   = my_visibility_rate  - competitor_visibility_rate  (higher = better)
      - position_gap     = competitor_median_ranking - my_median_ranking      (higher = I rank better)
      - sentiment_gap    = my_sentiment_score  - competitor_sentiment_score   (higher = better)

    trend icon logic: 'up' = gap improved vs 7 days ago.
    """
    logger.info(
        f"Fetching competitor gap summary for brand_id: {brand_id}, "
        f"segment: {segment}, competitor: {competitor_brand_name}"
    )

    # ── Fetch the two most recent competitor metric windows ────────────────────
    comp_query = (
        select(BrandSearchCompetitorDailyBasicMetricsTable)
        .where(
            BrandSearchCompetitorDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchCompetitorDailyBasicMetricsTable.segment == segment,
            BrandSearchCompetitorDailyBasicMetricsTable.competitor_brand_name == competitor_brand_name,
        )
        .order_by(BrandSearchCompetitorDailyBasicMetricsTable.search_date_end.desc())
        .limit(2)
    )
    comp_result = await db.execute(comp_query)
    comp_records = comp_result.scalars().all()

    if not comp_records:
        empty = CompetitorGapMetric(trend="no_data")
        return CompetitorGapSummaryResponse(
            brand_id=brand_id,
            segment=segment,
            competitor_brand_name=competitor_brand_name,
            visibility_gap=empty,
            position_gap=empty,
            sentiment_gap=empty,
        )

    current_comp = comp_records[0]
    previous_comp = comp_records[1] if len(comp_records) > 1 else None

    # ── Fetch matching brand metric windows ────────────────────────────────────
    brand_dates = [current_comp.search_date_end]
    if previous_comp:
        brand_dates.append(previous_comp.search_date_end)

    brand_query = (
        select(BrandSearchDailyBasicMetricsTable)
        .where(
            BrandSearchDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchDailyBasicMetricsTable.segment == segment,
            BrandSearchDailyBasicMetricsTable.search_date_end.in_(brand_dates),
        )
        .order_by(BrandSearchDailyBasicMetricsTable.search_date_end.desc())
    )
    brand_result = await db.execute(brand_query)
    brand_records = brand_result.scalars().all()

    brand_by_date = {r.search_date_end: r for r in brand_records}
    current_brand = brand_by_date.get(current_comp.search_date_end)
    previous_brand = brand_by_date.get(previous_comp.search_date_end) if previous_comp else None

    # ── Compute visibility rates ───────────────────────────────────────────────
    def vis_rate(brand_rec, comp_rec) -> Optional[float]:
        """Visibility rate = count / total * 100. Uses shared total_search_count."""
        if brand_rec is None or comp_rec is None:
            return None
        total = comp_rec.total_search_count
        if not total:
            return None
        my_rate = (brand_rec.search_visibility_count / total) * 100
        comp_rate = (comp_rec.competitor_visibility_count / total) * 100
        return my_rate - comp_rate

    current_vis_gap = vis_rate(current_brand, current_comp)
    previous_vis_gap = vis_rate(previous_brand, previous_comp) if previous_comp else None

    # ── Compute position gaps ──────────────────────────────────────────────────
    def pos_gap(brand_rec, comp_rec) -> Optional[float]:
        """competitor_median - my_median; positive = my brand ranks better (lower position number)."""
        if brand_rec is None or comp_rec is None:
            return None
        if brand_rec.median_ranking == 0 or comp_rec.median_ranking == 0:
            return None
        return float(comp_rec.median_ranking) - float(brand_rec.median_ranking)

    current_pos_gap = pos_gap(current_brand, current_comp)
    previous_pos_gap = pos_gap(previous_brand, previous_comp) if previous_comp else None

    # ── Compute sentiment gaps ─────────────────────────────────────────────────
    def sent_gap(brand_rec, comp_rec) -> Optional[float]:
        if brand_rec is None or comp_rec is None:
            return None
        if brand_rec.final_sentiment_score is None or comp_rec.final_sentiment_score is None:
            return None
        return float(brand_rec.final_sentiment_score) - float(comp_rec.final_sentiment_score)

    current_sent_gap = sent_gap(current_brand, current_comp)
    previous_sent_gap = sent_gap(previous_brand, previous_comp) if previous_comp else None

    # ── Build response ─────────────────────────────────────────────────────────
    return CompetitorGapSummaryResponse(
        brand_id=brand_id,
        segment=segment,
        competitor_brand_name=competitor_brand_name,
        visibility_gap=_make_gap_metric(current_vis_gap, previous_vis_gap, higher_is_better=True),
        position_gap=_make_gap_metric(current_pos_gap, previous_pos_gap, higher_is_better=True),
        sentiment_gap=_make_gap_metric(current_sent_gap, previous_sent_gap, higher_is_better=True),
        current_period_end=current_comp.search_date_end.isoformat(),
        previous_period_end=previous_comp.search_date_end.isoformat() if previous_comp else None,
    )


# ── Competitor gap historical trend ───────────────────────────────────────────


@router.get("/competitor-gap-trend", response_model=CompetitorGapTrendResponse)
async def get_competitor_gap_trend(
    brand_id: str = Query(..., description="My brand ID"),
    segment: str = Query(..., description="Segment; use 'all-segment' for the rollup row"),
    competitor_brand_name: str = Query(..., description="Competitor brand name"),
    time_range: TimeRange = Query(TimeRange.ONE_MONTH, description="Predefined time range"),
    start_date: Optional[date] = Query(None, description="Custom start date (when time_range=custom)"),
    end_date: Optional[date] = Query(None, description="Custom end date (when time_range=custom)"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Return time-series gap metrics between my brand and a competitor.

    For each date window in the selected range, computes:
      - visibility_gap   = my_visibility%  - competitor_visibility%   (positive = I appear more)
      - position_gap     = competitor_median_rank - my_median_rank     (positive = I rank better)
      - sentiment_gap    = my_sentiment    - competitor_sentiment      (positive = I'm perceived better)

    Gaps are computed only for dates where both brand and competitor records exist.
    """
    logger.info(
        f"Fetching competitor gap trend for brand_id: {brand_id}, segment: {segment}, "
        f"competitor: {competitor_brand_name}, time_range: {time_range}"
    )

    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range",
            )
        query_start = start_date
        query_end = end_date
    else:
        query_start, query_end = get_date_range_for_time_range(time_range)

    # ── Fetch brand metrics over date range ────────────────────────────────────
    brand_query = (
        select(BrandSearchDailyBasicMetricsTable)
        .where(
            BrandSearchDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchDailyBasicMetricsTable.segment == segment,
            BrandSearchDailyBasicMetricsTable.search_date_end >= query_start,
            BrandSearchDailyBasicMetricsTable.search_date_end <= query_end,
        )
        .order_by(asc(BrandSearchDailyBasicMetricsTable.search_date_end))
    )
    brand_result = await db.execute(brand_query)
    brand_by_date = {r.search_date_end: r for r in brand_result.scalars().all()}

    # ── Fetch competitor metrics over date range ────────────────────────────────
    comp_query = (
        select(BrandSearchCompetitorDailyBasicMetricsTable)
        .where(
            BrandSearchCompetitorDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchCompetitorDailyBasicMetricsTable.segment == segment,
            BrandSearchCompetitorDailyBasicMetricsTable.competitor_brand_name == competitor_brand_name,
            BrandSearchCompetitorDailyBasicMetricsTable.search_date_end >= query_start,
            BrandSearchCompetitorDailyBasicMetricsTable.search_date_end <= query_end,
        )
        .order_by(asc(BrandSearchCompetitorDailyBasicMetricsTable.search_date_end))
    )
    comp_result = await db.execute(comp_query)
    comp_by_date = {r.search_date_end: r for r in comp_result.scalars().all()}

    if not brand_by_date and not comp_by_date:
        return CompetitorGapTrendResponse(
            brand_id=brand_id,
            segment=segment,
            competitor_brand_name=competitor_brand_name,
            data_points=[],
        )

    # ── Compute gap for each date where both records exist ─────────────────────
    all_dates = sorted(set(brand_by_date.keys()) & set(comp_by_date.keys()))

    data_points: list[CompetitorGapTrendDataPoint] = []
    for d in all_dates:
        brand_rec = brand_by_date[d]
        comp_rec = comp_by_date[d]

        # Raw visibility values
        brand_vis: Optional[float] = None
        comp_vis: Optional[float] = None
        vis_gap: Optional[float] = None
        if comp_rec.total_search_count:
            brand_vis = round(brand_rec.search_visibility_count / comp_rec.total_search_count * 100, 2)
            comp_vis = round(comp_rec.competitor_visibility_count / comp_rec.total_search_count * 100, 2)
            vis_gap = round(brand_vis - comp_vis, 2)

        # Raw ranking values and gap
        brand_median: Optional[float] = float(brand_rec.median_ranking) if brand_rec.median_ranking else None
        comp_median: Optional[float] = float(comp_rec.median_ranking) if comp_rec.median_ranking else None
        pos_gap: Optional[float] = None
        if brand_median is not None and comp_median is not None:
            pos_gap = round(comp_median - brand_median, 2)

        # Raw sentiment values and gap
        brand_sent: Optional[float] = (
            float(brand_rec.final_sentiment_score) if brand_rec.final_sentiment_score is not None else None
        )
        comp_sent: Optional[float] = (
            float(comp_rec.final_sentiment_score) if comp_rec.final_sentiment_score is not None else None
        )
        sent_gap: Optional[float] = None
        if brand_sent is not None and comp_sent is not None:
            sent_gap = round(brand_sent - comp_sent, 2)

        data_points.append(CompetitorGapTrendDataPoint(
            date=d.isoformat(),
            brand_visibility=brand_vis,
            comp_visibility=comp_vis,
            brand_median_ranking=brand_median,
            comp_median_ranking=comp_median,
            brand_sentiment=brand_sent,
            comp_sentiment=comp_sent,
            visibility_gap=vis_gap,
            position_gap=pos_gap,
            sentiment_gap=sent_gap,
        ))

    logger.info(
        f"Returning {len(data_points)} gap trend points for brand_id: {brand_id}, "
        f"competitor: {competitor_brand_name}"
    )
    return CompetitorGapTrendResponse(
        brand_id=brand_id,
        segment=segment,
        competitor_brand_name=competitor_brand_name,
        data_points=data_points,
    )


# ── Competitor ranking detail (brand vs competitor high/low/median/avg) ────────


@router.get("/competitor-ranking-detail", response_model=CompetitorRankingDetailResponse)
async def get_competitor_ranking_detail(
    brand_id: str = Query(..., description="My brand ID"),
    segment: str = Query(..., description="Segment; use 'all-segment' for the rollup row"),
    competitor_brand_name: str = Query(..., description="Competitor brand name"),
    time_range: TimeRange = Query(TimeRange.ONE_MONTH, description="Predefined time range"),
    start_date: Optional[date] = Query(None, description="Custom start date (when time_range=custom)"),
    end_date: Optional[date] = Query(None, description="Custom end date (when time_range=custom)"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Return time-series ranking stats (best/worst/median/avg) for both brand and competitor.

    Ranking is lower-is-better (#1 = best). Zero values from the DB mean the brand had
    no visibility in that window and are returned as null.

    Brand columns  : min_ranking (best), max_ranking (worst), median_ranking, avg_ranking
    Competitor cols: high_ranking (best), low_ranking (worst), median_ranking, avg_ranking
    """
    logger.info(
        f"Fetching competitor ranking detail for brand_id: {brand_id}, segment: {segment}, "
        f"competitor: {competitor_brand_name}, time_range: {time_range}"
    )

    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range",
            )
        query_start = start_date
        query_end = end_date
    else:
        query_start, query_end = get_date_range_for_time_range(time_range)

    # ── Fetch brand ranking records ────────────────────────────────────────────
    brand_query = (
        select(BrandSearchDailyBasicMetricsTable)
        .where(
            BrandSearchDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchDailyBasicMetricsTable.segment == segment,
            BrandSearchDailyBasicMetricsTable.search_date_end >= query_start,
            BrandSearchDailyBasicMetricsTable.search_date_end <= query_end,
        )
        .order_by(asc(BrandSearchDailyBasicMetricsTable.search_date_end))
    )
    brand_result = await db.execute(brand_query)
    brand_by_date = {r.search_date_end: r for r in brand_result.scalars().all()}

    # ── Fetch competitor ranking records ───────────────────────────────────────
    comp_query = (
        select(BrandSearchCompetitorDailyBasicMetricsTable)
        .where(
            BrandSearchCompetitorDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchCompetitorDailyBasicMetricsTable.segment == segment,
            BrandSearchCompetitorDailyBasicMetricsTable.competitor_brand_name == competitor_brand_name,
            BrandSearchCompetitorDailyBasicMetricsTable.search_date_end >= query_start,
            BrandSearchCompetitorDailyBasicMetricsTable.search_date_end <= query_end,
        )
        .order_by(asc(BrandSearchCompetitorDailyBasicMetricsTable.search_date_end))
    )
    comp_result = await db.execute(comp_query)
    comp_by_date = {r.search_date_end: r for r in comp_result.scalars().all()}

    if not brand_by_date and not comp_by_date:
        return CompetitorRankingDetailResponse(
            brand_id=brand_id, segment=segment,
            competitor_brand_name=competitor_brand_name, data_points=[],
        )

    def _rank_or_none(value: int | float) -> Optional[float]:
        """Return None when value == 0 (means no visibility in that window)."""
        return None if not value else float(value)

    # ── Build data points for dates where at least one side has data ───────────
    all_dates = sorted(set(brand_by_date.keys()) | set(comp_by_date.keys()))
    data_points: list[CompetitorRankingDetailDataPoint] = []

    for d in all_dates:
        br = brand_by_date.get(d)
        cr = comp_by_date.get(d)

        brand_best = int(br.min_ranking) if br and br.min_ranking else None
        brand_worst = int(br.max_ranking) if br and br.max_ranking else None
        brand_avg = round(float(br.avg_ranking), 2) if br and br.avg_ranking else None

        comp_best = int(cr.high_ranking) if cr and cr.high_ranking else None
        comp_worst = int(cr.low_ranking) if cr and cr.low_ranking else None
        comp_avg = round(float(cr.avg_ranking), 2) if cr and cr.avg_ranking else None

        # Gaps: comp - brand (positive = brand ranks better / lower position number)
        best_gap = round(float(comp_best) - float(brand_best), 2) if brand_best and comp_best else None
        worst_gap = round(float(comp_worst) - float(brand_worst), 2) if brand_worst and comp_worst else None
        avg_gap = round(comp_avg - brand_avg, 2) if brand_avg and comp_avg else None

        data_points.append(CompetitorRankingDetailDataPoint(
            date=d.isoformat(),
            brand_best=brand_best,
            brand_worst=brand_worst,
            brand_avg=brand_avg,
            comp_best=comp_best,
            comp_worst=comp_worst,
            comp_avg=comp_avg,
            best_gap=best_gap,
            worst_gap=worst_gap,
            avg_gap=avg_gap,
        ))

    logger.info(
        f"Returning {len(data_points)} ranking detail points for brand_id: {brand_id}, "
        f"competitor: {competitor_brand_name}"
    )
    return CompetitorRankingDetailResponse(
        brand_id=brand_id,
        segment=segment,
        competitor_brand_name=competitor_brand_name,
        data_points=data_points,
    )


# ── Sentiment comparison (brand vs competitor customer reviews) ─────────────


@router.get("/sentiment-comparison", response_model=SentimentComparisonResponse)
async def get_sentiment_comparison(
    brand_id: str = Query(..., description="My brand ID"),
    segment: str = Query(..., description="Segment; use 'all-segment' for all segments combined"),
    competitor_brand_name: str = Query(..., description="Competitor brand name"),
    time_range: TimeRange = Query(TimeRange.ONE_MONTH, description="Predefined time range"),
    start_date: Optional[date] = Query(None, description="Custom start date (when time_range=custom)"),
    end_date: Optional[date] = Query(None, description="Custom end date (when time_range=custom)"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Return side-by-side brand vs competitor customer reviews from BrandSearchResultTable.

    Brand reviews   : rows where search_return_brand_name == search_target_brand_name
    Competitor reviews: rows where search_return_brand_name == competitor_brand_name

    Reviews are deduped, grouped by sentiment (Positive → Neutral → Negative → Unknown),
    then zipped into paired rows. Where one side has more reviews than the other, the
    missing side is returned as an empty string.
    """
    logger.info(
        f"Fetching sentiment comparison for brand_id: {brand_id}, segment: {segment}, "
        f"competitor: {competitor_brand_name}, time_range: {time_range}"
    )

    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range",
            )
        query_start, query_end = start_date, end_date
    else:
        query_start, query_end = get_date_range_for_time_range(time_range)

    # ── Fetch brand reviews (brand appears under its own name) ─────────────────
    brand_filters = [
        BrandSearchResultTable.search_target_brand_id == brand_id,
        BrandSearchResultTable.search_target_brand_name == BrandSearchResultTable.search_return_brand_name,
        BrandSearchResultTable.search_date >= query_start,
        BrandSearchResultTable.search_date <= query_end,
        BrandSearchResultTable.search_return_customer_review.isnot(None),
    ]
    if segment != "all-segment":
        brand_filters.append(BrandSearchResultTable.segment == segment)

    brand_query = (
        select(BrandSearchResultTable.search_return_customer_review)
        .where(*brand_filters)
        .order_by(desc(BrandSearchResultTable.search_date))
        .limit(500)
    )
    brand_result = await db.execute(brand_query)
    brand_raw_rows = brand_result.fetchall()

    # ── Fetch competitor reviews ───────────────────────────────────────────────
    comp_filters = [
        BrandSearchResultTable.search_target_brand_id == brand_id,
        BrandSearchResultTable.search_return_brand_name == competitor_brand_name,
        BrandSearchResultTable.search_date >= query_start,
        BrandSearchResultTable.search_date <= query_end,
        BrandSearchResultTable.search_return_customer_review.isnot(None),
    ]
    if segment != "all-segment":
        comp_filters.append(BrandSearchResultTable.segment == segment)

    comp_query = (
        select(BrandSearchResultTable.search_return_customer_review)
        .where(*comp_filters)
        .order_by(desc(BrandSearchResultTable.search_date))
        .limit(500)
    )
    comp_result = await db.execute(comp_query)
    comp_raw_rows = comp_result.fetchall()

    # ── Parse and deduplicate ──────────────────────────────────────────────────
    def _deduplicated_reviews(raw_rows: list) -> list[tuple[str, str]]:
        seen: set[str] = set()
        reviews: list[tuple[str, str]] = []
        for (raw,) in raw_rows:
            for review_text, sentiment in _extract_customer_reviews(raw):
                key = review_text.lower().strip()
                if key and key not in seen:
                    seen.add(key)
                    reviews.append((review_text, sentiment))
        return reviews

    brand_reviews = _deduplicated_reviews(brand_raw_rows)
    comp_reviews = _deduplicated_reviews(comp_raw_rows)

    # ── Group by sentiment ─────────────────────────────────────────────────────
    SENTIMENT_ORDER = ["Positive", "Neutral", "Negative", "Unknown"]
    brand_by_sentiment: dict[str, list[str]] = {s: [] for s in SENTIMENT_ORDER}
    for review_text, sentiment in brand_reviews:
        bucket = sentiment if sentiment in brand_by_sentiment else "Unknown"
        brand_by_sentiment[bucket].append(review_text)

    comp_by_sentiment: dict[str, list[str]] = {s: [] for s in SENTIMENT_ORDER}
    for review_text, sentiment in comp_reviews:
        bucket = sentiment if sentiment in comp_by_sentiment else "Unknown"
        comp_by_sentiment[bucket].append(review_text)

    # ── Zip into paired rows ───────────────────────────────────────────────────
    rows: list[SentimentComparisonRow] = []
    for sentiment in SENTIMENT_ORDER:
        b_list = brand_by_sentiment[sentiment]
        c_list = comp_by_sentiment[sentiment]
        max_len = max(len(b_list), len(c_list), 0)
        for i in range(max_len):
            rows.append(SentimentComparisonRow(
                sentiment=sentiment,
                brand_review=b_list[i] if i < len(b_list) else "",
                comp_review=c_list[i] if i < len(c_list) else "",
            ))

    logger.info(
        f"Returning {len(rows)} sentiment comparison rows for brand_id: {brand_id}, "
        f"competitor: {competitor_brand_name}"
    )
    return SentimentComparisonResponse(
        brand_id=brand_id,
        segment=segment,
        competitor_brand_name=competitor_brand_name,
        rows=rows,
    )


# ── Reference source comparison (brand vs competitor) ─────────────────────────


@router.get("/reference-source-comparison", response_model=ReferenceSourceComparisonResponse)
async def get_reference_source_comparison(
    brand_id: str = Query(..., description="My brand ID"),
    segment: str = Query(..., description="Segment; use 'all-segment' for all segments combined"),
    competitor_brand_name: str = Query(..., description="Competitor brand name"),
    time_range: TimeRange = Query(TimeRange.ONE_MONTH, description="Predefined time range"),
    start_date: Optional[date] = Query(None, description="Custom start date (when time_range=custom)"),
    end_date: Optional[date] = Query(None, description="Custom end date (when time_range=custom)"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Return a categorised comparison of reference sources for brand vs competitor.

    Brand sources   : rows where search_return_brand_name == search_target_brand_name
    Competitor sources: rows where search_return_brand_name == competitor_brand_name

    Each row is tagged with a category:
      - 'common'     : URL appears in both brand and competitor (deduped by normalised URL)
      - 'brand_only' : URL appears only in brand
      - 'comp_only'  : URL appears only in competitor

    Rows are ordered: common first, then brand_only, then comp_only.
    """
    logger.info(
        f"Fetching reference source comparison for brand_id: {brand_id}, segment: {segment}, "
        f"competitor: {competitor_brand_name}, time_range: {time_range}"
    )

    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range",
            )
        query_start, query_end = start_date, end_date
    else:
        query_start, query_end = get_date_range_for_time_range(time_range)

    def _normalize_url(url: str) -> str:
        u = url.lower().strip()
        for prefix in ("https://", "http://"):
            if u.startswith(prefix):
                u = u[len(prefix):]
                break
        if u.startswith("www."):
            u = u[4:]
        return u.rstrip("/")

    async def _fetch_sources(extra_filters: list) -> dict[str, str]:
        """Return {normalized_url: original_url} (first occurrence wins)."""
        base_filters = [
            BrandSearchResultTable.search_target_brand_id == brand_id,
            BrandSearchResultTable.search_date >= query_start,
            BrandSearchResultTable.search_date <= query_end,
            BrandSearchResultTable.search_return_reference_sources.isnot(None),
        ]
        if segment != "all-segment":
            base_filters.append(BrandSearchResultTable.segment == segment)

        q = (
            select(BrandSearchResultTable.search_return_reference_sources)
            .where(*(base_filters + extra_filters))
            .order_by(desc(BrandSearchResultTable.search_date))
            .limit(500)
        )
        result = await db.execute(q)
        sources_map: dict[str, str] = {}
        for (raw,) in result.fetchall():
            for src in _extract_reference_sources(raw):
                key = _normalize_url(src)
                if key and key not in sources_map:
                    sources_map[key] = src
        return sources_map

    brand_map = await _fetch_sources([
        BrandSearchResultTable.search_target_brand_name == BrandSearchResultTable.search_return_brand_name,
    ])
    comp_map = await _fetch_sources([
        BrandSearchResultTable.search_return_brand_name == competitor_brand_name,
    ])

    # ── Categorise ────────────────────────────────────────────────────────────
    brand_keys = set(brand_map.keys())
    comp_keys = set(comp_map.keys())
    common_keys = brand_keys & comp_keys
    brand_only_keys = brand_keys - common_keys
    comp_only_keys = comp_keys - brand_keys

    rows: list[ReferenceSourceComparisonRow] = []
    seq = 1

    for key in sorted(common_keys):
        rows.append(ReferenceSourceComparisonRow(
            seq=seq, category="common",
            brand_source=brand_map[key], comp_source=comp_map[key],
        ))
        seq += 1

    for key in sorted(brand_only_keys):
        rows.append(ReferenceSourceComparisonRow(
            seq=seq, category="brand_only",
            brand_source=brand_map[key], comp_source="",
        ))
        seq += 1

    for key in sorted(comp_only_keys):
        rows.append(ReferenceSourceComparisonRow(
            seq=seq, category="comp_only",
            brand_source="", comp_source=comp_map[key],
        ))
        seq += 1

    logger.info(
        f"Returning {len(rows)} reference source comparison rows "
        f"({len(common_keys)} common, {len(brand_only_keys)} brand-only, {len(comp_only_keys)} comp-only) "
        f"for brand_id: {brand_id}, competitor: {competitor_brand_name}"
    )
    return ReferenceSourceComparisonResponse(
        brand_id=brand_id,
        segment=segment,
        competitor_brand_name=competitor_brand_name,
        rows=rows,
    )


@router.get("/market-dynamic", response_model=MarketDynamicResponse)
async def get_market_dynamic(
    brand_id: str = Query(..., description="Target brand ID"),
    segment: str = Query(..., description="Segment name (e.g. 'All-Segment' or specific segment)"),
    time_range: TimeRange = Query(
        TimeRange.ONE_MONTH,
        description="Predefined time range for the query"
    ),
    start_date: Optional[date] = Query(
        None,
        description="Custom start date (required if time_range is 'custom')"
    ),
    end_date: Optional[date] = Query(
        None,
        description="Custom end date (required if time_range is 'custom')"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
) -> MarketDynamicResponse:
    """
    Retrieve market dynamic data for the target brand and all its competitors.

    Returns time-series visibility_share, search_momentum, and position_strength
    for the target brand plus every competitor, suitable for rendering pie, stacked
    area, line/bar, and quadrant charts on the Market Dynamic page.
    """
    logger.info(
        f"Fetching market dynamic for user: {current_user.user_id}, "
        f"brand_id: {brand_id}, segment: {segment}, time_range: {time_range}"
    )

    # Determine date range
    if time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date are required for custom time range",
            )
        query_start = start_date
        query_end = end_date
    else:
        query_start, query_end = get_date_range_for_time_range(time_range)

    # ── Query target brand daily performance ──────────────────────────────────
    brand_query = (
        select(BrandAwarenessDailyPerformanceTable)
        .where(
            BrandAwarenessDailyPerformanceTable.brand_id == brand_id,
            BrandAwarenessDailyPerformanceTable.segment == segment,
            BrandAwarenessDailyPerformanceTable.search_date >= query_start,
            BrandAwarenessDailyPerformanceTable.search_date <= query_end,
        )
        .order_by(asc(BrandAwarenessDailyPerformanceTable.search_date))
    )
    brand_result = await db.execute(brand_query)
    brand_rows = brand_result.scalars().all()

    # Get brand name from first row (fallback to brand_id)
    brand_name = brand_rows[0].brand_name if brand_rows else brand_id

    # ── Query all competitors daily performance ───────────────────────────────
    comp_query = (
        select(BrandCompetitorsAwarenessDailyPerformanceTable)
        .where(
            BrandCompetitorsAwarenessDailyPerformanceTable.search_target_brand_id == brand_id,
            BrandCompetitorsAwarenessDailyPerformanceTable.segment == segment,
            BrandCompetitorsAwarenessDailyPerformanceTable.search_date >= query_start,
            BrandCompetitorsAwarenessDailyPerformanceTable.search_date <= query_end,
        )
        .order_by(
            asc(BrandCompetitorsAwarenessDailyPerformanceTable.competitor_brand_name),
            asc(BrandCompetitorsAwarenessDailyPerformanceTable.search_date),
        )
    )
    comp_result = await db.execute(comp_query)
    comp_rows = comp_result.scalars().all()

    # ── Build target brand data ───────────────────────────────────────────────
    brand_points = [
        MarketDynamicDataPoint(
            date=row.search_date.isoformat(),
            visibility_share=round(row.share_of_visibility, 4) if row.share_of_visibility is not None else None,
            search_momentum=round(row.search_momentum, 4) if row.search_momentum is not None else None,
            position_strength=round(row.position_strength, 4) if row.position_strength is not None else None,
        )
        for row in brand_rows
    ]

    vis_vals = [r.share_of_visibility for r in brand_rows if r.share_of_visibility is not None]
    ps_vals = [r.position_strength for r in brand_rows if r.position_strength is not None]

    brands: list[MarketDynamicBrandData] = [
        MarketDynamicBrandData(
            brand_name=brand_name,
            is_target=True,
            data_points=brand_points,
            avg_visibility_share=round(statistics.mean(vis_vals), 4) if vis_vals else 0.0,
            median_position_strength=round(statistics.median(ps_vals), 4) if ps_vals else 0.0,
        )
    ]

    # ── Build per-competitor data ─────────────────────────────────────────────
    from collections import defaultdict
    comp_by_name: dict[str, list] = defaultdict(list)
    for row in comp_rows:
        comp_by_name[row.competitor_brand_name].append(row)

    for comp_name in sorted(comp_by_name.keys()):
        rows_for_comp = comp_by_name[comp_name]
        comp_points = [
            MarketDynamicDataPoint(
                date=row.search_date.isoformat(),
                visibility_share=round(row.share_of_visibility, 4) if row.share_of_visibility is not None else None,
                search_momentum=round(row.search_momentum, 4) if row.search_momentum is not None else None,
                position_strength=round(row.position_strength, 4) if row.position_strength is not None else None,
            )
            for row in rows_for_comp
        ]
        c_vis = [r.share_of_visibility for r in rows_for_comp if r.share_of_visibility is not None]
        c_ps = [r.position_strength for r in rows_for_comp if r.position_strength is not None]
        brands.append(
            MarketDynamicBrandData(
                brand_name=comp_name,
                is_target=False,
                data_points=comp_points,
                avg_visibility_share=round(statistics.mean(c_vis), 4) if c_vis else 0.0,
                median_position_strength=round(statistics.median(c_ps), 4) if c_ps else 0.0,
            )
        )

    logger.info(
        f"Returning market dynamic for {len(brands)} brands "
        f"({len(brand_points)} target data points, {len(comp_by_name)} competitors)"
    )
    return MarketDynamicResponse(
        brands=brands,
        start_date=query_start.isoformat(),
        end_date=query_end.isoformat(),
    )
