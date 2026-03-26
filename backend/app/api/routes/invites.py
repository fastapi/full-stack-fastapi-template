import logging
import uuid as uuid_mod
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.crud import (
    complete_company_registration,
    create_company_initial,
    create_company_invite,
    get_company_by_cnpj,
    get_invite_by_token,
)
from app.models import (
    CompanyInvite,
    CompanyInviteCreate,
    CompanyInvitePublic,
    CompanyInviteValidation,
    CompanyPublic,
    CompanyRegistrationComplete,
    CompanyStatus,
)
from app.utils import (
    generate_invite_token,
    generate_pj_invite_email,
    send_email,
    verify_invite_token,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/invites", tags=["invites"])


@router.post("/", response_model=CompanyInvitePublic)
def send_invite(
    *,
    session: SessionDep,
    current_user: CurrentUser,  # noqa: ARG001
    invite_in: CompanyInviteCreate,
) -> Any:
    """
    Send a PJ registration invite. Creates initial company record and sends email.
    Only authorized internal users (Juridico, Financeiro, RH, Comercial) can send invites.
    """
    existing_company = get_company_by_cnpj(session=session, cnpj=invite_in.cnpj)

    if existing_company and existing_company.status == CompanyStatus.completed:
        raise HTTPException(
            status_code=400,
            detail="Uma empresa com este CNPJ já possui cadastro completo.",
        )

    if existing_company:
        company = existing_company
        company.email = invite_in.email
        session.add(company)
        session.commit()
        session.refresh(company)
    else:
        company = create_company_initial(
            session=session,
            cnpj=invite_in.cnpj,
            email=invite_in.email,
        )

    token, expires_at = generate_invite_token(
        company_id=str(company.id),
        email=invite_in.email,
    )

    invite = create_company_invite(
        session=session,
        company_id=company.id,
        email=invite_in.email,
        token=token,
        expires_at=expires_at,
    )

    link = f"{settings.FRONTEND_HOST}/pj-registration?token={token}"

    try:
        email_data = generate_pj_invite_email(
            email_to=invite_in.email,
            link=link,
            valid_days=settings.INVITE_TOKEN_EXPIRE_DAYS,
        )
        send_email(
            email_to=invite_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    except Exception as e:
        logger.error(
            "Falha ao enviar e-mail de convite para %s (company_id=%s, invite_id=%s): %s",
            invite_in.email,
            company.id,
            invite.id,
            e,
        )
        raise HTTPException(
            status_code=500,
            detail="Falha ao enviar o e-mail de convite. O convite foi criado, tente reenviar.",
        )

    return invite


@router.post("/{invite_id}/resend", response_model=CompanyInvitePublic)
def resend_invite(
    *,
    session: SessionDep,
    current_user: CurrentUser,  # noqa: ARG001
    invite_id: str,
) -> Any:
    """
    Resend a PJ registration invite. Generates a new token and sends a new email.
    """
    try:
        invite_uuid = uuid_mod.UUID(invite_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de convite inválido.")

    statement = select(CompanyInvite).where(CompanyInvite.id == invite_uuid)
    old_invite = session.exec(statement).first()

    if not old_invite:
        raise HTTPException(status_code=404, detail="Convite não encontrado.")

    if old_invite.used:
        raise HTTPException(
            status_code=400,
            detail="Este convite já foi utilizado. O cadastro já foi completado.",
        )

    company = old_invite.company
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")

    old_invite.used = True
    session.add(old_invite)
    session.commit()

    token, expires_at = generate_invite_token(
        company_id=str(company.id),
        email=old_invite.email,
    )

    new_invite = create_company_invite(
        session=session,
        company_id=company.id,
        email=old_invite.email,
        token=token,
        expires_at=expires_at,
    )

    link = f"{settings.FRONTEND_HOST}/pj-registration?token={token}"

    try:
        email_data = generate_pj_invite_email(
            email_to=old_invite.email,
            link=link,
            valid_days=settings.INVITE_TOKEN_EXPIRE_DAYS,
        )
        send_email(
            email_to=old_invite.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    except Exception as e:
        logger.error(
            "Falha ao reenviar e-mail de convite para %s (invite_id=%s): %s",
            old_invite.email,
            new_invite.id,
            e,
        )
        raise HTTPException(
            status_code=500,
            detail="Falha ao reenviar o e-mail de convite. Tente novamente.",
        )

    return new_invite


@router.get("/validate", response_model=CompanyInviteValidation)
def validate_invite_token(
    *,
    session: SessionDep,
    token: str,
) -> Any:
    """
    Validate an invite token. Public endpoint (no auth required).
    Returns company data if token is valid.
    """
    token_data = verify_invite_token(token)
    if not token_data:
        return CompanyInviteValidation(
            valid=False,
            message="O link é inválido ou expirou. Solicite um novo convite ao responsável interno.",
        )

    invite = get_invite_by_token(session=session, token=token)
    if not invite:
        return CompanyInviteValidation(
            valid=False,
            message="O link é inválido ou expirou. Solicite um novo convite ao responsável interno.",
        )

    if invite.used:
        return CompanyInviteValidation(
            valid=False,
            message="Este convite já foi utilizado. O cadastro já foi completado.",
        )

    company = invite.company
    if not company:
        return CompanyInviteValidation(
            valid=False,
            message="Empresa não encontrada.",
        )

    return CompanyInviteValidation(
        valid=True,
        company=CompanyPublic.model_validate(company),
    )


@router.put("/complete", response_model=CompanyPublic)
def complete_registration(
    *,
    session: SessionDep,
    registration_data: CompanyRegistrationComplete,
) -> Any:
    """
    Complete PJ registration. Public endpoint (no auth required).
    Requires a valid invite token.
    """
    token_data = verify_invite_token(registration_data.token)
    if not token_data:
        raise HTTPException(
            status_code=400,
            detail="O link é inválido ou expirou. Solicite um novo convite ao responsável interno.",
        )

    invite = get_invite_by_token(session=session, token=registration_data.token)
    if not invite:
        raise HTTPException(
            status_code=400,
            detail="Convite não encontrado.",
        )

    if invite.used:
        raise HTTPException(
            status_code=400,
            detail="Este convite já foi utilizado.",
        )

    company = invite.company
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Empresa não encontrada.",
        )

    updated_company = complete_company_registration(
        session=session,
        company=company,
        invite=invite,
        registration_data=registration_data,
    )

    return updated_company
