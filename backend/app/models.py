from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


# Session base table
class Session(SQLModel, table=True):
    session_id: str = Field(primary_key=True)
    bot_name: str = Field()
    user_id: str = Field()


# Summary features from Summary Merged v1.csv
class SummaryFeatures(SQLModel, table=True):
    session_id: str = Field(foreign_key="session.session_id", primary_key=True)
    conversation_summary: str = Field(default=None)
    human_values: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    chatbot_recommendations: list[str] = Field(
        default_factory=list, sa_column=Column(JSON)
    )
    chatbot_response_type: str = Field(default=None)


# Abandonment features from Abandonment Analysis O3.csv
class AbandonmentFeatures(SQLModel, table=True):
    session_id: str = Field(foreign_key="session.session_id", primary_key=True)
    abandonment_category: str = Field()
    abandonment_subcategory: str = Field()
    abandonment_reason: str = Field()
    number_of_completed_steps: int = Field()


# Meaningful features from Is Meaningful.csv
class MeaningfulFeatures(SQLModel, table=True):
    session_id: str = Field(foreign_key="session.session_id", primary_key=True)
    is_meaningful: bool = Field()
