from app.core import qe_client
from pydantic import BaseModel

# Define request and response models
class QERequestInput(BaseModel):
    src: str  # Source text
    mt: str   # Machine translation

class QERequestOutput(BaseModel):
    src: str
    mt: str
    score: float  # Single quality score

class QERequestResponse(BaseModel):
    system_score: float  # Overall average score
    estimates: list[QERequestOutput]


async def calculate_quality_estimation(data: list[QERequestInput]) -> QERequestResponse:

    # Convert input data to the format expected by the model
    formatted_data = [{"src": item.src, "mt": item.mt } for item in data]

    # Scored by qe-svc. The direct prepare_sample/forward fast path that used to
    # live here now lives in that service.
    scores, system_score = await qe_client.score(formatted_data)

    # Prepare the output
    results = []

    for item, score in zip(formatted_data, scores):
        result = QERequestOutput(
            src=item['src'],
            mt=item['mt'],
            score=float(score)  # Convert score to float if necessary
        )
        results.append(result)

    return QERequestResponse(system_score=system_score, estimates=results)
