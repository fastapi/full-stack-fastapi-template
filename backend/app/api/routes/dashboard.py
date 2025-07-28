from collections import Counter
from typing import Any

from fastapi import APIRouter
from sqlalchemy import distinct
from sqlmodel import func, select

from app.api.deps import SessionDep
from app.models import AbandonmentFeatures, ChallengeAnalysis, Session, SummaryFeatures

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
                "completion_percentage_per_session": [],
                "number_of_total_steps": TOTAL_NUMBER_OF_STEPS_FOR_BOT[bot_name],
            }

        completion_percentage = (
            completed_steps / TOTAL_NUMBER_OF_STEPS_FOR_BOT[bot_name]
        )
        bot_stats[bot_name]["completion_percentage_per_session"].append(
            completion_percentage
        )

    # Calculate completion percentages
    completion_stats = {}
    for bot_name, stats in bot_stats.items():
        completion_percentage = 0
        if len(stats["completion_percentage_per_session"]) > 0:
            completion_percentage = sum(
                stats["completion_percentage_per_session"]
            ) / len(stats["completion_percentage_per_session"])

        completion_stats[bot_name] = {
            "completion_percentage": round(completion_percentage, 2),
            "number_of_total_steps": TOTAL_NUMBER_OF_STEPS_FOR_BOT[bot_name],
        }

    return {"bot_completion_stats": completion_stats}


@router.get("/stats/top-human-values")
def top_human_values(session: SessionDep, limit: int = 10) -> dict[str, Any]:
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
    all_values = [
        value.lower().replace("_", " ").strip().title() for value in all_values
    ]

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

    response = {
        "top_human_values": top_human_values,
        "total_values_analyzed": len(all_values),
    }

    return response


@router.get("/stats/top-chatbot-recommendations")
def get_top_chatbot_recommendations(
    session: SessionDep, limit: int = 10
) -> dict[str, Any]:
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

    all_recommendations = [
        recommendation.lower().replace("_", " ").strip().title()
        for recommendation in all_recommendations
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


@router.get("/stats/top-leadership-challenges")
def get_top_leadership_challenges(
    session: SessionDep, limit: int = 6, num_summaries: int = 5
) -> dict[str, Any]:
    """
    Get top leadership challenges with their subcategories and challenge summaries.
    Returns top 5 subcategories and up to 5 challenge summaries for each subcategory.
    """
    # Get all challenge analysis data

    results = session.exec(select(ChallengeAnalysis)).all()

    # Group by subcategory (challenge_name) and count occurrences
    subcategory_data = {}
    for item in results:
        # Clean up the data
        topic_name = item.high_level_topic_name
        topic_name = topic_name.strip() if topic_name else "Unknown"

        challenge_name = item.challenge_name
        challenge_name = challenge_name.strip() if challenge_name else "Unknown"

        challenge_summary = item.challenge_summary
        challenge_summary = item.challenge_summary.strip() if challenge_summary else ""

        if "Unknown" in topic_name or "Other" in topic_name:
            continue

        if challenge_name not in subcategory_data:
            subcategory_data[challenge_name] = {
                "category": topic_name,
                "challenge_name": challenge_name,
                "count": 0,
                "summaries": [],
            }

        subcategory_data[challenge_name]["count"] += 1
        if (
            challenge_summary
            and challenge_summary not in subcategory_data[challenge_name]["summaries"]
        ):
            subcategory_data[challenge_name]["summaries"].append(challenge_summary)

    # Sort by count and get top subcategories
    sorted_subcategories = sorted(
        subcategory_data.values(), key=lambda x: x["count"], reverse=True
    )[:limit]

    # Format the response with up to 5 summaries per subcategory
    top_challenges = []
    for subcategory in sorted_subcategories:
        # Limit to 5 summaries per subcategory
        limited_summaries = subcategory["summaries"][:num_summaries]

        top_challenges.append(
            {
                "category": subcategory["category"],
                "challenge_name": subcategory["challenge_name"],
                "count": subcategory["count"],
                "summaries": limited_summaries,
            }
        )

    return {
        "top_leadership_challenges": top_challenges,
        "total_challenges_analyzed": len(results),
    }
