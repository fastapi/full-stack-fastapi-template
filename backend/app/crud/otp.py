from uuid import UUID
from sqlmodel import Session
from sqlalchemy import desc
from app.models import OTPOAuth, OTPOAuthCreate

def create_otp_auth(*, session: Session, otp_auth_data: OTPOAuthCreate) -> OTPOAuth:
    db_obj = OTPOAuth.model_validate(otp_auth_data)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def get_otp_auth_by_user_id(*, session: Session, user_id: UUID) -> OTPOAuth:
    return session.query(OTPOAuth).filter(OTPOAuth.user_id == user_id).order_by(desc(OTPOAuth.id)).first()


def delete_otp_auth(*, session: Session, db_otp_auth: OTPOAuth) -> None:
    session.delete(db_otp_auth)
    session.commit()
