from app.core import metricx_client
from pydantic import BaseModel, ValidationError
from typing import Union, Optional

# Define request and response models
class MetricXRequestInputList(BaseModel):
    src: Optional[str] = ""  # Source text, optional, defaults to empty string
    mt: str   # Machine translation
    ref: Optional[str] = None   # Reference text

class MetricXRequestInputDict(BaseModel):
    src: Optional[list[str]] = None
    mt: list[str]
    ref: Optional[list[str]] = None
    
    def validate_lengths(self):
        # If src is provided, check length
        if self.src:
            if len(self.src) != len(self.mt):
                raise ValueError("Lists src and mt must have the same length.")
        
        # If ref is provided, check length
        if self.ref:
            if len(self.ref) != len(self.mt):
                raise ValueError("Lists ref and mt must have the same length.")

class MetricXRequestOutput(BaseModel):
    src: str
    mt: str
    ref: Optional[str] = None
    score: float  # Single quality score

class MetricXRequestResponse(BaseModel):
    system_score: float  # Overall average score
    estimates: list[MetricXRequestOutput]

async def calculate_metricx(data: Union[list[MetricXRequestInputList], MetricXRequestInputDict]) -> MetricXRequestResponse:
    # Determine the input format
    formatted_data = []
    if isinstance(data, list):  # Schema 1
        formatted_data = [{"src": item.src if item.src is not None else "", "mt": item.mt, "ref": item.ref} for item in data]
    elif isinstance(data, (dict, BaseModel)):
        try:
            if isinstance(data, BaseModel):
                validated_data = data
            else:
                validated_data = MetricXRequestInputDict(**data)
            
            validated_data.validate_lengths()
            
            # Prepare lists
            mt_list = validated_data.mt
            count = len(mt_list)
            
            src_list = validated_data.src if validated_data.src else [""] * count
            ref_list = validated_data.ref if validated_data.ref else [None] * count
            
            formatted_data = [
                {"src": s, "mt": m, "ref": r} 
                for s, m, r in zip(src_list, mt_list, ref_list)
            ]
        except ValidationError as e:
            raise ValueError(f"Invalid input format for Schema 2: {e}") from e
        except ValueError as ve:
            raise ValueError(f"Schema 2 validation error: {ve}") from ve
        except Exception as ex:
            raise ValueError(f"Unexpected error processing Schema 2: {ex}") from ex
    else:
        raise ValueError("Invalid input format. Expected list of objects or dictionary of lists.")

    # Scored by metricx-svc. Prompt construction, tokenization, EOS trimming and
    # the length-sorted mini-batching that used to live here now live in that
    # service, which owns the tokenizer alongside the weights.
    scores, mean_score = await metricx_client.score(formatted_data)

    estimates = []
    for i, item in enumerate(formatted_data):
        score = float(scores[i])
        estimates.append(MetricXRequestOutput(
            src=item['src'],
            mt=item['mt'],
            ref=item['ref'],
            score=score
        ))
        
    # The client already averages across chunks and returns 0.0 for an empty
    # batch, which np.mean did not — it produced a NaN that is not valid JSON.
    system_score = mean_score
    
    return MetricXRequestResponse(system_score=system_score, estimates=estimates)
