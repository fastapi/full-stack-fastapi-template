from app.core import comet_client
from pydantic import BaseModel, ValidationError
from typing import Union

# Define request and response models
class CometRequestInputList(BaseModel):
    src: str  # Source text
    mt: str   # Machine translation
    ref: str   # Reference text

class CometRequestInputDict(BaseModel):
    src: list[str]
    mt: list[str]
    ref: list[str]
    def validate_lengths(self):
        if not (len(self.src) == len(self.mt) == len(self.ref)):
            raise ValueError("All lists (src, mt, ref) must have the same length.")

class CometRequestOutput(BaseModel):
    src: str
    mt: str
    ref: str
    score: float  # Single quality score

class CometRequestResponse(BaseModel):
    system_score: float  # Overall average score
    estimates: list[CometRequestOutput]

async def calculate_comet(data: Union[list[CometRequestInputList], dict]) -> CometRequestResponse:

    # Determine the input format
    if isinstance(data, list):  # Schema 1
        formatted_data = [{"src": item.src, "mt": item.mt, "ref": item.ref} for item in data]
    elif isinstance(data, (dict, BaseModel)):
        try:
            data = dict(data)  # Ensure it's a true dictionary
            validated_data = CometRequestInputDict(**data)
            validated_data.validate_lengths()  # Ensure all lists have the same length
            formatted_data = [
                {"src": s, "mt": m, "ref": r} 
                for s, m, r in zip(validated_data.src, validated_data.mt, validated_data.ref)
            ]
        except ValidationError as e:
            raise ValueError(f"Invalid input format for Schema 2: {e}") from e
        except ValueError as ve:
            raise ValueError(f"Schema 2 validation error: {ve}") from ve
        except Exception as ex:
            raise ValueError(f"Unexpected error processing Schema 2: {ex}") from ex
    else:
        raise ValueError(f"Unsupported input format: {type(data)}")

    # Scored by comet-svc. The direct prepare_sample/forward fast path that used
    # to live here now lives in that service.
    scores, system_score = await comet_client.score(formatted_data)

    # Prepare the output
    results = []

    for item, score in zip(formatted_data, scores):
        result = CometRequestOutput(
            src=item['src'],
            mt=item['mt'],
            ref=item['ref'],
            score=float(score)  # Convert score to float if necessary
        )
        results.append(result)

    return CometRequestResponse(system_score=system_score, estimates=results)
