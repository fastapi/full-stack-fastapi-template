from collections import Counter
from typing import Any

from fastapi import APIRouter
from sqlalchemy import distinct
from sqlmodel import func, select

from app.api.deps import SessionDep
from app.models import AbandonmentFeatures, MeaningfulFeatures, Session, SummaryFeatures

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Total number of steps for each bot (for completion percentage calculation)
TOTAL_NUMBER_OF_STEPS_FOR_BOT = {
    "assessment_actionplan_en": 7,
    "player_mindset_en": 7,
    "assessment_debrief_en": 5,
}


@router.get("/stats/total-sessions")
def get_total_sessions(session: SessionDep) -> dict[str, int]:
    """
    Get total number of sessions.
    """
    count_statement = select(func.count()).select_from(Session)
    total_sessions = session.exec(count_statement).one()

    return {"total_sessions": total_sessions}


@router.get("/stats/active-users")
def get_active_users(session: SessionDep) -> dict[str, int]:
    """
    Get total number of active users.
    """
    count_statement = select(func.count(distinct(Session.user_id))).select_from(Session)
    active_users = session.exec(count_statement).one()

    return {"active_users": active_users}


@router.get("/stats/bot-completion")
def get_bot_completion_percentage(session: SessionDep) -> dict[str, Any]:
    """
    Get completion percentage for each bot.
    Completion is calculated based on number_of_completed_steps vs total steps for each bot.
    """
    # Get all sessions with their abandonment data
    statement = select(
        Session.bot_name, AbandonmentFeatures.number_of_completed_steps
    ).join(
        AbandonmentFeatures,
        Session.session_id == AbandonmentFeatures.session_id,
        isouter=True,
    )

    results = session.exec(statement).all()

    # Group by bot_name and calculate completion stats
    bot_stats = {}
    for bot_name, completed_steps in results:
        if bot_name not in bot_stats:
            bot_stats[bot_name] = {
                "total_sessions": 0,
                "completed_sessions": 0,
                "total_steps": TOTAL_NUMBER_OF_STEPS_FOR_BOT[bot_name],
            }

        bot_stats[bot_name]["total_sessions"] += 1

        # Consider a session completed if completed_steps equals total_steps for that bot
        if (
            completed_steps is not None
            and completed_steps >= TOTAL_NUMBER_OF_STEPS_FOR_BOT[bot_name]
        ):
            bot_stats[bot_name]["completed_sessions"] += 1

    # Calculate completion percentages
    completion_stats = {}
    for bot_name, stats in bot_stats.items():
        completion_percentage = 0
        if stats["total_sessions"] > 0:
            completion_percentage = (
                stats["completed_sessions"] / stats["total_sessions"]
            ) * 100

        completion_stats[bot_name] = {
            "total_sessions": stats["total_sessions"],
            "completed_sessions": stats["completed_sessions"],
            "completion_percentage": round(completion_percentage, 2),
            "total_steps_required": stats["total_steps"],
        }

    return {"bot_completion_stats": completion_stats}


@router.get("/stats/top-human-values")
def get_top_human_values(
    session: SessionDep, limit: int = 10
) -> dict[str, list[dict[str, Any]]]:
    """
    Get top human values across all sessions.
    """
    # Get all human values from summary features
    statement = select(SummaryFeatures.human_values).where(
        SummaryFeatures.human_values.is_not(None)
    )

    results = session.exec(statement).all()

    # Flatten the list of lists and count occurrences
    all_values = []
    for human_values_list in results:
        if human_values_list:
            all_values.extend(human_values_list)

    all_values = [value for value in all_values if value != "none"]

    # Count occurrences and get top values
    value_counts = Counter(all_values)
    top_values = value_counts.most_common(limit)

    # Format the response
    top_human_values = [
        {
            "value": value,
            "count": count,
            "percentage": round((count / len(all_values)) * 100, 2),
        }
        for value, count in top_values
    ]

    return {
        "top_human_values": top_human_values,
        "total_values_analyzed": len(all_values),
    }


@router.get("/stats/top-chatbot-recommendations")
def get_top_chatbot_recommendations(
    session: SessionDep, limit: int = 10
) -> dict[str, list[dict[str, Any]]]:
    """
    Get top chatbot recommendations across all sessions.
    """
    # Get all chatbot recommendations from summary features
    statement = select(SummaryFeatures.chatbot_recommendations).where(
        SummaryFeatures.chatbot_recommendations.is_not(None)
    )

    results = session.exec(statement).all()

    # Flatten the list of lists and count occurrences
    all_recommendations = []
    for recommendations_list in results:
        if recommendations_list:
            all_recommendations.extend(recommendations_list)

    all_recommendations = [
        recommendation
        for recommendation in all_recommendations
        if recommendation != "none"
    ]

    # Count occurrences and get top recommendations
    recommendation_counts = Counter(all_recommendations)
    top_recommendations = recommendation_counts.most_common(limit)

    # Format the response
    top_chatbot_recommendations = [
        {
            "recommendation": recommendation,
            "count": count,
            "percentage": round((count / len(all_recommendations)) * 100, 2),
        }
        for recommendation, count in top_recommendations
    ]

    return {
        "top_chatbot_recommendations": top_chatbot_recommendations,
        "total_recommendations_analyzed": len(all_recommendations),
    }


@router.get("/stats/overview")
def get_dashboard_overview(session: SessionDep) -> dict[str, Any]:
    """
    Get comprehensive dashboard overview with all key statistics.
    """
    # Get total sessions
    total_sessions_result = get_total_sessions(session)

    # Get bot completion stats
    bot_completion_result = get_bot_completion_percentage(session)

    # Get top human values (top 5 for overview)
    top_human_values_result = get_top_human_values(session, limit=5)

    # Get top chatbot recommendations (top 5 for overview)
    top_recommendations_result = get_top_chatbot_recommendations(session, limit=5)

    # Get meaningful sessions count
    meaningful_count_statement = (
        select(func.count())
        .select_from(MeaningfulFeatures)
        .where(MeaningfulFeatures.is_meaningful)
    )
    meaningful_sessions = session.exec(meaningful_count_statement).one()

    return {
        "total_sessions": total_sessions_result["total_sessions"],
        "meaningful_sessions": meaningful_sessions,
        "bot_completion_stats": bot_completion_result["bot_completion_stats"],
        "top_human_values": top_human_values_result["top_human_values"],
        "top_chatbot_recommendations": top_recommendations_result[
            "top_chatbot_recommendations"
        ],
    }
