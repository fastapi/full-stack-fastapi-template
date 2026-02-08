from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.db import get_db, BrandSearchVisibilityTable, BrandSearchRankingTable
from app. models.brand_visibility import VisibilityDataPoint, VisibilityResponse
from app.models.brand_ranking import RankingDataPoint, RankingResponse
from app.models.brand_score import BrandScoreDataPoint, BrandScoreResponse
from app.models.shared_model import TimeRangeQuery
from app.utils.date_range import generate_periods
from app.utils.data_aggregation import calculate_median

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/brand-metrics", tags=["brand-metrics"])


@router.post("/visibility", response_model=VisibilityResponse)
async def query_visibility(
        query: TimeRangeQuery,
        db: AsyncSession = Depends(get_db)
):
    """
    Query brand visibility metrics aggregated by time period.

    - **brand_name**: Name of the brand to analyze
    - **start_date**: Start of date range (YYYY-MM-DD)
    - **end_date**: End of date range (YYYY-MM-DD)
    - **aggregation**: Time period (week, month, quarter, year)

    Returns median visibility scores per period, along with min/max/avg.
    """
    periods = generate_periods(query.start_date, query.end_date, query.aggregation)
    data_points = []

    for period_start, period_end in periods:
        # Query visibility data for this period
        stmt = select(BrandSearchVisibilityTable).where(
            and_(
                BrandSearchVisibilityTable.brand_name == query.brand_name,
                BrandSearchVisibilityTable.search_date >= period_start,
                BrandSearchVisibilityTable.search_date <= period_end
            )
        ).order_by(BrandSearchVisibilityTable.search_date)

        result = await db.execute(stmt)
        records = result.scalars().all()

        if records:
            visibility_scores = [r.visibility_score for r in records]
            positions = [r.position for r in records if r.position is not None]

            data_point = VisibilityDataPoint(
                period_start=period_start,
                period_end=period_end,
                median_visibility=calculate_median(visibility_scores),
                avg_visibility=sum(visibility_scores) / len(visibility_scores),
                min_visibility=min(visibility_scores),
                max_visibility=max(visibility_scores),
                data_points_count=len(records),
                total_impressions=sum(r.impressions for r in records),
                total_clicks=sum(r.clicks for r in records),
                avg_position=sum(positions) / len(positions) if positions else None
            )
            data_points.append(data_point)

    return VisibilityResponse(
        brand_name=query.brand_name,
        start_date=query.start_date,
        end_date=query.end_date,
        aggregation=query.aggregation,
        data=data_points
    )


@router.post("/ranking", response_model=RankingResponse)
async def query_ranking(
        query: TimeRangeQuery,
        db: AsyncSession = Depends(get_db)
):
    """
    Query brand ranking metrics aggregated by time period.

    - **brand_name**: Name of the brand to analyze
    - **start_date**: Start of date range (YYYY-MM-DD)
    - **end_date**: End of date range (YYYY-MM-DD)
    - **aggregation**: Time period (week, month, quarter, year)

    Returns median ranking positions per period (lower is better).
    """
    periods = generate_periods(query.start_date, query.end_date, query.aggregation)
    data_points = []
    previous_median = None

    for period_start, period_end in periods:
        # Query ranking data for this period
        stmt = select(BrandSearchRankingTable).where(
            and_(
                BrandSearchRankingTable.brand_name == query.brand_name,
                BrandSearchRankingTable.search_date >= period_start,
                BrandSearchRankingTable.search_date <= period_end
            )
        ).order_by(BrandSearchRankingTable.search_date)

        result = await db.execute(stmt)
        records = result.scalars().all()

        if records:
            rankings = [r.ranking_position for r in records]
            median_rank = calculate_median(rankings)

            # Calculate improvement (negative = better ranking)
            rank_improvement = None
            if previous_median is not None:
                rank_improvement = previous_median - median_rank

            data_point = RankingDataPoint(
                period_start=period_start,
                period_end=period_end,
                median_ranking=median_rank,
                avg_ranking=sum(rankings) / len(rankings),
                best_ranking=min(rankings),  # Lower is better
                worst_ranking=max(rankings),
                data_points_count=len(records),
                rank_improvement=rank_improvement
            )
            data_points.append(data_point)
            previous_median = median_rank

    return RankingResponse(
        brand_name=query.brand_name,
        start_date=query.start_date,
        end_date=query.end_date,
        aggregation=query.aggregation,
        data=data_points
    )


@router.post("/brand-score", response_model=BrandScoreResponse)
async def calculate_brand_score(
        query: TimeRangeQuery,
        db: AsyncSession = Depends(get_db)
):
    """
    Calculate comprehensive brand score based on visibility and ranking.

    **Brand Score Algorithm (0-100):**
    - Visibility Score (40%): Median visibility score
    - Ranking Score (30%): Inverted ranking (1st = 100, lower ranks scaled)
    - Engagement Score (20%): CTR and impression metrics
    - Trend Score (10%): Improvement over time

    - **brand_name**: Name of the brand to analyze
    - **start_date**: Start of date range (YYYY-MM-DD)
    - **end_date**: End of date range (YYYY-MM-DD)
    - **aggregation**: Time period (week, month, quarter, year)
    """
    periods = generate_periods(query.start_date, query.end_date, query.aggregation)
    data_points = []
    previous_scores = None

    for period_start, period_end in periods:
        # Query both visibility and ranking data
        vis_stmt = select(BrandSearchVisibilityTable).where(
            and_(
                BrandSearchVisibilityTable.brand_name == query.brand_name,
                BrandSearchVisibilityTable.search_date >= period_start,
                BrandSearchVisibilityTable.search_date <= period_end
            )
        )

        rank_stmt = select(BrandSearchRankingTable).where(
            and_(
                BrandSearchRankingTable.brand_name == query.brand_name,
                BrandSearchRankingTable.search_date >= period_start,
                BrandSearchRankingTable.search_date <= period_end
            )
        )

        vis_result = await db.execute(vis_stmt)
        rank_result = await db.execute(rank_stmt)

        vis_records = vis_result.scalars().all()
        rank_records = rank_result.scalars().all()

        if vis_records or rank_records:
            # 1. Visibility Score (40% weight)
            if vis_records:
                visibility_scores = [r.visibility_score for r in vis_records]
                visibility_score = calculate_median(visibility_scores)
            else:
                visibility_score = 0.0

            # 2. Ranking Score (30% weight)
            # Convert ranking to 0-100 scale (1st place = 100, 10th place = 10)
            if rank_records:
                rankings = [r.ranking_position for r in rank_records]
                total_competitors = rank_records[0].total_competitors if rank_records else 10
                median_rank = calculate_median(rankings)
                # Inverse ranking: (total - rank + 1) / total * 100
                ranking_score = ((total_competitors - median_rank + 1) / total_competitors) * 100
            else:
                ranking_score = 0.0

            # 3. Engagement Score (20% weight)
            # CTR = clicks / impressions
            if vis_records:
                total_impressions = sum(r.impressions for r in vis_records)
                total_clicks = sum(r.clicks for r in vis_records)
                ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
                # Normalize CTR to 0-100 (assuming 5% CTR = excellent)
                engagement_score = min(ctr * 20, 100)
            else:
                engagement_score = 0.0

            # 4. Trend Score (10% weight)
            # Improvement compared to previous period
            current_combined = (visibility_score + ranking_score) / 2
            if previous_scores is not None:
                improvement = current_combined - previous_scores
                # Scale improvement: +10 points = 100, -10 points = 0
                trend_score = max(0, min(100, 50 + (improvement * 5)))
            else:
                trend_score = 50.0  # Neutral for first period

            # Calculate weighted brand score
            brand_score = (
                    visibility_score * 0.40 +
                    ranking_score * 0.30 +
                    engagement_score * 0.20 +
                    trend_score * 0.10
            )

            data_point = BrandScoreDataPoint(
                period_start=period_start,
                period_end=period_end,
                brand_score=round(brand_score, 2),
                visibility_score=round(visibility_score, 2),
                ranking_score=round(ranking_score, 2),
                engagement_score=round(engagement_score, 2),
                trend_score=round(trend_score, 2),
                components={
                    "visibility_weight": "40%",
                    "ranking_weight": "30%",
                    "engagement_weight": "20%",
                    "trend_weight": "10%",
                    "median_ranking": median_rank if rank_records else None,
                    "ctr": round(ctr, 2) if vis_records else None,
                    "data_quality": {
                        "visibility_points": len(vis_records),
                        "ranking_points": len(rank_records)
                    }
                }
            )

            data_points.append(data_point)
            previous_scores = current_combined

    # Calculate overall score (average of all periods)
    overall_score = sum(dp.brand_score for dp in data_points) / len(data_points) if data_points else 0.0

    return BrandScoreResponse(
        brand_name=query.brand_name,
        start_date=query.start_date,
        end_date=query.end_date,
        aggregation=query.aggregation,
        overall_score=round(overall_score, 2),
        data=data_points
    )
