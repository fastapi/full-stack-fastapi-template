from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.core.model_service import ModelServiceUnavailable
from app.models_ml.labse import AlignmentInput, AlignmentInputSingle, AlignmentResponse, AlignmentOutput, align_sentences, align_sentences_uni, align_sentences_special, generate_tmx
import logging

router = APIRouter()


def _labse_unavailable(e: ModelServiceUnavailable) -> HTTPException:
    """The embedding service is down or still loading — retryable, not a 500."""
    logging.warning("labse-svc unavailable during alignment: %s", e)
    return HTTPException(status_code=503, detail=str(e), headers={"Retry-After": "10"})


@router.post("/align", response_model=AlignmentResponse)
async def align(request: AlignmentInput) -> AlignmentResponse:
    try:
        return await align_sentences(request)
    except ModelServiceUnavailable as e:
        raise _labse_unavailable(e)
    except Exception as e:
        logging.error("Error in alignment procedure: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during LaBSE alignment procedure."
        )

@router.post("/align-uni")
async def align_texts(request: AlignmentInputSingle):
    try:
        return await align_sentences_uni(request)
    except ModelServiceUnavailable as e:
        raise _labse_unavailable(e)
    except Exception as e:
        logging.error("Error in alignment procedure: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during LaBSE alignment procedure."
        )


@router.post("/generate_tmx", response_class=Response)
async def create_tmx(data: list[AlignmentOutput]):
    if not data:
        raise HTTPException(status_code=400, detail="Input data cannot be empty.")
    
    tmx_content = generate_tmx(data)
    return Response(content=tmx_content, media_type="application/xml")



@router.post("/align-uni-special", response_model=AlignmentResponse)
async def align_ai(request: AlignmentInputSingle):
    try:
        return await align_sentences_special(request)
    except Exception as e:
        logging.error("Error in alignment procedure: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during LaBSE alignment procedure."
        )



# To run the app, use the command:
# uvicorn script_name:app --reload