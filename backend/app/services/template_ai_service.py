import re
from typing import Any

from app.models import TemplateVariableConfig, TemplateVariableType
from app.template_utils import is_missing_value, render_template_text, value_to_text

EXTRACT_SYSTEM_PROMPT = """
You are an information extraction engine.
Return strict JSON only.
Rules:
- Use only user input_text and optional profile_context.
- Never fabricate facts.
- If unknown, leave empty and mark as missing.
- list variables must always be arrays.
""".strip()

RENDER_SYSTEM_PROMPT = """
You are a constrained template renderer.
Rules:
- Preserve template structure and order.
- Replace placeholders only.
- No new factual claims unless provided in values.
""".strip()

BULLET_PATTERN = re.compile(r"^\s*[-*]\s+(.+)$", re.MULTILINE)


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
        pattern = re.compile(rf"(?im)^\s*{re.escape(alias)}\s*[:：\-]\s*(.+)$")
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
            r"(?i)\b(?:company|at)\s*[:：\-]?\s*([A-Z][A-Za-z0-9& .\-]{1,80})",
            input_text,
        )
        if match:
            return match.group(1).strip(), "Matched company heuristic"

    if "role" in lowered or "position" in lowered or "job" in lowered:
        match = re.search(
            r"(?i)\b(?:role|position|job\s*title|title)\s*[:：\-]?\s*([A-Za-z0-9& ./\-]{2,80})",
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


def extract_variables(
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


def render_template(
    *, content: str, values: dict[str, Any], style: dict[str, Any] | None = None
) -> str:
    # MVP renderer intentionally stays deterministic and constrained.
    _ = style
    return render_template_text(content, values)
