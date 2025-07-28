import json
from pathlib import Path

import pandas as pd
from loguru import logger
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.models import (
    AbandonmentFeatures,
    ChallengeAnalysis,
    MeaningfulFeatures,
    SummaryFeatures,
)
from app.models import Session as SessionModel

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def load_csv_data(session: Session) -> None:
    """Load data from CSV files into the database."""

    # Get the project root directory (assuming we're in backend/app/)
    project_root = Path(__file__).parent.parent.parent
    dataset_path = project_root / "dataset" / "analytics-csv"

    # Check if dataset directory exists
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_path}")

    # Load Summary Merged data
    summary_file = dataset_path / "Summary Merged v1.csv"
    logger.info("Loading Summary Merged data...")
    summary_df = pd.read_csv(
        summary_file, converters={"outputs": json.loads, "run": json.loads}
    )

    # Extract features
    summary_df["conversation_summary"] = summary_df["outputs"].apply(
        lambda x: x.get("conversation_summary")
    )
    summary_df["human_values"] = summary_df["outputs"].apply(
        lambda x: x.get("human_values")
    )
    summary_df["chatbot_recommendations"] = summary_df["outputs"].apply(
        lambda x: x.get("chatbot_recommendations")
    )
    summary_df["chatbot_response_type"] = summary_df["outputs"].apply(
        lambda x: x.get("chatbot_response_type")
    )
    summary_df["bot_name"] = summary_df["run"].apply(
        lambda x: x.get("extra", {}).get("metadata", {}).get("ls_example_bot_name")
    )
    summary_df["session_id"] = summary_df["run"].apply(
        lambda x: x.get("extra", {}).get("metadata", {}).get("ls_example_session_id")
    )
    summary_df["user_id"] = summary_df["run"].apply(
        lambda x: x.get("extra", {}).get("metadata", {}).get("ls_example_user_id")
    )

    # Insert sessions and summary features
    for _, row in summary_df.iterrows():
        # Insert or update session
        existing_session = session.get(SessionModel, row["session_id"])
        if not existing_session:
            session_obj = SessionModel(
                session_id=row["session_id"],
                bot_name=row["bot_name"],
                user_id=row["user_id"],
            )
            session.add(session_obj)

        # Insert summary features
        summary_features = SummaryFeatures(
            session_id=row["session_id"],
            conversation_summary=row["conversation_summary"],
            human_values=row["human_values"],
            chatbot_recommendations=row["chatbot_recommendations"],
            chatbot_response_type=row["chatbot_response_type"],
        )
        session.merge(summary_features)

    session.commit()
    logger.info(f"Loaded {len(summary_df)} summary records")

    # Load Abandonment Analysis data
    abandonment_file = dataset_path / "Abandonment Analysis O3.csv"
    logger.info("Loading Abandonment Analysis data...")
    abandonment_df = pd.read_csv(
        abandonment_file, converters={"outputs": json.loads, "run": json.loads}
    )

    # Extract features
    abandonment_df["abandonment_category"] = abandonment_df["outputs"].apply(
        lambda x: x.get("abandonment_category")
    )
    abandonment_df["abandonment_subcategory"] = abandonment_df["outputs"].apply(
        lambda x: x.get("abandonment_subcategory")
    )
    abandonment_df["abandonment_reason"] = abandonment_df["outputs"].apply(
        lambda x: x.get("abandonment_reason")
    )
    abandonment_df["number_of_completed_steps"] = abandonment_df["outputs"].apply(
        lambda x: x.get("number_of_completed_steps")
    )
    abandonment_df["bot_name"] = abandonment_df["run"].apply(
        lambda x: x.get("extra", {}).get("metadata", {}).get("ls_example_bot_name")
    )
    abandonment_df["session_id"] = abandonment_df["run"].apply(
        lambda x: x.get("extra", {}).get("metadata", {}).get("ls_example_session_id")
    )

    abandonment_df["user_id"] = abandonment_df["run"].apply(
        lambda x: x.get("extra", {}).get("metadata", {}).get("ls_example_user_id")
    )

    # Insert sessions and abandonment features
    for _, row in abandonment_df.iterrows():
        # Insert or update session
        existing_session = session.get(SessionModel, row["session_id"])
        if not existing_session:
            session_obj = SessionModel(
                session_id=row["session_id"],
                bot_name=row["bot_name"],
                user_id=row["user_id"],
            )
            session.add(session_obj)

        # Insert abandonment features
        abandonment_features = AbandonmentFeatures(
            session_id=row["session_id"],
            abandonment_category=row["abandonment_category"],
            abandonment_subcategory=row["abandonment_subcategory"],
            abandonment_reason=row["abandonment_reason"],
            number_of_completed_steps=int(row["number_of_completed_steps"]),
        )
        session.merge(abandonment_features)

    session.commit()
    logger.info(f"Loaded {len(abandonment_df)} abandonment records")

    # Load Is Meaningful data
    meaningful_file = dataset_path / "Is Meaningful.csv"
    logger.info("Loading Is Meaningful data...")
    meaningful_df = pd.read_csv(
        meaningful_file, converters={"outputs": json.loads, "run": json.loads}
    )

    # Extract features
    meaningful_df["is_meaningful"] = meaningful_df["outputs"].apply(
        lambda x: x.get("is_meaningful")
    )
    meaningful_df["bot_name"] = meaningful_df["run"].apply(
        lambda x: x.get("extra", {}).get("metadata", {}).get("ls_example_bot_name")
    )
    meaningful_df["session_id"] = meaningful_df["run"].apply(
        lambda x: x.get("extra", {}).get("metadata", {}).get("ls_example_session_id")
    )
    meaningful_df["user_id"] = meaningful_df["run"].apply(
        lambda x: x.get("extra", {}).get("metadata", {}).get("ls_example_user_id")
    )

    # Insert sessions and meaningful features
    for _, row in meaningful_df.iterrows():
        # Insert or update session
        existing_session = session.get(SessionModel, row["session_id"])
        if not existing_session:
            session_obj = SessionModel(
                session_id=row["session_id"],
                bot_name=row["bot_name"],
                user_id=row["user_id"],
            )
            session.add(session_obj)

        # Insert meaningful features
        meaningful_features = MeaningfulFeatures(
            session_id=row["session_id"],
            is_meaningful=bool(row["is_meaningful"]),
        )
        session.merge(meaningful_features)

    session.commit()
    logger.info(f"Loaded {len(meaningful_df)} meaningful records")

    # Load Topic and Challenge Analysis data
    challenge_file = dataset_path / "Topic and Challenge Analysis.csv"
    logger.info("Loading Topic and Challenge Analysis data...")
    challenge_df = pd.read_csv(
        challenge_file, converters={"outputs": json.loads, "run": json.loads}
    )

    # Extract features
    challenge_df["high_level_topic_name"] = challenge_df["outputs"].apply(
        lambda x: x.get("high_level_topic_name")
    )
    challenge_df["challenge_name"] = challenge_df["outputs"].apply(
        lambda x: x.get("challenge_name")
    )
    challenge_df["challenge_summary"] = challenge_df["outputs"].apply(
        lambda x: x.get("challenge_summary")
    )
    challenge_df["bot_name"] = challenge_df["run"].apply(
        lambda x: x.get("extra", {}).get("metadata", {}).get("ls_example_bot_name")
    )
    challenge_df["session_id"] = challenge_df["run"].apply(
        lambda x: x.get("extra", {}).get("metadata", {}).get("ls_example_session_id")
    )
    challenge_df["user_id"] = challenge_df["run"].apply(
        lambda x: x.get("extra", {}).get("metadata", {}).get("ls_example_user_id")
    )

    # Insert sessions and challenge features
    for _, row in challenge_df.iterrows():
        # Insert or update session
        existing_session = session.get(SessionModel, row["session_id"])
        if not existing_session:
            session_obj = SessionModel(
                session_id=row["session_id"],
                bot_name=row["bot_name"],
                user_id=row["user_id"],
            )
            session.add(session_obj)

        # Insert challenge features
        challenge_features = ChallengeAnalysis(
            session_id=row["session_id"],
            high_level_topic_name=row["high_level_topic_name"],
            challenge_name=row["challenge_name"],
            challenge_summary=row["challenge_summary"],
        )
        session.merge(challenge_features)

    session.commit()
    logger.info(f"Loaded {len(challenge_df)} challenge analysis records")


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    SQLModel.metadata.create_all(engine)

    load_csv_data(session)
