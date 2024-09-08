import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlmodel import func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    get_db_transaction,
)
from app.core.config import settings
from app.core.security import generate_jwt_token, get_password_hash, verify_password
from app.models import (
    JobPreferences,
    JobTitlePreference,
    JobTypePreference,
    Message,
    OAuthRegisterPayload,
    OTPOAuthCreate,
    Token,
    UpdatePassword,
    User,
    UserCreate,
    UserOnboarding,
    UserOnBoardingPayload,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import (
    generate_new_account_email,
    generate_new_account_email_otp,
    send_email,
)

logging.basicConfig(level=logging.INFO)
router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    try:
        session.begin()
        user = crud.get_user_by_email(session=session, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )

        user = crud.create_user(session=session, user_create=user_in)
        if settings.emails_enabled and user_in.email:
            email_data = generate_new_account_email(
                email_to=user_in.email, username=user_in.full_name, password=user_in.password
            )
            send_email(
                email_to=user_in.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )
        return user
    except SQLAlchemyError as e:
        # Rollback transaction in case of an exception
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Rollback transaction for any other exceptions
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    # statement = delete(Item).where(col(Item.owner_id) == current_user.id)
    session.exec(statement)  # type: ignore
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(user_in: UserRegister,db: Session = Depends(get_db_transaction), ) -> Any:
    """
    Create new user without the need to be logged in.
    """
    try:
        # if not settings.USERS_OPEN_REGISTRATION:
        #     raise HTTPException(
        #         status_code=403,
        #         detail="Open user registration is forbidden on this server",
        #     )
        user = crud.get_user_by_email(session=db, email=user_in.primary_email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system",
            )
        user_create = UserCreate.model_validate(user_in)
        user = crud.create_user(session=db, user_create=user_create)
        if settings.emails_enabled and user_in.primary_email:
            otp_createobj = OTPOAuthCreate(user_id=user.id)
            otp_obj = crud.create_otp_auth(session=db, otp_auth_data=otp_createobj)
            email_data = generate_new_account_email_otp(
                email_to=user.primary_email, username=user.full_name, otp=otp_obj.token
            )
            send_email(
                email_to=user_in.primary_email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )
        db.commit()
        return user
    except SQLAlchemyError as e:
        # Rollback transaction in case of an exception
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Rollback transaction for any other exceptions
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/signup/oauth/google", response_model=Token)
def register_user_oauth(*, session: SessionDep, user_in:OAuthRegisterPayload) -> Token:
    """
    Registers a user using OAuth
    """
    try:
        user = crud.get_user_by_email(session=session, email=user_in.user.primary_email)
        if user:
            return generate_jwt_token(user)
        user_create: User = crud.create_user_given_oauth(session=session, user_in=user_in)
        return generate_jwt_token(user_create)
    except SQLAlchemyError as e:
        # Rollback transaction in case of an exception
        session.flush()
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Rollback transaction for any other exceptions
        session.flush()
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 

@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: int,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: int
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    # statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)  # type: ignore
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")

@router.post("/onboarding/")
def add_user_onboarding(session: SessionDep, current_user: CurrentUser, onboarding_data: UserOnBoardingPayload) -> Message:
    """
    Add user onboarding data
    """
    try:
        with session.begin():
            onboarding = UserOnboarding(
                user_id = current_user.id,
                urgency_level = onboarding_data.urgency_level
            )
            session.add(onboarding)
            session.flush()
            job_preferences = JobPreferences(
                location= onboarding_data.location,
                location_coordinates = onboarding_data.location_coordinates,
                remote_bool = onboarding_data.remote_bool,
                h1b_bool = onboarding_data.h1b_bool,
                onboarding_id = onboarding.id
            )
            session.add(job_preferences)
            session.flush()
            job_title_prefs = [JobTitlePreference(jobtitle_id=title.jobtitle_id, pref_jobs_id=job_preferences.id)
                                for title in onboarding_data.pref_job_title]
            job_type_prefs = [JobTypePreference(jobtype_id=_.jobtype_id, pref_jobs_id=job_preferences.id)
                                for _ in onboarding_data.pref_job_type]
            session.add_all(job_title_prefs + job_type_prefs)
            session.commit()
            current_user.onboarded = True
            session.add(current_user)
            session.commit()
            return Message(message="User onboarding data added successfully")  # type: ignore
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))



    