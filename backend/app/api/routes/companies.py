import logging
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile

from app.api.deps import CurrentUser, SessionDep
from app.crud import create_company, get_company_by_cnpj
from app.models import CompanyCreate, CompanyPublic, ResumeData
from app.resume_parser import (
    extract_text_from_docx,
    extract_text_from_pdf,
    parse_resume_text,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companies", tags=["companies"])

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


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


@router.post("/parse-resume", response_model=ResumeData)
async def parse_resume(
    *, current_user: CurrentUser, file: UploadFile  # noqa: ARG001
) -> Any:
    """
    Parse a resume file (PDF or DOCX) and extract structured data.
    """
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Nenhum arquivo foi enviado.",
        )

    extension = ""
    if "." in file.filename:
        extension = "." + file.filename.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Formato de arquivo não suportado. Envie um arquivo PDF ou DOCX.",
        )

    try:
        file_bytes = await file.read()

        if extension == ".pdf":
            text = extract_text_from_pdf(file_bytes)
        else:
            text = extract_text_from_docx(file_bytes)

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Não foi possível extrair texto do arquivo. Verifique se o arquivo não está vazio ou protegido.",
            )

        parsed_data = parse_resume_text(text)
        return ResumeData(**parsed_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro ao processar currículo: %s", e)
        raise HTTPException(
            status_code=400,
            detail="Não foi possível ler o currículo enviado. Verifique o formato do arquivo e tente novamente.",
        )
