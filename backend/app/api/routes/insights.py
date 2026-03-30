"""
Actionable Insights API routes.

Provides endpoints for brand performance signals, drill-down details,
and query-level analysis. All endpoints require super user access.

Endpoints:
    GET /insights/overview                    - All active signals grouped by category
    GET /insights/signal/{type}               - Signal detail with recommendations
    GET /insights/signal/{type}/queries       - Query-level drill-down
"""

from __future__ import annotations

import logging
from datetime import date as DateType
from datetime import timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_super_user
from app.core.db import get_db
from kila_models.models import UsersTable
from kila_models.models.database import (
    BrandAwarenessDailyPerformanceTable,
    BrandCompetitorsAwarenessDailyPerformanceTable,
    BrandPerformanceInsightTable,
    BrandSearchResultTable,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Signal category mapping
# ---------------------------------------------------------------------------

SIGNAL_CATEGORIES: dict[str, str] = {
    "competitive_erosion_signal": "competitive_position",
    "rank_displacement_signal": "competitive_position",
    "competitive_dominance_signal": "competitive_position",
    "growth_deceleration_signal": "momentum_acceleration",
    "fragile_leadership_signal": "structural_strength",
    "weak_structural_position_signal": "structural_strength",
    "volatility_spike_signal": "risk_instability",
    "competitor_breakthrough_signal": "risk_instability",
    "new_entrant_signal": "risk_instability",
}

ALL_CATEGORIES = [
    "competitive_position",
    "momentum_acceleration",
    "structural_strength",
    "risk_instability",
]

# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class SeveritySummary(BaseModel):
    high: int
    medium: int
    low: int


class SignalOverviewItem(BaseModel):
    signal_type: str
    severity: str
    business_meaning: str
    score: float
    top_competitor: Optional[str]
    created_date: DateType


class OverviewResponse(BaseModel):
    date: Optional[DateType]
    summary: SeveritySummary
    categories: dict[str, list[SignalOverviewItem]]


class SignalInfo(BaseModel):
    type: str
    severity: str
    score: float
    created_date: DateType


class MetricItem(BaseModel):
    label: str
    value: str
    from_: Optional[str] = None
    to: Optional[str] = None
    status: Optional[str] = None


class WhyFired(BaseModel):
    explanation: str
    metrics: list[MetricItem]


class CompetitorInfo(BaseModel):
    name: str
    sov: Optional[float]
    ssi: Optional[float]
    position_strength: Optional[float]
    trend_7d: Optional[float]
    is_target: bool = False
    is_top_threat: bool = False


class Recommendation(BaseModel):
    priority: int
    title: str
    detail: str
    action_type: str


class SignalDetailResponse(BaseModel):
    signal: SignalInfo
    why_fired: WhyFired
    competitors: list[CompetitorInfo]
    recommendations: list[Recommendation]


class QueryRow(BaseModel):
    prompt_text: str
    brand_rank_today: Optional[int]
    brand_rank_7d_ago: Optional[int]
    rank_change: Optional[int]
    top_competitor_today: Optional[str]
    top_competitor_rank: Optional[int]


class QueryDrillDownResponse(BaseModel):
    queries: list[QueryRow]


# ---------------------------------------------------------------------------
# Recommendation builder
# ---------------------------------------------------------------------------

_RECOMMENDATION_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "competitive_erosion_signal": [
        {
            "priority": 1,
            "title": "Publish content for top high-loss queries",
            "detail": (
                "Your share of visibility (SOV) has dropped significantly vs. {top_competitor}. "
                "Identify the queries where you lost the most ground and create targeted content."
            ),
            "action_type": "view_affected_queries",
        },
        {
            "priority": 2,
            "title": "Analyse {top_competitor}'s rising queries",
            "detail": (
                "Review the queries where {top_competitor} gained impressions to understand "
                "what content angles are working for them."
            ),
            "action_type": "compare_impressions",
        },
    ],
    "rank_displacement_signal": [
        {
            "priority": 1,
            "title": "Fix ranking regressions on key queries",
            "detail": (
                "Your average ranking has worsened. Audit the queries with the largest rank drops "
                "and refresh the underlying content."
            ),
            "action_type": "view_affected_queries",
        },
        {
            "priority": 2,
            "title": "Benchmark against {top_competitor}",
            "detail": (
                "Compare your impression share on displaced queries with {top_competitor} "
                "to find content gaps."
            ),
            "action_type": "compare_impressions",
        },
    ],
    "competitive_dominance_signal": [
        {
            "priority": 1,
            "title": "Defend dominant queries from {top_competitor}",
            "detail": (
                "{top_competitor} is approaching your top queries. Review those queries "
                "and strengthen your content to maintain your lead."
            ),
            "action_type": "view_affected_queries",
        },
    ],
    "fragile_leadership_signal": [
        {
            "priority": 1,
            "title": "Identify vulnerable top-ranked queries",
            "detail": (
                "Your leadership position shows high volatility. Find the queries where your "
                "ranking fluctuates the most and stabilise them."
            ),
            "action_type": "view_affected_queries",
        },
        {
            "priority": 2,
            "title": "Monitor {top_competitor}'s impression gains",
            "detail": (
                "Track which queries {top_competitor} is gaining on to anticipate displacement risk."
            ),
            "action_type": "compare_impressions",
        },
    ],
    "growth_deceleration_signal": [
        {
            "priority": 1,
            "title": "Re-engage stagnating query segments",
            "detail": (
                "Your search momentum has slowed. Identify queries where impressions have plateaued "
                "and refresh your content strategy."
            ),
            "action_type": "view_affected_queries",
        },
    ],
    "weak_structural_position_signal": [
        {
            "priority": 1,
            "title": "Improve low-ranking queries",
            "detail": (
                "Your structural position index is weak. Focus on the queries where your ranking "
                "is persistently low and build authoritative content."
            ),
            "action_type": "view_affected_queries",
        },
        {
            "priority": 2,
            "title": "Learn from {top_competitor}'s strong queries",
            "detail": (
                "Analyse the queries where {top_competitor} outranks you most to identify "
                "content and positioning opportunities."
            ),
            "action_type": "compare_impressions",
        },
    ],
    "volatility_spike_signal": [
        {
            "priority": 1,
            "title": "Stabilise high-volatility queries",
            "detail": (
                "Ranking volatility has spiked. Find the queries with the greatest rank swings "
                "and investigate content or algorithmic changes."
            ),
            "action_type": "view_affected_queries",
        },
    ],
    "competitor_breakthrough_signal": [
        {
            "priority": 1,
            "title": "Track {top_competitor}'s breakthrough queries",
            "detail": (
                "{top_competitor} has broken through in new query areas. Analyse these queries "
                "to understand their content strategy."
            ),
            "action_type": "compare_impressions",
        },
        {
            "priority": 2,
            "title": "Reinforce your positions on affected queries",
            "detail": (
                "Identify the queries where {top_competitor}'s breakthrough displaced you "
                "and update your content."
            ),
            "action_type": "view_affected_queries",
        },
    ],
    "new_entrant_signal": [
        {
            "priority": 1,
            "title": "Analyse new entrant's query footprint",
            "detail": (
                "A new competitor has appeared. Review the queries they are ranking on "
                "to assess the threat to your visibility."
            ),
            "action_type": "compare_impressions",
        },
    ],
}


def build_recommendations(signal_type: str, signal_data: dict[str, Any]) -> list[Recommendation]:
    """Generate recommendation objects for a given signal type, interpolating
    competitor names and metric values from signal_data."""
    templates = _RECOMMENDATION_TEMPLATES.get(signal_type, [])
    top_competitor = signal_data.get("top_competitor") or "your top competitor"
    score = signal_data.get("score", 0.0)

    recommendations: list[Recommendation] = []
    for tmpl in templates:
        title = tmpl["title"].format(top_competitor=top_competitor, score=score)
        detail = tmpl["detail"].format(top_competitor=top_competitor, score=score)
        recommendations.append(
            Recommendation(
                priority=tmpl["priority"],
                title=title,
                detail=detail,
                action_type=tmpl["action_type"],
            )
        )
    return recommendations


# ---------------------------------------------------------------------------
# Helper: build "why fired" explanation
# ---------------------------------------------------------------------------

_EXPLANATIONS: dict[str, str] = {
    "competitive_erosion_signal": (
        "Your share-of-visibility gap vs. {top_competitor} has narrowed by {score_abs:.1f} points "
        "in the trailing 7-day window, triggering a {severity} erosion alert."
    ),
    "rank_displacement_signal": (
        "Your average ranking dropped by {score_abs:.1f} positions relative to the previous window, "
        "indicating displacement pressure from {top_competitor}."
    ),
    "competitive_dominance_signal": (
        "{top_competitor} is closing the gap to your dominant position. "
        "The dominance score moved by {score:.1f} this period."
    ),
    "fragile_leadership_signal": (
        "Your leadership position shows high volatility (score {score:.1f}). "
        "Ranking swings indicate instability that {top_competitor} may exploit."
    ),
    "growth_deceleration_signal": (
        "Search momentum decelerated with a score of {score:.1f}, "
        "suggesting your visibility growth is stalling."
    ),
    "weak_structural_position_signal": (
        "Structural position index is {score:.1f}, indicating persistent low ranking "
        "relative to {top_competitor} across multiple queries."
    ),
    "volatility_spike_signal": (
        "Ranking volatility spiked to {score:.1f} standard deviations above baseline, "
        "suggesting algorithmic or content changes are destabilising your positions."
    ),
    "competitor_breakthrough_signal": (
        "{top_competitor} achieved a breakthrough with score {score:.1f}, "
        "entering new query territory and competing with your key positions."
    ),
    "new_entrant_signal": (
        "A new competitor has appeared in your segment with a score of {score:.1f}, "
        "potentially reducing your overall share of visibility."
    ),
}


def _build_why_fired(signal_type: str, signal_data: dict[str, Any]) -> WhyFired:
    score = signal_data.get("score", 0.0)
    top_competitor = signal_data.get("top_competitor") or "a competitor"
    severity = signal_data.get("severity", "").capitalize()

    tmpl = _EXPLANATIONS.get(
        signal_type,
        "Signal '{signal_type}' fired with score {score:.1f} and severity {severity}.",
    )
    explanation = tmpl.format(
        top_competitor=top_competitor,
        score=score,
        score_abs=abs(score),
        severity=severity,
        signal_type=signal_type,
    )

    metrics: list[MetricItem] = [
        MetricItem(
            label="Signal Score",
            value=f"{score:.1f}",
            status=(
                "critical"
                if severity == "High"
                else ("warning" if severity == "Medium" else "info")
            ),  # severity already capitalized above
        )
    ]

    return WhyFired(explanation=explanation, metrics=metrics)


# ---------------------------------------------------------------------------
# Endpoint 1: Overview
# ---------------------------------------------------------------------------


@router.get("/overview", response_model=OverviewResponse)
async def get_insights_overview(
    brand_id: str = Query(..., description="Brand ID to retrieve insights for"),
    segment: str = Query(..., description="Segment filter"),
    db: AsyncSession = Depends(get_db),
    _current_user: UsersTable = Depends(require_super_user),
) -> OverviewResponse:
    """Return all active signals grouped by category for the most recent date."""

    # Find the most recent created_date for this brand/segment
    latest_date_stmt = select(func.max(BrandPerformanceInsightTable.created_date)).where(
        and_(
            BrandPerformanceInsightTable.search_target_brand_id == brand_id,
            BrandPerformanceInsightTable.segment == segment,
        )
    )
    latest_date_result = await db.execute(latest_date_stmt)
    latest_date = latest_date_result.scalar_one_or_none()

    if latest_date is None:
        return OverviewResponse(
            date=None,
            summary=SeveritySummary(high=0, medium=0, low=0),
            categories={cat: [] for cat in ALL_CATEGORIES},
        )

    stmt = select(BrandPerformanceInsightTable).where(
        and_(
            BrandPerformanceInsightTable.search_target_brand_id == brand_id,
            BrandPerformanceInsightTable.segment == segment,
            BrandPerformanceInsightTable.created_date == latest_date,
        )
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    categories: dict[str, list[SignalOverviewItem]] = {cat: [] for cat in ALL_CATEGORIES}
    severity_counts = {"High": 0, "Medium": 0, "Low": 0}

    for row in rows:
        sev_key = row.severity.capitalize() if row.severity else "Low"
        if sev_key in severity_counts:
            severity_counts[sev_key] += 1

        item = SignalOverviewItem(
            signal_type=row.signal_type,
            severity=row.severity,
            business_meaning=row.business_meaning,
            score=row.signal_score,
            top_competitor=row.top_competitor_brand_name,
            created_date=row.created_date,
        )
        category = SIGNAL_CATEGORIES.get(row.signal_type, "risk_instability")
        categories[category].append(item)

    return OverviewResponse(
        date=latest_date,
        summary=SeveritySummary(
            high=severity_counts["High"],
            medium=severity_counts["Medium"],
            low=severity_counts["Low"],
        ),
        categories=categories,
    )


# ---------------------------------------------------------------------------
# Endpoint 2: Signal Detail
# ---------------------------------------------------------------------------


@router.get("/signal/{signal_type}", response_model=SignalDetailResponse)
async def get_signal_detail(
    signal_type: str,
    brand_id: str = Query(...),
    segment: str = Query(...),
    date_str: Optional[str] = Query(
        None,
        alias="date",
        description="Date in YYYY-MM-DD format; defaults to most recent",
    ),
    db: AsyncSession = Depends(get_db),
    _current_user: UsersTable = Depends(require_super_user),
) -> SignalDetailResponse:
    """Return detail for a specific signal type including why it fired and recommendations."""

    # Resolve target date
    target_date: Optional[DateType] = None
    if date_str:
        try:
            target_date = DateType.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid date format. Use YYYY-MM-DD.")

    if target_date is None:
        latest_stmt = select(func.max(BrandPerformanceInsightTable.created_date)).where(
            and_(
                BrandPerformanceInsightTable.search_target_brand_id == brand_id,
                BrandPerformanceInsightTable.segment == segment,
                BrandPerformanceInsightTable.signal_type == signal_type,
            )
        )
        res = await db.execute(latest_stmt)
        target_date = res.scalar_one_or_none()

    if target_date is None:
        return SignalDetailResponse(
            signal=SignalInfo(
                type=signal_type,
                severity="Unknown",
                score=0.0,
                created_date=DateType.today(),  # no data at all — use today as placeholder
            ),
            why_fired=WhyFired(explanation="No signal data found.", metrics=[]),
            competitors=[],
            recommendations=[],
        )

    signal_stmt = select(BrandPerformanceInsightTable).where(
        and_(
            BrandPerformanceInsightTable.search_target_brand_id == brand_id,
            BrandPerformanceInsightTable.segment == segment,
            BrandPerformanceInsightTable.signal_type == signal_type,
            BrandPerformanceInsightTable.created_date == target_date,
        )
    )
    signal_res = await db.execute(signal_stmt)
    signal_row = signal_res.scalar_one_or_none()

    if signal_row is None:
        return SignalDetailResponse(
            signal=SignalInfo(
                type=signal_type,
                severity="Unknown",
                score=0.0,
                created_date=target_date,
            ),
            why_fired=WhyFired(
                explanation="No signal data found for the requested date.", metrics=[]
            ),
            competitors=[],
            recommendations=[],
        )

    signal_data = {
        "score": signal_row.signal_score,
        "severity": signal_row.severity,
        "top_competitor": signal_row.top_competitor_brand_name,
    }

    # Fetch brand awareness metrics for target date
    brand_stmt = select(BrandAwarenessDailyPerformanceTable).where(
        and_(
            BrandAwarenessDailyPerformanceTable.brand_id == brand_id,
            BrandAwarenessDailyPerformanceTable.segment == segment,
            BrandAwarenessDailyPerformanceTable.search_date == target_date,
            BrandAwarenessDailyPerformanceTable.model == "all",
        )
    )
    brand_res = await db.execute(brand_stmt)
    brand_row = brand_res.scalar_one_or_none()

    # Fetch competitor metrics for the target date
    comp_stmt = select(BrandCompetitorsAwarenessDailyPerformanceTable).where(
        and_(
            BrandCompetitorsAwarenessDailyPerformanceTable.search_target_brand_id == brand_id,
            BrandCompetitorsAwarenessDailyPerformanceTable.segment == segment,
            BrandCompetitorsAwarenessDailyPerformanceTable.search_date == target_date,
            BrandCompetitorsAwarenessDailyPerformanceTable.model == "all",
        )
    )
    comp_res = await db.execute(comp_stmt)
    comp_rows = comp_res.scalars().all()

    # Fetch 7-day-ago brand data for trend calculation
    date_7d_ago = target_date - timedelta(days=7)
    brand_7d_stmt = select(BrandAwarenessDailyPerformanceTable).where(
        and_(
            BrandAwarenessDailyPerformanceTable.brand_id == brand_id,
            BrandAwarenessDailyPerformanceTable.segment == segment,
            BrandAwarenessDailyPerformanceTable.search_date == date_7d_ago,
            BrandAwarenessDailyPerformanceTable.model == "all",
        )
    )
    brand_7d_res = await db.execute(brand_7d_stmt)
    brand_7d_row = brand_7d_res.scalar_one_or_none()

    brand_sov = brand_row.share_of_visibility if brand_row else None
    brand_sov_7d = brand_7d_row.share_of_visibility if brand_7d_row else None
    brand_trend_7d = (
        round((brand_sov - brand_sov_7d) * 100, 2)
        if brand_sov is not None and brand_sov_7d is not None
        else None
    )

    competitors: list[CompetitorInfo] = [
        CompetitorInfo(
            name=signal_row.search_target_brand_name,
            sov=round(brand_sov * 100, 2) if brand_sov is not None else None,
            ssi=(
                round(brand_row.search_share_index * 100, 2)
                if brand_row and brand_row.search_share_index is not None
                else None
            ),
            position_strength=brand_row.position_strength if brand_row else None,
            trend_7d=brand_trend_7d,
            is_target=True,
        )
    ]

    top_threat_name = signal_row.top_competitor_brand_name
    for comp in comp_rows:
        is_top_threat = bool(top_threat_name and comp.competitor_brand_name == top_threat_name)
        comp_sov = comp.share_of_visibility
        competitors.append(
            CompetitorInfo(
                name=comp.competitor_brand_name,
                sov=round(comp_sov * 100, 2) if comp_sov is not None else None,
                ssi=(
                    round(comp.search_share_index * 100, 2)
                    if comp.search_share_index is not None
                    else None
                ),
                position_strength=comp.position_strength,
                trend_7d=(
                    round(comp.search_momentum * 100, 2)
                    if comp.search_momentum is not None
                    else None
                ),
                is_top_threat=is_top_threat,
            )
        )

    why_fired = _build_why_fired(signal_type, signal_data)

    # Enrich with SOV gap metric if data is available
    if brand_sov is not None and top_threat_name:
        top_comp_row = next(
            (c for c in comp_rows if c.competitor_brand_name == top_threat_name), None
        )
        if top_comp_row and top_comp_row.share_of_visibility is not None:
            sov_gap = (brand_sov - top_comp_row.share_of_visibility) * 100
            gap_status = "critical" if sov_gap < 0 else ("warning" if sov_gap < 5 else "ok")
            why_fired.metrics.insert(
                0,
                MetricItem(
                    label="SOV Gap vs Top Threat",
                    value=f"{sov_gap:.1f}%",
                    status=gap_status,
                ),
            )

    recommendations = build_recommendations(signal_type, signal_data)

    return SignalDetailResponse(
        signal=SignalInfo(
            type=signal_type,
            severity=signal_row.severity,
            score=signal_row.signal_score,
            created_date=signal_row.created_date,
        ),
        why_fired=why_fired,
        competitors=competitors,
        recommendations=recommendations,
    )


# ---------------------------------------------------------------------------
# Endpoint 3: Query drill-down
# ---------------------------------------------------------------------------


@router.get("/signal/{signal_type}/queries", response_model=QueryDrillDownResponse)
async def get_signal_queries(
    signal_type: str,
    brand_id: str = Query(...),
    segment: str = Query(...),
    date_str: Optional[str] = Query(
        None,
        alias="date",
        description="Date in YYYY-MM-DD format; defaults to today",
    ),
    action_type: str = Query(
        "view_affected_queries",
        description="view_affected_queries or compare_impressions",
    ),
    db: AsyncSession = Depends(get_db),
    _current_user: UsersTable = Depends(require_super_user),
) -> QueryDrillDownResponse:
    """Return query-level drill-down for a signal.

    - view_affected_queries: queries where brand's rank worsened vs. 7 days ago
    - compare_impressions: queries where top threat competitor gained rank vs. 7 days ago
    """
    target_date: DateType
    if date_str:
        try:
            target_date = DateType.fromisoformat(date_str)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid date format. Use YYYY-MM-DD.")
    else:
        target_date = DateType.today()

    date_7d_ago = target_date - timedelta(days=7)

    # Look up top threat competitor for compare_impressions mode
    top_threat_name: Optional[str] = None
    if action_type == "compare_impressions":
        insight_stmt = select(
            BrandPerformanceInsightTable.top_competitor_brand_name
        ).where(
            and_(
                BrandPerformanceInsightTable.search_target_brand_id == brand_id,
                BrandPerformanceInsightTable.segment == segment,
                BrandPerformanceInsightTable.signal_type == signal_type,
                BrandPerformanceInsightTable.created_date == target_date,
            )
        )
        insight_res = await db.execute(insight_stmt)
        top_threat_name = insight_res.scalar_one_or_none()

    # Fetch today's search results for the brand
    today_stmt = select(BrandSearchResultTable).where(
        and_(
            BrandSearchResultTable.search_target_brand_id == brand_id,
            BrandSearchResultTable.segment == segment,
            BrandSearchResultTable.search_date >= target_date,
            BrandSearchResultTable.search_date < target_date + timedelta(days=1),
        )
    )
    today_res = await db.execute(today_stmt)
    today_rows = today_res.scalars().all()

    if not today_rows:
        return QueryDrillDownResponse(queries=[])

    # Build lookup: prompt_text -> best matching row (prefer target brand's own row)
    today_by_prompt: dict[str, BrandSearchResultTable] = {}
    for row in today_rows:
        is_brand_row = (
            row.search_return_brand_name.lower() == row.search_target_brand_name.lower()
        )
        if is_brand_row or row.user_prompt not in today_by_prompt:
            today_by_prompt[row.user_prompt] = row

    prompt_texts = list(today_by_prompt.keys())

    # Fetch 7-day-ago results for the same prompts
    ago_stmt = select(BrandSearchResultTable).where(
        and_(
            BrandSearchResultTable.search_target_brand_id == brand_id,
            BrandSearchResultTable.segment == segment,
            BrandSearchResultTable.search_date >= date_7d_ago,
            BrandSearchResultTable.search_date < date_7d_ago + timedelta(days=1),
            BrandSearchResultTable.user_prompt.in_(prompt_texts),
        )
    )
    ago_res = await db.execute(ago_stmt)
    ago_rows = ago_res.scalars().all()

    ago_by_prompt: dict[str, BrandSearchResultTable] = {}
    for row in ago_rows:
        is_brand_row = (
            row.search_return_brand_name.lower() == row.search_target_brand_name.lower()
        )
        if is_brand_row or row.user_prompt not in ago_by_prompt:
            ago_by_prompt[row.user_prompt] = row

    # Fetch all competitors' rankings today for display purposes (scoped to this brand's queries)
    all_today_stmt = select(BrandSearchResultTable).where(
        and_(
            BrandSearchResultTable.search_target_brand_id == brand_id,
            BrandSearchResultTable.segment == segment,
            BrandSearchResultTable.search_date >= target_date,
            BrandSearchResultTable.search_date < target_date + timedelta(days=1),
            BrandSearchResultTable.user_prompt.in_(prompt_texts),
        )
    )
    all_today_res = await db.execute(all_today_stmt)
    all_today_rows = all_today_res.scalars().all()

    # Best competitor per prompt (not the target brand)
    best_competitor_by_prompt: dict[str, tuple[str, int]] = {}
    for row in all_today_rows:
        if row.search_target_brand_id == brand_id:
            continue
        prompt = row.user_prompt
        current_best = best_competitor_by_prompt.get(prompt)
        if current_best is None or row.search_return_ranking < current_best[1]:
            best_competitor_by_prompt[prompt] = (
                row.search_return_brand_name,
                row.search_return_ranking,
            )

    # Build base query rows
    query_rows: list[QueryRow] = []
    for prompt_text, today_row in today_by_prompt.items():
        brand_rank_today = today_row.search_return_ranking
        ago_row = ago_by_prompt.get(prompt_text)
        brand_rank_7d_ago = ago_row.search_return_ranking if ago_row else None
        rank_change = (
            brand_rank_today - brand_rank_7d_ago
            if brand_rank_7d_ago is not None
            else None
        )

        top_comp = best_competitor_by_prompt.get(prompt_text)
        query_rows.append(
            QueryRow(
                prompt_text=prompt_text,
                brand_rank_today=brand_rank_today,
                brand_rank_7d_ago=brand_rank_7d_ago,
                rank_change=rank_change,
                top_competitor_today=top_comp[0] if top_comp else None,
                top_competitor_rank=top_comp[1] if top_comp else None,
            )
        )

    if action_type == "view_affected_queries":
        # Keep only queries where rank worsened (rank increased), sorted by largest drop
        query_rows = [q for q in query_rows if q.rank_change is not None and q.rank_change > 0]
        query_rows.sort(key=lambda q: -(q.rank_change or 0))

    elif action_type == "compare_impressions" and top_threat_name:
        # Build threat today map from already-fetched all_today_rows
        threat_today_map: dict[str, int] = {
            r.user_prompt: r.search_return_ranking
            for r in all_today_rows
            if r.search_return_brand_name == top_threat_name
        }

        # Build threat ago map from already-fetched ago_rows
        threat_ago_map: dict[str, int] = {
            r.user_prompt: r.search_return_ranking
            for r in ago_rows
            if r.search_return_brand_name == top_threat_name
        }

        def _comp_gain(q: QueryRow) -> int:
            today_rank = threat_today_map.get(q.prompt_text)
            ago_rank = threat_ago_map.get(q.prompt_text)
            if today_rank is not None and ago_rank is not None:
                return ago_rank - today_rank  # positive = competitor improved rank
            return 0

        query_rows = [q for q in query_rows if _comp_gain(q) > 0]
        query_rows.sort(key=lambda q: -_comp_gain(q))

    else:
        # Default fallback: all queries sorted by largest rank worsening
        query_rows.sort(key=lambda q: -(q.rank_change or 0))

    return QueryDrillDownResponse(queries=query_rows)
