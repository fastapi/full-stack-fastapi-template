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
)
from kila_models.models import (
    UsersTable,
    BrandAwarenessWeeklyPerformanceTable,
    BrandSearchVisibilityTable,
    BrandSearchRankingTable,
    ProjectUserTable,
    ProjectsRecord,
    BrandPromptTable,
    BrandCompetitorsTable,
    BrandSearchCompetitorsVisibilityTable,
    BrandSearchCompetitorsRankingTable,
)


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


@router.get("/awareness-score", response_model=Optional[AwarenessScoreResponse])
async def get_awareness_score(
    brand_id: Optional[str] = Query(None, description="Filter by specific brand ID"),
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
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        AwarenessScoreResponse with current and previous scores,
        or None if no data exists.

    Raises:
        HTTPException 401: If user is not authenticated
    """
    logger.info(f"Fetching awareness score for user: {current_user.user_id}, brand_id: {brand_id}")

    # Build query to get the two most recent records for trend calculation
    # We order by created_date descending to get the latest first
    query = (
        select(BrandAwarenessWeeklyPerformanceTable)
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
        db: Database session (injected by FastAPI)
        current_user: Authenticated user (injected by FastAPI)

    Returns:
        ConsistencyIndexResponse with current and previous indices,
        or None if no data exists.

    Raises:
        HTTPException 401: If user is not authenticated
    """
    logger.info(f"Fetching consistency index for user: {current_user.user_id}, brand_id: {brand_id}")

    # Build query to get the two most recent records for trend calculation
    query = (
        select(BrandAwarenessWeeklyPerformanceTable)
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
        select(BrandSearchVisibilityTable)
        .where(
            BrandSearchVisibilityTable.brand_id == brand_id,
            BrandSearchVisibilityTable.search_date >= query_start_date,
            BrandSearchVisibilityTable.search_date <= query_end_date
        )
        .order_by(asc(BrandSearchVisibilityTable.search_date))
    )
    vis_result = await db.execute(vis_query)
    vis_records = vis_result.scalars().all()

    # Group visibility by date
    vis_by_date: dict[str, list] = {}
    brand_name = "Unknown"
    for rec in vis_records:
        d = rec.search_date.date().isoformat() if hasattr(rec.search_date, 'date') else str(rec.search_date)
        vis_by_date.setdefault(d, []).append(rec)
        brand_name = rec.brand_name

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
