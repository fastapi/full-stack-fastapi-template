from sqlmodel import Field, SQLModel


# Session base table
class Session(SQLModel, table=True):
    session_id: str = Field(primary_key=True)
    bot_name: str = Field()
    user_id: str = Field()


# Summary features from Summary Merged v1.csv
class SummaryFeatures(SQLModel, table=True):
    session_id: str = Field(foreign_key="session.session_id", primary_key=True)
    conversation_summary: str | None = Field(default=None)
    human_values: list[str] | None = Field(default=None)
    chatbot_recommendations: list[str] | None = Field(default=None)
    chatbot_response_type: str | None = Field(default=None)


# Abandonment features from Abandonment Analysis O3.csv
class AbandonmentFeatures(SQLModel, table=True):
    session_id: str = Field(foreign_key="session.session_id", primary_key=True)
    abandonment_category: str | None = Field(default=None)
    abandonment_subcategory: str | None = Field(default=None)
    abandonment_reason: str | None = Field(default=None)
    number_of_completed_steps: int | None = Field(default=None)


# Meaningful features from Is Meaningful.csv
class MeaningfulFeatures(SQLModel, table=True):
    session_id: str = Field(foreign_key="session.session_id", primary_key=True)
    is_meaningful: bool | None = Field(default=None)
