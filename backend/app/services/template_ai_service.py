import json
import logging
import re
from typing import Any

import httpx

from app.core.config import settings
from app.models import TemplateVariableConfig, TemplateVariableType
from app.template_utils import is_missing_value, render_template_text, value_to_text

logger = logging.getLogger(__name__)

EXTRACT_SYSTEM_PROMPT = """
You are an information extraction engine.
Return strict JSON only.
Rules:
- Use only user input_text and optional profile_context.
- Never fabricate facts.
- If unknown, leave empty and mark as missing.
- list variables must always be arrays.
- Keep variable names exactly as provided in variables_schema.
- Return this JSON shape:
  {
    "values": {"var": "..." or ["..."]},
    "missing_required": ["var"],
    "confidence": {"var": 0.0},
    "notes": {"var": "source sentence or reason"}
  }
""".strip()

RENDER_SYSTEM_PROMPT = """
You are a constrained template renderer.
Return strict JSON only.
Rules:
- Preserve template structure and order.
- Replace placeholders only.
- No new factual claims unless provided in values.
- Minimal polishing only (transitions, grammar fixes, tone consistency).
- Return this JSON shape: {"output_text": "..."}
""".strip()

BULLET_PATTERN = re.compile(r"^\s*[-*]\s+(.+)$", re.MULTILINE)
LABELED_SEPARATOR_PATTERN = r"(?:[:\-]|\uFF1A)"


class GeminiResponseError(RuntimeError):
    pass


def _has_gemini_key() -> bool:
    return bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())


def _strip_json_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def _extract_text_from_gemini_response(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        prompt_feedback = payload.get("promptFeedback")
        raise GeminiResponseError(f"Gemini returned no candidates: {prompt_feedback}")

    parts = candidates[0].get("content", {}).get("parts", [])
    if not isinstance(parts, list):
        raise GeminiResponseError("Gemini candidate content.parts is invalid")

    text_chunks: list[str] = []
    for part in parts:
        if isinstance(part, dict) and isinstance(part.get("text"), str):
            text_chunks.append(part["text"])

    text = "".join(text_chunks).strip()
    if not text:
        finish_reason = candidates[0].get("finishReason")
        raise GeminiResponseError(
            f"Gemini returned empty text response (finishReason={finish_reason})"
        )
    return text


def _gemini_generate_json(*, system_prompt: str, user_payload: dict[str, Any]) -> dict[str, Any]:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise GeminiResponseError("GEMINI_API_KEY is not configured")

    model = settings.GEMINI_MODEL.strip() or "gemini-2.5-flash-lite"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    )

    request_body = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": json.dumps(
                            user_payload,
                            ensure_ascii=False,
                            indent=2,
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }

    try:
        with httpx.Client(timeout=settings.GEMINI_TIMEOUT_SECONDS) as client:
            response = client.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key,
                },
                json=request_body,
            )
    except httpx.HTTPError as exc:
        raise GeminiResponseError(f"Gemini request failed: {exc}") from exc

    if response.status_code >= 400:
        body_preview = response.text[:500]
        raise GeminiResponseError(
            f"Gemini API error {response.status_code}: {body_preview}"
        )

    payload = response.json()
    text = _extract_text_from_gemini_response(payload)
    normalized = _strip_json_code_fences(text)

    try:
        parsed = json.loads(normalized)
    except json.JSONDecodeError as exc:
        raise GeminiResponseError(
            f"Gemini returned invalid JSON: {normalized[:500]}"
        ) from exc

    if not isinstance(parsed, dict):
        raise GeminiResponseError("Gemini JSON response is not an object")
    return parsed


def _variable_aliases(variable: str) -> list[str]:
    normalized = variable.replace("_", " ").strip()
    aliases = [
        variable,
        normalized,
        normalized.lower(),
        normalized.title(),
        normalized.replace(" ", "_"),
    ]
    seen: set[str] = set()
    unique_aliases: list[str] = []
    for alias in aliases:
        if alias and alias not in seen:
            seen.add(alias)
            unique_aliases.append(alias)
    return unique_aliases


def _split_list_values(raw: str) -> list[str]:
    if not raw.strip():
        return []
    bullet_items = [match.group(1).strip() for match in BULLET_PATTERN.finditer(raw)]
    if bullet_items:
        return [item for item in bullet_items if item]

    chunks = re.split(r"[\n,;|]", raw)
    values = [chunk.strip(" -\t") for chunk in chunks if chunk.strip(" -\t")]
    return values


def _extract_labeled_value(
    input_text: str, aliases: list[str]
) -> tuple[str | None, str | None]:
    for alias in aliases:
        pattern = re.compile(
            rf"(?im)^\s*{re.escape(alias)}\s*{LABELED_SEPARATOR_PATTERN}\s*(.+)$"
        )
        match = pattern.search(input_text)
        if match:
            return match.group(1).strip(), f"Matched labeled field '{alias}'"
    return None, None


def _extract_heuristic_value(
    variable: str, input_text: str
) -> tuple[str | None, str | None]:
    lowered = variable.lower()

    if "company" in lowered:
        match = re.search(
            rf"(?i)\b(?:company|at)\s*{LABELED_SEPARATOR_PATTERN}?\s*([A-Z][A-Za-z0-9& .\-]{{1,80}})",
            input_text,
        )
        if match:
            return match.group(1).strip(), "Matched company heuristic"

    if "role" in lowered or "position" in lowered or "job" in lowered:
        match = re.search(
            rf"(?i)\b(?:role|position|job\s*title|title)\s*{LABELED_SEPARATOR_PATTERN}?\s*([A-Za-z0-9& ./\-]{{2,80}})",
            input_text,
        )
        if match:
            return match.group(1).strip(), "Matched role heuristic"

    return None, None


def _value_from_profile_context(
    variable: str, profile_context: dict[str, Any]
) -> tuple[Any | None, str | None]:
    aliases = _variable_aliases(variable)
    for alias in aliases:
        if alias in profile_context:
            return profile_context[alias], f"Pulled from profile_context['{alias}']"
    return None, None


def _coerce_value_for_type(value: Any, variable_type: TemplateVariableType) -> Any:
    if variable_type == TemplateVariableType.list:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if value is None:
            return []
        return _split_list_values(str(value))

    if value is None:
        return ""
    return value_to_text(value)


def _normalize_extract_output(
    *,
    raw: dict[str, Any],
    variables_schema: dict[str, Any],
) -> tuple[dict[str, Any], list[str], dict[str, float], dict[str, str]]:
    raw_values = raw.get("values") if isinstance(raw.get("values"), dict) else {}
    raw_confidence = (
        raw.get("confidence") if isinstance(raw.get("confidence"), dict) else {}
    )
    raw_notes = raw.get("notes") if isinstance(raw.get("notes"), dict) else {}

    values: dict[str, Any] = {}
    missing_required: list[str] = []
    confidence: dict[str, float] = {}
    notes: dict[str, str] = {}

    for variable, raw_config in variables_schema.items():
        config = TemplateVariableConfig.model_validate(raw_config)
        coerced = _coerce_value_for_type(raw_values.get(variable), config.type)
        values[variable] = coerced

        raw_conf_value = raw_confidence.get(variable)
        if isinstance(raw_conf_value, (int, float)):
            confidence[variable] = max(0.0, min(1.0, float(raw_conf_value)))
        else:
            confidence[variable] = 0.0 if is_missing_value(coerced, config.type) else 0.5

        raw_note = raw_notes.get(variable)
        if isinstance(raw_note, str) and raw_note.strip():
            notes[variable] = raw_note.strip()

        if config.required and is_missing_value(coerced, config.type):
            missing_required.append(variable)

    return values, missing_required, confidence, notes


def _extract_variables_with_rules(
    *,
    input_text: str,
    variables_schema: dict[str, Any],
    profile_context: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str], dict[str, float], dict[str, str]]:
    profile = profile_context or {}
    values: dict[str, Any] = {}
    missing_required: list[str] = []
    confidence: dict[str, float] = {}
    notes: dict[str, str] = {}

    for variable, raw_config in variables_schema.items():
        config = TemplateVariableConfig.model_validate(raw_config)

        profile_value, profile_note = _value_from_profile_context(variable, profile)
        if profile_value is not None:
            coerced = _coerce_value_for_type(profile_value, config.type)
            values[variable] = coerced
            confidence[variable] = 0.85
            if profile_note:
                notes[variable] = profile_note
            if config.required and is_missing_value(coerced, config.type):
                missing_required.append(variable)
            continue

        aliases = _variable_aliases(variable)
        labeled_value, label_note = _extract_labeled_value(input_text, aliases)

        if labeled_value is not None:
            coerced = _coerce_value_for_type(labeled_value, config.type)
            values[variable] = coerced
            confidence[variable] = 0.93
            if label_note:
                notes[variable] = label_note
        else:
            heuristic_value, heuristic_note = _extract_heuristic_value(
                variable, input_text
            )
            if heuristic_value is not None:
                coerced = _coerce_value_for_type(heuristic_value, config.type)
                values[variable] = coerced
                confidence[variable] = 0.6
                if heuristic_note:
                    notes[variable] = heuristic_note
            else:
                empty_value = [] if config.type == TemplateVariableType.list else ""
                values[variable] = empty_value

        if config.required and is_missing_value(values[variable], config.type):
            missing_required.append(variable)

    return values, missing_required, confidence, notes


def extract_variables(
    *,
    input_text: str,
    variables_schema: dict[str, Any],
    profile_context: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str], dict[str, float], dict[str, str]]:
    profile = profile_context or {}
    schema_var_count = len(variables_schema)

    if not _has_gemini_key():
        logger.info(
            "AI extract using rules fallback (reason=no_gemini_key, variables=%s)",
            schema_var_count,
        )
        return _extract_variables_with_rules(
            input_text=input_text,
            variables_schema=variables_schema,
            profile_context=profile,
        )

    payload = {
        "task": "extract_variables",
        "input_text": input_text,
        "profile_context": profile,
        "variables_schema": variables_schema,
    }

    try:
        raw = _gemini_generate_json(
            system_prompt=EXTRACT_SYSTEM_PROMPT, user_payload=payload
        )
        normalized = _normalize_extract_output(raw=raw, variables_schema=variables_schema)
        logger.info(
            "AI extract provider=gemini model=%s variables=%s missing_required=%s",
            settings.GEMINI_MODEL,
            schema_var_count,
            len(normalized[1]),
        )
        return normalized
    except GeminiResponseError as exc:
        logger.warning("AI extract Gemini failed, falling back to rules: %s", exc)
        return _extract_variables_with_rules(
            input_text=input_text,
            variables_schema=variables_schema,
            profile_context=profile,
        )


def _render_with_gemini(
    *,
    content: str,
    values: dict[str, Any],
    style: dict[str, Any] | None = None,
) -> str:
    payload = {
        "task": "render_template",
        "template_content": content,
        "values": values,
        "style": style or {},
    }
    raw = _gemini_generate_json(system_prompt=RENDER_SYSTEM_PROMPT, user_payload=payload)
    output_text = raw.get("output_text")
    if not isinstance(output_text, str) or not output_text.strip():
        raise GeminiResponseError("Gemini render response missing output_text")
    return output_text.strip()


def render_template(
    *, content: str, values: dict[str, Any], style: dict[str, Any] | None = None
) -> str:
    if not _has_gemini_key():
        logger.info("AI render using rules fallback (reason=no_gemini_key)")
        return render_template_text(content, values)

    try:
        output = _render_with_gemini(content=content, values=values, style=style)
        logger.info(
            "AI render provider=gemini model=%s output_chars=%s",
            settings.GEMINI_MODEL,
            len(output),
        )
        return output
    except GeminiResponseError as exc:
        logger.warning(
            "AI render Gemini failed, falling back to local renderer: %s",
            exc,
        )
        # Keep the feature functional even if Gemini is unavailable.
        return render_template_text(content, values)
