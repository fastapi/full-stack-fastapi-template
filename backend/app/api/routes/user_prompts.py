from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import logging
from typing import List
import json

from app.services.local_ai_services import local_model_service
from app.models.prompts_schemas import PromptRequest, PromptResponse, AlternativePromptsResponse, ReferencePromptRequest
from kila_models.models import BrandPromptTable
from app.core.db import get_db
from app.config.prompts import system_prompts


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/", response_model=PromptResponse, status_code=201)
async def create_prompt(
        request: PromptRequest,
        database: AsyncSession = Depends(get_db)
):
    """
    Create a new prompt and process it with AI model.
    Uses idempotency_key to prevent duplicate submissions.
    """
    try:
        # Check for existing prompt with same idempotency key
        stmt = select(BrandPromptTable).where(
            BrandPromptTable.idempotency_key == request.idempotency_key
        )
        result = await database.execute(stmt)
        existing_prompt: PromptResponse = result.scalar_one_or_none()

        if existing_prompt:
            logger.info(f"Duplicate request detected for idempotency_key: {request.idempotency_key}")
            return PromptResponse(
                id=existing_prompt.id,
                prompt=existing_prompt.prompt,
                project_name=existing_prompt.project_name,
                user_id=existing_prompt.user_id,
                idempotency_key=existing_prompt.idempotency_key,
                created_at=existing_prompt.created_at,
                is_duplicate=True,
                company_id=existing_prompt.company_id,
                is_active=existing_prompt.is_active
            )

        # Create new prompt record with pending status
        new_prompt = BrandPromptTable(
            prompt=request.prompt,
            project_name=request.project_name,
            user_id=request.user_id,
            idempotency_key=request.idempotency_key,
            company_id=request.company_id
        )

        database.add(new_prompt)
        # await database.flush()  # Get the ID without committing

        await database.commit()
        await database.refresh(new_prompt)

        return PromptResponse(
            id=new_prompt.id,
            prompt=new_prompt.prompt,
            project_name=new_prompt.project_name,
            user_id=new_prompt.user_id,
            idempotency_key=new_prompt.idempotency_key,
            created_at=new_prompt.created_at,
            is_duplicate=False,
            company_id=new_prompt.company_id,
            is_active=new_prompt.is_active
        )

    except IntegrityError as e:
        await database.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        raise HTTPException(
            status_code=409,
            detail="Prompt with this idempotency key already exists"
        )
    except Exception as e:
        await database.rollback()
        logger.error(f"Unexpected error creating prompt: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/prompt_id/{prompt_id}", response_model=PromptResponse)
async def get_prompt_by_id(
        prompt_id: int,
        database: AsyncSession = Depends(get_db)
):
    """Retrieve a specific prompt by ID"""
    stmt = select(BrandPromptTable).where(BrandPromptTable.id == prompt_id)
    result = await database.execute(stmt)
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return PromptResponse(
        id=prompt.id,
        prompt=prompt.prompt,
        project_name=prompt.project_name,
        user_id=prompt.user_id,
        idempotency_key=prompt.idempotency_key,
        created_at=prompt.created_at,
        company_id=prompt.company_id,
        is_active=prompt.is_active,
        is_duplicate=False
    )


@router.get("/company_id/{company_id}", response_model=List[PromptResponse])
async def get_prompts_by_company_id(
        company_id: int,
        database: AsyncSession = Depends(get_db)):
    """
    Retrieve a list of prompts belongs to a company ID
    Todo: consider pagination
    """
    stmt = select(BrandPromptTable).where(BrandPromptTable.company_id == company_id)
    result = await database.execute(stmt)

    prompts = result.scalars().all()

    if not prompts:
        raise HTTPException(status_code=404, detail="Prompts not found")

    response_array = []
    for record in prompts:
        response_array.append(PromptResponse(
            id=record.id,
            prompt=record.prompt,
            project_name=record.project_name,
            user_id=record.user_id,
            idempotency_key=record.idempotency_key,
            created_at=record.created_at,
            company_id=record.company_id,
            is_active=record.is_active,
            is_duplicate=False
        ))
    return response_array


@router.post("/alternative_prompts", response_model=AlternativePromptsResponse)
async def create_alternative_prompts(request: ReferencePromptRequest):
    """Process using local Ollama"""
    logger.info(f"Calling local model: {local_model_service.model}")

    # Check if Ollama is running
    is_healthy = await local_model_service.check_health()
    if not is_healthy:
        raise Exception("local model service is not running or not accessible")

    # Use chat endpoint for better results
    content = (system_prompts.alternative_prompts_system_input +
               f"\n Now provide alternative prompts for this reference: {request.origin_prompt}")
    # messages = [{"role": "user", "content": content}]
    result = await local_model_service.generate(prompt=content)

    logger.info(f"Generated alternative prompts: {result}")

    logger.info("Ollama processing completed successfully")

    json_output = json.loads(result)

    return AlternativePromptsResponse(**json_output)
