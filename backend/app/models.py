from sqlmodel import SQLModel


# Generic message
class Message(SQLModel):
    message: str
