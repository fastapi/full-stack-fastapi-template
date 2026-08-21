import logging
import time
from dataclasses import dataclass
from typing import Any, Literal
from uuid import UUID

from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from pydantic import ValidationError
from sqlalchemy import select
from sqlmodel import Session

from app.core.ai.embeddings import embed_text
from app.core.ai.prompts import PromptId, get_prompt
from app.core.ai.retrieval import retrieve_top_k_chunks
from app.core.config import settings
from app.models import (
    Difficulty,
    Document,
    ExplanationOutput,
    QuestionCreate,
    QuestionItem,
    QuestionOutput,
    QuestionType,
)

# Initialize logging
logger = logging.getLogger(__name__)

# Maximum characters for extracted text when generating exam questions
MAX_CHARS = 15_000
DEFAULT_MAX_COMPLETION_TOKENS = 500
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.5

llm = ChatOpenAI(
    model=DEFAULT_MODEL,
    temperature=DEFAULT_TEMPERATURE,
    max_completion_tokens=DEFAULT_MAX_COMPLETION_TOKENS,
    api_key=settings.OPENAI_API_KEY,  # type: ignore
)

ErrorKind = Literal["validation", "parse", "provider"]


@dataclass
class GenerationResult:
    prompt_id: str
    ok: bool
    error: str | None
    error_kind: ErrorKind | None
    latency_ms: float
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    schema_valid: bool
    final_contract_valid: bool
    content_checks: dict[str, Any]
    questions: list[QuestionCreate]


def normalize_question_types(
    question_types: list[QuestionType] | None,
) -> list[QuestionType]:
    if question_types is None:
        return [QuestionType.multiple_choice, QuestionType.true_false]
    return question_types


def normalize_difficulty(difficulty: Difficulty | None) -> Difficulty:
    if difficulty is None:
        return Difficulty.medium
    return difficulty


def resolve_question_type_counts(
    num_questions: int,
    *,
    question_types: list[QuestionType] | None = None,
    question_type_counts: dict[QuestionType, int] | None = None,
) -> dict[QuestionType, int]:
    """Resolve an explicit MC/TF mix.

    Defaults for mixed types at num_questions=5: 3 multiple_choice + 2 true_false.
    """
    if question_type_counts is not None:
        total = sum(question_type_counts.values())
        if total != num_questions:
            raise ValueError(
                f"question_type_counts sum ({total}) must equal "
                f"num_questions ({num_questions})"
            )
        return dict(question_type_counts)

    types = normalize_question_types(question_types)
    if len(types) == 1:
        return {types[0]: num_questions}

    if num_questions == 5:
        return {
            QuestionType.multiple_choice: 3,
            QuestionType.true_false: 2,
        }

    mc = (num_questions * 3) // 5
    tf = num_questions - mc
    if num_questions >= 2 and tf == 0:
        tf = 1
        mc = num_questions - 1
    if num_questions >= 2 and mc == 0:
        mc = 1
        tf = num_questions - 1
    return {
        QuestionType.multiple_choice: mc,
        QuestionType.true_false: tf,
    }


def generate_questions_prompt(
    text: str,
    num_questions: int = 5,
    difficulty: Difficulty | None = None,
    question_types: list[QuestionType] | None = None,
) -> str:
    """Backward-compatible wrapper around baseline prompt A."""
    counts = resolve_question_type_counts(num_questions, question_types=question_types)
    return get_prompt(
        "a",
        text,
        num_questions=num_questions,
        difficulty=normalize_difficulty(difficulty),
        question_type_counts=counts,
    )


def fetch_document_texts(session: Session, document_ids: list[UUID]) -> list[str]:
    """Fetch extracted texts for given document IDs."""
    try:
        stmt = select(Document.extracted_text).where(Document.id.in_(document_ids))  # type: ignore[attr-defined, call-overload]
        results = session.exec(stmt).all()
        texts = [text for (text,) in results if text]
        if not texts:
            raise ValueError(f"No extracted texts found for documents: {document_ids}")
        return texts
    except Exception as e:
        logger.error(f"Failed to fetch document texts for {document_ids}: {e}")
        raise


def validate_and_convert_question_item(q: Any) -> QuestionCreate | None:
    """Validate LLM question item and convert to QuestionCreate.

    Re-validates via QuestionItem so answer ∈ options is enforced even when
    callers pass a duck-typed object (not only structured-output parsing).
    """
    try:
        if isinstance(q, QuestionItem):
            item = q
        else:
            item = QuestionItem(
                question=q.question,
                answer=q.answer,
                type=q.type,
                options=list(q.options) if q.options is not None else [],
            )
        return QuestionCreate(
            question=item.question,
            correct_answer=item.answer,
            type=QuestionType(item.type),
            options=item.options,
        )
    except ValidationError as ve:
        logger.error(f"Validation error for question item {q}: {ve}")
        raise


def parse_llm_output(llm_output: Any) -> list[QuestionCreate]:
    """Parse LLM structured output into QuestionCreate list."""
    questions: list[QuestionCreate] = []
    for q in llm_output.questions:
        qc = validate_and_convert_question_item(q)
        if qc:
            questions.append(qc)

    return questions


def _empty_content_checks(expected_count: int) -> dict[str, Any]:
    return {
        "expected_count": expected_count,
        "actual_count": 0,
        "answer_in_options_rate": 0.0,
        "mc_count": 0,
        "tf_count": 0,
    }


def _compute_content_checks(
    questions: list[QuestionCreate],
    expected_count: int,
) -> dict[str, Any]:
    mc_count = sum(1 for q in questions if q.type == QuestionType.multiple_choice)
    tf_count = sum(1 for q in questions if q.type == QuestionType.true_false)
    if not questions:
        answer_in_options_rate = 0.0
    else:
        in_options = sum(
            1
            for q in questions
            if q.correct_answer is not None and q.correct_answer in q.options
        )
        answer_in_options_rate = in_options / len(questions)

    return {
        "expected_count": expected_count,
        "actual_count": len(questions),
        "answer_in_options_rate": answer_in_options_rate,
        "mc_count": mc_count,
        "tf_count": tf_count,
    }


def _final_contract_valid(content_checks: dict[str, Any]) -> bool:
    actual_count = int(content_checks["actual_count"])
    expected_count = int(content_checks["expected_count"])
    answer_in_options_rate = float(content_checks["answer_in_options_rate"])
    return actual_count == expected_count and answer_in_options_rate == 1.0


def _extract_token_usage(raw_message: Any) -> tuple[int | None, int | None, int | None]:
    usage = getattr(raw_message, "usage_metadata", None) or {}
    if usage:
        prompt_tokens = usage.get("input_tokens")
        completion_tokens = usage.get("output_tokens")
        total_tokens = usage.get("total_tokens")
        if (
            total_tokens is None
            and prompt_tokens is not None
            and completion_tokens is not None
        ):
            total_tokens = prompt_tokens + completion_tokens
        return prompt_tokens, completion_tokens, total_tokens

    metadata = getattr(raw_message, "response_metadata", None) or {}
    token_usage = metadata.get("token_usage") or metadata.get("usage") or {}
    prompt_tokens = token_usage.get("prompt_tokens")
    completion_tokens = token_usage.get("completion_tokens")
    total_tokens = token_usage.get("total_tokens")
    return prompt_tokens, completion_tokens, total_tokens


def _truncate_text(text: str) -> str:
    if len(text) <= MAX_CHARS:
        return text
    logger.warning(
        f"Truncated extracted text from {len(text)} to {MAX_CHARS} characters"
    )
    return text[:MAX_CHARS]


def _question_llm(max_completion_tokens: int) -> Any:
    chat = ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=DEFAULT_TEMPERATURE,
        max_completion_tokens=max_completion_tokens,
        api_key=settings.OPENAI_API_KEY,  # type: ignore
    )
    return chat.with_structured_output(QuestionOutput, include_raw=True)


async def generate_questions(
    text: str,
    *,
    prompt_id: PromptId = "a",
    num_questions: int = 5,
    difficulty: Difficulty | None = None,
    question_type_counts: dict[QuestionType, int] | None = None,
    max_completion_tokens: int | None = None,
) -> GenerationResult:
    """Shared question generation core used by the API and (later) eval.

    Does not raise HTTPException — callers decide how to surface failures.
    """
    resolved_difficulty = normalize_difficulty(difficulty)
    resolved_counts = resolve_question_type_counts(
        num_questions, question_type_counts=question_type_counts
    )
    token_limit = (
        DEFAULT_MAX_COMPLETION_TOKENS
        if max_completion_tokens is None
        else max_completion_tokens
    )
    truncated = _truncate_text(text)
    prompt = get_prompt(
        prompt_id,
        truncated,
        num_questions=num_questions,
        difficulty=resolved_difficulty,
        question_type_counts=resolved_counts,
    )

    started = time.perf_counter()
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    try:
        raw_result = await _question_llm(token_limit).ainvoke(prompt)
        latency_ms = (time.perf_counter() - started) * 1000

        if isinstance(raw_result, dict):
            parsed = raw_result.get("parsed")
            raw_message = raw_result.get("raw")
            parsing_error = raw_result.get("parsing_error")
            if raw_message is not None:
                prompt_tokens, completion_tokens, total_tokens = _extract_token_usage(
                    raw_message
                )
            if parsing_error is not None or parsed is None:
                # parsing_error / raw bodies can contain model output; keep that out of
                # GenerationResult.error (and thus API responses).
                exc_type = (
                    type(parsing_error).__name__
                    if parsing_error is not None
                    else "MissingParsedOutput"
                )
                logger.error(
                    "Question generation parse failed (prompt_id=%s, exc_type=%s)",
                    prompt_id,
                    exc_type,
                )
                return GenerationResult(
                    prompt_id=prompt_id,
                    ok=False,
                    error="Failed to parse LLM output",
                    error_kind="parse",
                    latency_ms=latency_ms,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    schema_valid=False,
                    final_contract_valid=False,
                    content_checks=_empty_content_checks(num_questions),
                    questions=[],
                )
            llm_output = parsed
        else:
            llm_output = raw_result

        questions = parse_llm_output(llm_output)
        content_checks = _compute_content_checks(questions, num_questions)
        return GenerationResult(
            prompt_id=prompt_id,
            ok=True,
            error=None,
            error_kind=None,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            schema_valid=True,
            final_contract_valid=_final_contract_valid(content_checks),
            content_checks=content_checks,
            questions=questions,
        )
    except ValidationError as ve:
        latency_ms = (time.perf_counter() - started) * 1000
        # ValidationError.input can include model output; do not forward str(ve).
        logger.error(
            "Question generation validation failed (prompt_id=%s, exc_type=%s)",
            prompt_id,
            type(ve).__name__,
        )
        return GenerationResult(
            prompt_id=prompt_id,
            ok=False,
            error="LLM validation error",
            error_kind="validation",
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            schema_valid=False,
            final_contract_valid=False,
            content_checks=_empty_content_checks(num_questions),
            questions=[],
        )
    except Exception as e:
        latency_ms = (time.perf_counter() - started) * 1000
        # Provider errors may embed response snippets; log type only, not str(e).
        logger.error(
            "Question generation LLM call failed (prompt_id=%s, exc_type=%s)",
            prompt_id,
            type(e).__name__,
        )
        return GenerationResult(
            prompt_id=prompt_id,
            ok=False,
            error="Failed to generate questions",
            error_kind="provider",
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            schema_valid=False,
            final_contract_valid=False,
            content_checks=_empty_content_checks(num_questions),
            questions=[],
        )


async def generate_questions_from_documents(
    session: Session,
    document_ids: list[UUID],
    num_questions: int = 5,
    difficulty: Difficulty | None = None,
    question_types: list[QuestionType] | None = None,
) -> list[QuestionCreate]:
    """API-facing wrapper: fetch documents, generate questions, raise HTTP errors."""
    document_texts = fetch_document_texts(session, document_ids)
    if not document_texts:
        return []

    combined_text = "\n".join(document_texts)
    counts = resolve_question_type_counts(num_questions, question_types=question_types)
    result = await generate_questions(
        combined_text,
        prompt_id="a",
        num_questions=num_questions,
        difficulty=difficulty,
        question_type_counts=counts,
    )
    if not result.ok:
        if result.error_kind == "validation":
            detail = "LLM validation error"
        elif result.error_kind == "parse":
            detail = "Failed to parse LLM output"
        else:
            detail = "Failed to generate questions"
        raise HTTPException(status_code=500, detail=detail)
    return result.questions


# ------------------------
# Explanation LLM
# ------------------------

structured_explanation_llm = llm.with_structured_output(ExplanationOutput)


def generate_explanation_prompt(
    *,
    question: str,
    correct_answer: str,
    user_answer: str,
    context_chunks: list[str],
) -> str:
    context = "\n\n".join(context_chunks)

    return f"""
You are a friendly but academic tutor helping a student learn from a mistake.

Rules (must follow):
- Use ONLY the study material below
- Do NOT restate the material verbatim
- Do NOT say \"the material says\" or similar phrases
- Be brief (1–4 sentences total)
- Maintain an academic tone while being approachable and supportive
- Use precise, scholarly language appropriate for educational content
- Be encouraging but maintain intellectual rigor

Task:
Explain why the student's answer is incorrect and what they should remember next time.

Question:
{question}

Correct answer:
{correct_answer}

Student answer:
{user_answer}

Study material:
{context}


Explain clearly using ONLY the material above.
Avoid introducing new facts.
"""


def normalize_uuid_list(values: list[str | UUID]) -> list[UUID]:
    return [v if isinstance(v, UUID) else UUID(v) for v in values]


async def generate_answer_explanation(
    *,
    session: Session,
    exam: Any,  # ideally Exam
    question: str,
    correct_answer: str,
    user_answer: str,
) -> ExplanationOutput:
    if not correct_answer:
        raise ValueError("Cannot generate explanation without a correct answer")

    source_doc_ids = normalize_uuid_list(exam.source_document_ids)

    query_text = (
        f"Question: {question}\n"
        f"Correct answer: {correct_answer}\n"
        f"Student answer: {user_answer}"
    )

    query_embedding = embed_text(query_text)

    context_chunks = retrieve_top_k_chunks(
        session=session,
        document_ids=source_doc_ids,
        query_embedding=query_embedding,
        k=4,
    )

    prompt = generate_explanation_prompt(
        question=question,
        correct_answer=correct_answer,
        user_answer=user_answer,
        context_chunks=context_chunks,
    )

    try:
        raw = await structured_explanation_llm.ainvoke(prompt)
        return ExplanationOutput.model_validate(raw)
    except Exception as e:
        logger.error(f"Failed to generate explanation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate answer explanation",
        )
