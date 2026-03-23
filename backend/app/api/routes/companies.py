from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.crud import create_company, get_company_by_cnpj
from app.models import CompanyCreate, CompanyPublic

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanyPublic)
def create_company_route(
    *, session: SessionDep, current_user: CurrentUser, company_in: CompanyCreate  # noqa: ARG001
) -> Any:
    """
    Create new company (PJ).
    """
    existing_company = get_company_by_cnpj(session=session, cnpj=company_in.cnpj)
    if existing_company:
        raise HTTPException(
            status_code=400,
            detail="A company with this CNPJ already exists.",
        )
    company = create_company(session=session, company_in=company_in)
    return company
