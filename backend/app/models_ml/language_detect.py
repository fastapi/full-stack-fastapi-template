from app.core import langid_client
from pydantic import BaseModel
from typing import Optional

class LanguageDetectionResponse(BaseModel):
    source: str
    language: Optional[str]
    score: float

async def identify_language(sentence: str) -> LanguageDetectionResponse:

    results = await identify_languages([sentence])
    return results[0]


async def identify_languages(sentences: list[str]) -> list[LanguageDetectionResponse]:

    # Detected by langid-svc. Text is passed through unchanged: the previous
    # fastText path lowercased first, but capitalisation is a signal lingua
    # uses, so lowercasing would throw accuracy away.
    detections = await langid_client.detect(sentences)

    results = []

    for sentence, (detected_language, confidence) in zip(sentences, detections):

        # The service is configured for en+fr only, so this is already true of
        # anything it returns. Kept so the contract still holds if LANGUAGES is
        # ever widened on the service side.
        if detected_language not in ["en", "fr"]:
            detected_language = None
            confidence = float(0)

        results.append(LanguageDetectionResponse(
            source=sentence,
            language=detected_language,
            score=confidence
        ))

    return results
