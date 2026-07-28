from fastapi import APIRouter, HTTPException
from app.models_ml.language_detect import LanguageDetectionResponse, identify_language, identify_languages
import logging

router = APIRouter()

@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(sentence: str) -> LanguageDetectionResponse:
    try:
        return await identify_language(sentence)
    except Exception as e:
        logging.error("Error in language detection: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while detecting language."
        )
        
@router.post("/detect-language-batch", response_model=list[LanguageDetectionResponse])
async def detect_language_batch(sentences: list[str]) -> list[LanguageDetectionResponse]:
    try:
        return await identify_languages(sentences)
    except Exception as e:
        logging.error("Error in batch language detection: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while detecting languages."
        )