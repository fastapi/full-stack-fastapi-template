from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core.security import generate_jwt_token, get_password_hash
from app.models import (
    Message,
    NewPassword,
    OTPOAuthCreate,
    OTPOAuthVerify,
    OtpResend,
    RecoverPassword,
    Token,
    UserPublic,
    UserUpdate,
)
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return generate_jwt_token(user)


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/")
def recover_password(user_email: RecoverPassword, session: SessionDep) -> Message:
    """
    Password Recovery
    """
    user = crud.get_user_by_email(session=session, email=user_email.email)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=user_email.email)
    email_data = generate_reset_password_email(
        email_to=user.primary_email, username= user.full_name, token=password_reset_token
    )
    send_email(
        email_to=user.primary_email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    user = crud.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )


@router.post("/verify-otp/", response_model=UserPublic)
def verify_otp(session: SessionDep, otp_verification: OTPOAuthVerify):
    """
    Verify OTP for the user
    """
    try:
        user = crud.get_user_by_email(
            session=session, email=otp_verification.primary_email
        )
        if not user:
            raise HTTPException(
                status_code=404,
                detail="The user with this email does not exist in the system.",
            )
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        otp_obj = crud.get_otp_auth_by_user_id(session=session, user_id=user.id)
        if not otp_obj:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        if otp_obj.token != otp_verification.token:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        if not otp_obj.is_active():
            raise HTTPException(status_code=400, detail="Invalid OTP or OTP Expired")
        user_update = UserUpdate(email_verified_primary=True)
        user_email_verifed = crud.update_user(
            session=session, db_user=user, user_in=user_update
        )
        return user_email_verifed
    except SQLAlchemyError as e:
        # Rollback transaction in case of an exception
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Rollback transaction for any other exceptions
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resend-otp/", response_model=Message)
def resend_otp(session: SessionDep, otp_resend: OtpResend):
    """
    Resend OTP for the user
    """
    user = crud.get_user_by_email(session=session, email=otp_resend.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    otp_auth = OTPOAuthCreate(user_id=OtpResend.primary_email)
    crud.create_otp_auth(session=session, otp_auth_data=otp_auth)
    return Message(message="OTP resent successfully")
