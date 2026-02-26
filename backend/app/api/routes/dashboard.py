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
)
from kila_models.models import (
    UsersTable,
    BrandAwarenessWeeklyPerformanceTable,
    BrandSearchRankingTable,
    ProjectUserTable,
    ProjectsRecord,
    BrandPromptTable,
    BrandCompetitorsTable,
    BrandCompetitorsAwarenessWeeklyPerformanceTable,
    BrandSearchCompetitorsVisibilityTable,
    BrandSearchCompetitorsRankingTable,
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

    This endpoint retrieves all brands that belong to projects where
    the user is either an OWNER or a Monitor. It uses the ProjectUserTable
    to find user's projects and BrandPromptTable to find brands within
    those projects.

    Args:
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        UserBrandsResponse with list of accessible brands

    Raises:
        HTTPException 401: If user is not authenticated
    """
    logger.info(f"Fetching accessible brands for user: {current_user.user_id}")

    try:
        # Step 1: Get all projects the user has access to (as owner or monitor)
        project_user_query = select(ProjectUserTable).where(
            ProjectUserTable.user_id == current_user.user_id
        )
        project_user_result = await db.execute(project_user_query)
        project_users = project_user_result.scalars().all()

        if not project_users:
            logger.info(f"No projects found for user: {current_user.user_id}")
            return UserBrandsResponse(brands=[], total_count=0)

        # Build a map of project_id -> user_role
        project_roles = {pu.project_id: pu.user_role.value for pu in project_users}
        project_ids = list(project_roles.keys())

        logger.info(f"Found {len(project_ids)} projects for user")

        # Step 2: Get project details
        projects_query = select(ProjectsRecord).where(
            ProjectsRecord.project_id.in_(project_ids),
            ProjectsRecord.is_active == True
        )
        projects_result = await db.execute(projects_query)
        projects = projects_result.scalars().all()

        # Build project name map
        project_names = {p.project_id: p.project_name for p in projects}

        # Step 3: Get unique brands from BrandPromptTable for these projects
        brands_query = (
            select(
                BrandPromptTable.brand_id,
                BrandPromptTable.brand_name,
                BrandPromptTable.project_id
            )
            .where(
                BrandPromptTable.project_id.in_(project_ids),
                BrandPromptTable.is_active == True
            )
            .distinct(BrandPromptTable.brand_id, BrandPromptTable.project_id)
        )
        brands_result = await db.execute(brands_query)
        brand_records = brands_result.all()

        # Build unique brands list (dedupe by brand_id, keep first project)
        seen_brands = {}
        user_brands = []

        for record in brand_records:
            brand_id = record.brand_id
            brand_name = record.brand_name
            project_id = record.project_id

            if brand_id not in seen_brands:
                seen_brands[brand_id] = True
                user_brands.append(UserBrand(
                    brand_id=brand_id,
                    brand_name=brand_name,
                    project_id=project_id,
                    project_name=project_names.get(project_id, "Unknown"),
                    user_role=project_roles.get(project_id, "unknown")
                ))

        logger.info(f"Found {len(user_brands)} unique brands for user")

        return UserBrandsResponse(
            brands=user_brands,
            total_count=len(user_brands)
        )

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
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve the list of segments for a brand.

    Queries BrandAwarenessWeeklyPerformanceTable for distinct segment values,
    excluding the "All-Segment" aggregate entry.

    Args:
        brand_id: Brand identifier
        db: Database session
        current_user: Authenticated user

    Returns:
        BrandSegmentsResponse with list of segment names
    """
    logger.info(f"Fetching segments for brand_id: {brand_id}")

    query = (
        select(distinct(BrandAwarenessWeeklyPerformanceTable.segment))
        .where(
            BrandAwarenessWeeklyPerformanceTable.brand_id == brand_id,
            BrandAwarenessWeeklyPerformanceTable.segment != "All-Segment"
        )
        .order_by(asc(BrandAwarenessWeeklyPerformanceTable.segment))
    )

    result = await db.execute(query)
    segments = [row[0] for row in result.all()]

    logger.info(f"Found {len(segments)} segments for brand_id: {brand_id}")

    return BrandSegmentsResponse(
        brand_id=brand_id,
        segments=segments,
    )


@router.get("/awareness-score", response_model=Optional[AwarenessScoreResponse])
async def get_awareness_score(
    brand_id: Optional[str] = Query(None, description="Filter by specific brand ID"),
    segment: str = Query("All-Segment", description="Segment name to filter by"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """
    Retrieve the latest brand awareness score.

    This endpoint queries the BrandAwarenessWeeklyPerformanceTable to get
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
        select(BrandAwarenessWeeklyPerformanceTable)
        .where(BrandAwarenessWeeklyPerformanceTable.segment == segment)
        .order_by(desc(BrandAwarenessWeeklyPerformanceTable.created_date))
        .limit(2)  # Get current and previous for trend
    )

    # Apply brand_id filter if provided
    if brand_id:
        query = query.where(BrandAwarenessWeeklyPerformanceTable.brand_id == brand_id)

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
        current_date=current_record.created_date,
        previous_date=previous_record.created_date if previous_record else None,
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

    This endpoint queries the BrandAwarenessWeeklyPerformanceTable to get
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
        select(BrandAwarenessWeeklyPerformanceTable)
        .where(BrandAwarenessWeeklyPerformanceTable.segment == segment)
        .order_by(desc(BrandAwarenessWeeklyPerformanceTable.created_date))
        .limit(2)
    )

    # Apply brand_id filter if provided
    if brand_id:
        query = query.where(BrandAwarenessWeeklyPerformanceTable.brand_id == brand_id)

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
        current_date=current_record.created_date,
        previous_date=previous_record.created_date if previous_record else None,
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
        select(BrandAwarenessWeeklyPerformanceTable)
        .where(BrandAwarenessWeeklyPerformanceTable.segment == segment)
        .order_by(desc(BrandAwarenessWeeklyPerformanceTable.created_date))
        .limit(2)
    )

    if brand_id:
        query = query.where(BrandAwarenessWeeklyPerformanceTable.brand_id == brand_id)

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
        select(BrandAwarenessWeeklyPerformanceTable)
        .where(BrandAwarenessWeeklyPerformanceTable.created_date >= query_start_date)
        .where(BrandAwarenessWeeklyPerformanceTable.created_date <= query_end_date)
        .where(BrandAwarenessWeeklyPerformanceTable.segment == segment)
        .order_by(asc(BrandAwarenessWeeklyPerformanceTable.created_date))
    )

    # Apply brand_id filter if provided
    if brand_id:
        query = query.where(BrandAwarenessWeeklyPerformanceTable.brand_id == brand_id)

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
            date=record.created_date.isoformat(),
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

    # Group visibility by date (search_date_end is a Date column, already a date object)
    vis_by_date: dict[str, list] = {}
    brand_name = "Unknown"
    for rec in vis_records:
        d = rec.search_date_end.isoformat()
        vis_by_date.setdefault(d, []).append(rec)
        brand_name = rec.search_target_brand_name

    # ---- Query ranking data ----
    rank_query = (
        select(BrandSearchRankingTable)
        .where(
            BrandSearchRankingTable.brand_id == brand_id,
            BrandSearchRankingTable.search_date >= query_start_date,
            BrandSearchRankingTable.search_date <= query_end_date
        )
        .order_by(asc(BrandSearchRankingTable.search_date))
    )
    if segment:
        rank_query = rank_query.where(BrandSearchRankingTable.segment == segment)
    rank_result = await db.execute(rank_query)
    rank_records = rank_result.scalars().all()

    # Group ranking by date
    rank_by_date: dict[str, list] = {}
    for rec in rank_records:
        d = rec.search_date.date().isoformat() if hasattr(rec.search_date, 'date') else str(rec.search_date)
        rank_by_date.setdefault(d, []).append(rec)
        if brand_name == "Unknown":
            brand_name = rec.brand_name

    # ---- Build data points ----
    all_dates = sorted(set(list(vis_by_date.keys()) + list(rank_by_date.keys())))

    data_points = []
    visibility_values = []
    ranking_values = []

    for d in all_dates:
        # Visibility rate for this date
        vis_recs = vis_by_date.get(d, [])
        if vis_recs:
            total_search = sum(r.total_search_count for r in vis_recs)
            total_visible = sum(r.search_visibility_count for r in vis_recs)
            vis_rate = (total_visible / total_search * 100) if total_search > 0 else 0.0
        else:
            vis_rate = 0.0

        # Average ranking for this date
        rank_recs = rank_by_date.get(d, [])
        if rank_recs:
            avg_rank = sum(r.search_ranking for r in rank_recs) / len(rank_recs)
        else:
            avg_rank = 0.0

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

    # ---- Query competitor visibility data ----
    vis_query = (
        select(BrandSearchCompetitorsVisibilityTable)
        .where(
            BrandSearchCompetitorsVisibilityTable.search_target_brand_id == brand_id,
            BrandSearchCompetitorsVisibilityTable.competitor_brand_name == competitor_brand_name,
            BrandSearchCompetitorsVisibilityTable.search_date >= query_start_date,
            BrandSearchCompetitorsVisibilityTable.search_date <= query_end_date,
        )
        .order_by(asc(BrandSearchCompetitorsVisibilityTable.search_date))
    )
    if segment:
        vis_query = vis_query.where(BrandSearchCompetitorsVisibilityTable.segment == segment)
    vis_result = await db.execute(vis_query)
    vis_records = vis_result.scalars().all()

    # Group visibility by date
    vis_by_date: dict[str, list] = {}
    for rec in vis_records:
        d = rec.search_date.date().isoformat() if hasattr(rec.search_date, 'date') else str(rec.search_date)
        vis_by_date.setdefault(d, []).append(rec)

    # ---- Query competitor ranking data ----
    rank_query = (
        select(BrandSearchCompetitorsRankingTable)
        .where(
            BrandSearchCompetitorsRankingTable.search_target_brand_id == brand_id,
            BrandSearchCompetitorsRankingTable.competitor_brand_name == competitor_brand_name,
            BrandSearchCompetitorsRankingTable.search_date >= query_start_date,
            BrandSearchCompetitorsRankingTable.search_date <= query_end_date,
        )
        .order_by(asc(BrandSearchCompetitorsRankingTable.search_date))
    )
    if segment:
        rank_query = rank_query.where(BrandSearchCompetitorsRankingTable.segment == segment)
    rank_result = await db.execute(rank_query)
    rank_records = rank_result.scalars().all()

    # Group ranking by date
    rank_by_date: dict[str, list] = {}
    for rec in rank_records:
        d = rec.search_date.date().isoformat() if hasattr(rec.search_date, 'date') else str(rec.search_date)
        rank_by_date.setdefault(d, []).append(rec)

    # ---- Build data points ----
    all_dates = sorted(set(list(vis_by_date.keys()) + list(rank_by_date.keys())))

    data_points = []
    visibility_values = []
    ranking_values = []

    for d in all_dates:
        # Visibility rate for this date
        vis_recs = vis_by_date.get(d, [])
        if vis_recs:
            total_search = sum(r.total_search_count for r in vis_recs)
            total_visible = sum(r.competitor_visibility_count for r in vis_recs)
            vis_rate = (total_visible / total_search * 100) if total_search > 0 else 0.0
        else:
            vis_rate = 0.0

        # Average ranking for this date
        rank_recs = rank_by_date.get(d, [])
        if rank_recs:
            avg_rank = sum(r.search_ranking for r in rank_recs) / len(rank_recs)
        else:
            avg_rank = 0.0

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
        select(BrandAwarenessWeeklyPerformanceTable)
        .where(
            BrandAwarenessWeeklyPerformanceTable.brand_id == brand_id,
            BrandAwarenessWeeklyPerformanceTable.segment == segment,
            BrandAwarenessWeeklyPerformanceTable.created_date >= query_start_date,
            BrandAwarenessWeeklyPerformanceTable.created_date <= query_end_date,
        )
        .order_by(asc(BrandAwarenessWeeklyPerformanceTable.created_date))
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
            date=record.created_date.isoformat(),
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
        select(BrandAwarenessWeeklyPerformanceTable)
        .where(
            BrandAwarenessWeeklyPerformanceTable.brand_id == brand_id,
            BrandAwarenessWeeklyPerformanceTable.segment != "All-Segment",
            BrandAwarenessWeeklyPerformanceTable.created_date >= query_start_date,
            BrandAwarenessWeeklyPerformanceTable.created_date <= query_end_date,
        )
        .order_by(
            asc(BrandAwarenessWeeklyPerformanceTable.segment),
            desc(BrandAwarenessWeeklyPerformanceTable.created_date),
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
        select(BrandAwarenessWeeklyPerformanceTable)
        .where(
            BrandAwarenessWeeklyPerformanceTable.brand_id == brand_id,
            BrandAwarenessWeeklyPerformanceTable.segment != "All-Segment",
            BrandAwarenessWeeklyPerformanceTable.created_date >= query_start_date,
            BrandAwarenessWeeklyPerformanceTable.created_date <= query_end_date,
        )
        .order_by(
            asc(BrandAwarenessWeeklyPerformanceTable.segment),
            desc(BrandAwarenessWeeklyPerformanceTable.created_date),
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
            date=record.created_date.isoformat(),
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
        select(BrandCompetitorsAwarenessWeeklyPerformanceTable)
        .where(
            BrandCompetitorsAwarenessWeeklyPerformanceTable.search_target_brand_id == brand_id,
            BrandCompetitorsAwarenessWeeklyPerformanceTable.competitor_brand_name == competitor_brand_name,
            BrandCompetitorsAwarenessWeeklyPerformanceTable.segment == segment,
            BrandCompetitorsAwarenessWeeklyPerformanceTable.created_date >= query_start_date,
            BrandCompetitorsAwarenessWeeklyPerformanceTable.created_date <= query_end_date,
        )
        .order_by(asc(BrandCompetitorsAwarenessWeeklyPerformanceTable.created_date))
    )

    result = await db.execute(query)
    records = result.scalars().all()

    data_points = []
    for record in records:
        data_points.append(CompetitorAwarenessDataPoint(
            date=record.created_date.isoformat(),
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
        select(BrandCompetitorsAwarenessWeeklyPerformanceTable)
        .where(
            BrandCompetitorsAwarenessWeeklyPerformanceTable.search_target_brand_id == brand_id,
            BrandCompetitorsAwarenessWeeklyPerformanceTable.competitor_brand_name == competitor_brand_name,
            BrandCompetitorsAwarenessWeeklyPerformanceTable.segment != "All-Segment",
            BrandCompetitorsAwarenessWeeklyPerformanceTable.created_date >= query_start_date,
            BrandCompetitorsAwarenessWeeklyPerformanceTable.created_date <= query_end_date,
        )
        .order_by(
            asc(BrandCompetitorsAwarenessWeeklyPerformanceTable.segment),
            desc(BrandCompetitorsAwarenessWeeklyPerformanceTable.created_date),
        )
    )

    comp_result = await db.execute(comp_query)
    comp_records = comp_result.scalars().all()

    # Query brand's own awareness scores for gap calculation
    brand_query = (
        select(BrandAwarenessWeeklyPerformanceTable)
        .where(
            BrandAwarenessWeeklyPerformanceTable.brand_id == brand_id,
            BrandAwarenessWeeklyPerformanceTable.segment != "All-Segment",
            BrandAwarenessWeeklyPerformanceTable.created_date >= query_start_date,
            BrandAwarenessWeeklyPerformanceTable.created_date <= query_end_date,
        )
    )

    brand_result = await db.execute(brand_query)
    brand_records = brand_result.scalars().all()

    # Build lookup: (segment, date_str) -> brand_awareness_score
    brand_awareness_map: dict[tuple[str, str], float] = {}
    brand_name = "Unknown"
    for record in brand_records:
        brand_name = record.brand_name
        key = (record.segment, record.created_date.isoformat())
        brand_awareness_map[key] = record.awareness_score or 0.0

    # Build rows with segment gap
    rows: list[CompetitorDetailRow] = []
    for record in comp_records:
        if brand_name == "Unknown":
            brand_name = record.search_target_brand_name or "Unknown"

        comp_awareness = round(record.awareness_score or 0.0, 2)
        date_str = record.created_date.isoformat()
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

    Queries BrandCompetitorsAwarenessWeeklyPerformanceTable grouped by
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
        select(BrandCompetitorsAwarenessWeeklyPerformanceTable)
        .where(
            BrandCompetitorsAwarenessWeeklyPerformanceTable.search_target_brand_id == brand_id,
            BrandCompetitorsAwarenessWeeklyPerformanceTable.segment == segment,
            BrandCompetitorsAwarenessWeeklyPerformanceTable.created_date >= query_start_date,
            BrandCompetitorsAwarenessWeeklyPerformanceTable.created_date <= query_end_date,
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
]

SIGNAL_DISPLAY_NAMES = {
    "competitive_dominance_signal": "Competitive Dominance Risk",
    "competitive_erosion_signal": "Competitive Erosion Risk",
    "competitive_breakthrough_signal": "Competitor Breakthrough Risk",
    "deceleration_warning_signal": "Growth Deceleration Risk",
    "weak_structural_position_signal": "Position Structure Weakness Risk",
}

SEVERITY_TO_INT = {"Low": 1, "Medium": 2, "High": 4}

SIGNAL_TYPE_TO_HISTORY_KEY = {
    "competitive_dominance_signal": "competitive_dominance",
    "competitive_erosion_signal": "competitive_erosion",
    "competitive_breakthrough_signal": "competitor_breakthrough",
    "deceleration_warning_signal": "growth_deceleration",
    "weak_structural_position_signal": "position_weakness",
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
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Retrieve the brand impression summary with 3 quick metrics for the selector card.

    Queries BrandSearchDailyBasicMetricsTable for segment='all-segment' and returns
    visibility rate, median ranking position, and final sentiment score for the latest
    7-day window, plus comparison with the prior 7-day window.

    Visibility  = search_visibility_count / total_search_count * 100
    Position    = median_ranking (lower is better)
    Sentiment   = final_sentiment_score (0-100, NULL if brand had no visibility)
    """
    logger.info(
        f"Fetching brand impression summary for user: {current_user.user_id}, "
        f"brand_id: {brand_id}"
    )

    ALL_SEGMENT = "all-segment"

    # ── Current record: latest search_date_end for this brand + all-segment ──
    current_query = (
        select(BrandSearchDailyBasicMetricsTable)
        .where(
            BrandSearchDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchDailyBasicMetricsTable.segment == ALL_SEGMENT,
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
            BrandSearchDailyBasicMetricsTable.segment == ALL_SEGMENT,
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


@router.get("/brand-segments", response_model=BrandSegmentsResponse)
async def get_brand_segments(
    brand_id: str = Query(..., description="Brand ID to get segments for"),
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user),
):
    """
    Return distinct segment names for a brand from BrandSearchDailyBasicMetricsTable,
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
    segments = [row[0] for row in result.fetchall()]

    logger.info(f"Found {len(segments)} segments for brand_id: {brand_id}")
    return BrandSegmentsResponse(brand_id=brand_id, segments=segments)


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
    """Return deduplicated AI reference sources cited for the brand within the time range."""
    today = date.today()
    if time_range == TimeRange.CUSTOM and start_date and end_date:
        query_start, query_end = start_date, end_date
    elif time_range == TimeRange.ONE_MONTH:
        query_start, query_end = today - timedelta(days=30), today
    elif time_range == TimeRange.ONE_QUARTER:
        query_start, query_end = today - timedelta(days=90), today
    elif time_range == TimeRange.ONE_YEAR:
        query_start, query_end = today - timedelta(days=365), today
    elif time_range == TimeRange.YEAR_TO_DATE:
        query_start, query_end = date(today.year, 1, 1), today
    else:
        query_start, query_end = today - timedelta(days=30), today

    filters = [
        BrandSearchResultTable.search_target_brand_id == brand_id,
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
        .limit(200)
    )
    result = await db.execute(query)
    rows = result.fetchall()

    seen: set[str] = set()
    sources: list[str] = []
    for (raw,) in rows:
        for src in _parse_text_list(raw):
            if src not in seen:
                seen.add(src)
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
    """Return customer reviews with sentiment labels from the daily metrics aggregation."""
    today = date.today()
    if time_range == TimeRange.CUSTOM and start_date and end_date:
        query_start, query_end = start_date, end_date
    elif time_range == TimeRange.ONE_MONTH:
        query_start, query_end = today - timedelta(days=30), today
    elif time_range == TimeRange.ONE_QUARTER:
        query_start, query_end = today - timedelta(days=90), today
    elif time_range == TimeRange.ONE_YEAR:
        query_start, query_end = today - timedelta(days=365), today
    elif time_range == TimeRange.YEAR_TO_DATE:
        query_start, query_end = date(today.year, 1, 1), today
    else:
        query_start, query_end = today - timedelta(days=30), today

    seg_filter = segment if segment and segment != "all-segment" else "all-segment"
    query = (
        select(
            BrandSearchDailyBasicMetricsTable.positive_customer_reviews,
            BrandSearchDailyBasicMetricsTable.neutral_customer_reviews,
            BrandSearchDailyBasicMetricsTable.negative_customer_reviews,
        )
        .where(
            BrandSearchDailyBasicMetricsTable.search_target_brand_id == brand_id,
            BrandSearchDailyBasicMetricsTable.segment == seg_filter,
            BrandSearchDailyBasicMetricsTable.search_date_end >= query_start,
            BrandSearchDailyBasicMetricsTable.search_date_end <= query_end,
        )
        .order_by(desc(BrandSearchDailyBasicMetricsTable.search_date_end))
        .limit(10)
    )
    result = await db.execute(query)
    rows = result.fetchall()

    seen: set[str] = set()
    reviews: list[CustomerReviewItem] = []
    seq = 1
    for (pos_raw, neu_raw, neg_raw) in rows:
        for text in _parse_text_list(pos_raw):
            if text not in seen:
                seen.add(text)
                reviews.append(CustomerReviewItem(seq=seq, review=text, sentiment="Positive"))
                seq += 1
        for text in _parse_text_list(neu_raw):
            if text not in seen:
                seen.add(text)
                reviews.append(CustomerReviewItem(seq=seq, review=text, sentiment="Neutral"))
                seq += 1
        for text in _parse_text_list(neg_raw):
            if text not in seen:
                seen.add(text)
                reviews.append(CustomerReviewItem(seq=seq, review=text, sentiment="Negative"))
                seq += 1

    return CustomerReviewsResponse(brand_id=brand_id, reviews=reviews)
