from fastapi import APIRouter, HTTPException
from app.core.model_service import ModelServiceUnavailable
from app.models_ml.comet import calculate_comet, CometRequestInputList, CometRequestInputDict, CometRequestResponse
from app.models_ml.quality_estimation import calculate_quality_estimation, QERequestInput, QERequestResponse
from app.models_ml.labse import calculate_labse, LaBSERequestInput, LaBSERequestResponse
from app.models_ml.sacre_bleu import calculate_bleu, calculate_ter, calculate_chrf, calculate_hlepor, calculate_character, RequestInput, RequestResponse
from app.models_ml.metricx import calculate_metricx, MetricXRequestInputList, MetricXRequestInputDict, MetricXRequestResponse
from typing import Union

router = APIRouter()


def _unavailable(e: ModelServiceUnavailable) -> HTTPException:
    """A model container is down or still loading — retryable, not a 500.

    503 + Retry-After is what lets a batch worker back off and try the chunk
    again rather than recording a permanent failure.
    """
    return HTTPException(status_code=503, detail=str(e), headers={"Retry-After": "10"})


@router.post("/comet", response_model=CometRequestResponse)
async def comet(data: Union[list[CometRequestInputList], CometRequestInputDict]) -> CometRequestResponse:
    """API endpoint for the COMET score calculation."""
    try:
        return await calculate_comet(data)
    except ModelServiceUnavailable as e:
        raise _unavailable(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during quality estimation: {str(e)}")


@router.post("/quality-estimation", response_model=QERequestResponse)
async def quality_estimation(data: list[QERequestInput]) -> QERequestResponse:
    """API endpoint for the quality estimation score calculation."""
    try:
        return await calculate_quality_estimation(data)
    except ModelServiceUnavailable as e:
        raise _unavailable(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during quality estimation: {str(e)}")


@router.post("/labse", response_model=LaBSERequestResponse)
async def labse(data: list[LaBSERequestInput]) -> LaBSERequestResponse:
    """API endpoint for labse (accuracy) score calculation."""
    try:
        return await calculate_labse(data)
    except ModelServiceUnavailable as e:
        raise _unavailable(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during similarity calculation: {str(e)}")


@router.post("/sacre-bleu", response_model=RequestResponse)
async def sacre_bleu(data: list[RequestInput]) -> RequestResponse:
    """API endpoint for sacre blue score calculation."""
    try:
        return await calculate_bleu(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during corpus BLEU score calculation: {str(e)}")


@router.post("/ter", response_model=RequestResponse)
async def ter(data: list[RequestInput]) -> RequestResponse:
    """API endpoint for ter score calculation."""
    try:
        return await calculate_ter(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during TER calculation: {str(e)}")


@router.post("/characTER", response_model=RequestResponse)
async def characTER(data: list[RequestInput]) -> RequestResponse:
    """API endpoint for characTER score calculation."""
    try:
        return await calculate_character(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during characTER calculation: {str(e)}")


@router.post("/chrf", response_model=RequestResponse)
async def chrf(data: list[RequestInput]) -> RequestResponse:
    """API endpoint for chrf score calculation."""
    try:
        return await calculate_chrf(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during CHRF calculation: {str(e)}")


@router.post("/hlepor", response_model=RequestResponse)
async def hlepor(data: list[RequestInput]) -> RequestResponse:
    """API endpoint for hlepor score calculation."""
    try:
        return await calculate_hlepor(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during HLepor calculation: {str(e)}")


@router.post("/metricx", response_model=MetricXRequestResponse)
async def metricx(data: Union[list[MetricXRequestInputList], MetricXRequestInputDict]) -> MetricXRequestResponse:
    """API endpoint for the MetricX score calculation."""
    try:
        return await calculate_metricx(data)
    except ModelServiceUnavailable as e:
        raise _unavailable(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during MetricX score calculation: {str(e)}")



