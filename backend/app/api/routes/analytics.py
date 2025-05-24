from datetime import date

import polars as pl
import pydantic  # Ensure pydantic is imported
from fastapi import APIRouter
from opentelemetry import trace
from sqlmodel import select

from app.api.deps import SessionDep  # SessionDep for dependency injection
from app.models import Item, User  # Assuming User model is in app.models, Import Item


# Pydantic models for response
class UserSignupTrend(pydantic.BaseModel):  # Corrected: pydantic.BaseModel
    signup_date: date
    count: int


class UserActivity(pydantic.BaseModel):  # Corrected: pydantic.BaseModel
    active_users: int
    inactive_users: int


class UserAnalyticsSummary(pydantic.BaseModel):  # Corrected: pydantic.BaseModel
    total_users: int
    signup_trends: list[UserSignupTrend]
    activity_summary: UserActivity
    # Add more fields as desired, e.g., average_items_per_user: float


# Pydantic models for Item analytics
class ItemCreationTrend(pydantic.BaseModel):
    creation_date: date
    count: int


# class ItemOwnerDistribution(pydantic.BaseModel): # Optional for now
#     owner_id: str
#     item_count: int


class ItemAnalyticsTrends(pydantic.BaseModel):
    total_items: int
    creation_trends: list[ItemCreationTrend]
    # owner_distribution: List[ItemOwnerDistribution] # Optional


router = APIRouter(prefix="/analytics", tags=["analytics"])
tracer = trace.get_tracer(__name__)


@router.get("/user-summary", response_model=UserAnalyticsSummary)
def get_user_summary(
    session: SessionDep,
) -> (
    UserAnalyticsSummary
):  # get_current_active_superuser is imported but not used here yet
    with tracer.start_as_current_span("user_summary_endpoint"):
        with tracer.start_as_current_span("fetch_all_users_sql"):
            statement = select(User)
            users_list = list(session.exec(statement).all())

        if not users_list:
            return UserAnalyticsSummary(
                total_users=0,
                signup_trends=[],
                activity_summary=UserActivity(active_users=0, inactive_users=0),
            )

        with tracer.start_as_current_span("convert_users_to_polars"):
            users_data = []
            for user in users_list:
                user_dict = {
                    "id": user.id,  # No explicit str() casting for now, per instructions
                    "email": user.email,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                    "full_name": user.full_name,
                }
                # Attempt to get 'created_at' if it exists (it doesn't in the standard model)
                if hasattr(user, "created_at") and user.created_at:
                    user_dict["created_at"] = user.created_at
                users_data.append(user_dict)

            if (
                not users_data
            ):  # Should not happen if users_list is not empty, but as a safe guard
                return UserAnalyticsSummary(
                    total_users=0,
                    signup_trends=[],
                    activity_summary=UserActivity(active_users=0, inactive_users=0),
                )

            # Create DataFrame without explicit casting of 'id' first.
            # If Polars errors on UUID, the instruction is to add:
            # df_users = df_users.with_columns(pl.col('id').cast(pl.Utf8))
            df_users = pl.DataFrame(users_data)

        total_users = df_users.height  # More idiomatic for Polars than len(df_users)

        with tracer.start_as_current_span("calculate_user_activity_polars"):
            active_users = df_users.filter(pl.col("is_active")).height
            inactive_users = total_users - active_users

        signup_trends_data = []
        if (
            "created_at" in df_users.columns
        ):  # This will be false as User model has no created_at
            with tracer.start_as_current_span("calculate_signup_trends_polars"):
                # Ensure 'created_at' is a datetime type. If string, parse it.
                # Assuming it's already a datetime.date or datetime.datetime from SQLModel
                # If it's datetime, cast to date for daily trends
                df_users_with_date = df_users.with_columns(
                    pl.col("created_at").cast(pl.Date).alias("signup_day")
                )

                signup_counts_df = (
                    df_users_with_date.group_by("signup_day")
                    .agg(pl.count().alias("count"))
                    .sort("signup_day")
                )

                signup_trends_data = [
                    UserSignupTrend(signup_date=row["signup_day"], count=row["count"])
                    for row in signup_counts_df.to_dicts()
                ]

        return UserAnalyticsSummary(
            total_users=total_users,
            signup_trends=signup_trends_data,  # Will be empty as 'created_at' is not in User model
            activity_summary=UserActivity(
                active_users=active_users, inactive_users=inactive_users
            ),
        )


@router.get("/item-trends", response_model=ItemAnalyticsTrends)
def get_item_trends(session: SessionDep) -> ItemAnalyticsTrends:
    with tracer.start_as_current_span("item_trends_endpoint"):
        with tracer.start_as_current_span("fetch_all_items_sql"):
            statement = select(Item)
            items_list = list(session.exec(statement).all())

        if not items_list:
            return ItemAnalyticsTrends(
                total_items=0,
                creation_trends=[],
                # owner_distribution=[] # Optional
            )

        with tracer.start_as_current_span("convert_items_to_polars"):
            items_data = []
            for item in items_list:
                item_dict = {
                    "id": str(item.id),  # Cast UUID to string
                    "title": item.title,
                    "description": item.description,
                    "owner_id": str(item.owner_id),  # Cast UUID to string
                }
                # IMPORTANT: Item model does not have 'created_at'.
                # This will result in empty creation_trends.
                if hasattr(item, "created_at") and item.created_at:
                    item_dict["created_at"] = item.created_at
                items_data.append(item_dict)

            if not items_data:  # Safety check
                return ItemAnalyticsTrends(total_items=0, creation_trends=[])

            df_items = pl.DataFrame(items_data)

        total_items = df_items.height

        creation_trends_data = []
        if "created_at" in df_items.columns:
            with tracer.start_as_current_span("calculate_item_creation_trends_polars"):
                # Ensure 'created_at' is datetime, then cast to date for daily trends
                df_items_with_date = df_items.with_columns(
                    pl.col("created_at").cast(pl.Date).alias("creation_day")
                )

                creation_counts_df = (
                    df_items_with_date.group_by("creation_day")
                    .agg(pl.count().alias("count"))
                    .sort("creation_day")
                )

                creation_trends_data = [
                    ItemCreationTrend(
                        creation_date=row["creation_day"], count=row["count"]
                    )
                    for row in creation_counts_df.to_dicts()
                ]

        # Placeholder for owner distribution if implemented later
        # owner_distribution_data = []

        return ItemAnalyticsTrends(
            total_items=total_items,
            creation_trends=creation_trends_data,
            # owner_distribution=owner_distribution_data # Optional
        )
