import re
from typing import Any

from app.models import TemplateVariableConfig, TemplateVariableType

PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


def extract_template_variables(content: str) -> list[str]:
    """Extract unique variables from template content while preserving order."""
    seen: set[str] = set()
    variables: list[str] = []
    for match in PLACEHOLDER_PATTERN.finditer(content):
        variable = match.group(1)
        if variable not in seen:
            seen.add(variable)
            variables.append(variable)
    return variables


def _normalize_variable_config(raw: Any) -> TemplateVariableConfig:
    if isinstance(raw, TemplateVariableConfig):
        config = raw
    elif isinstance(raw, dict):
        try:
            config = TemplateVariableConfig.model_validate(raw)
        except Exception:
            config = TemplateVariableConfig()
    else:
        config = TemplateVariableConfig()

    if config.type == TemplateVariableType.list and config.default is None:
        config.default = []
    if config.type == TemplateVariableType.text and config.default is None:
        config.default = ""
    return config


def normalize_variables_schema(
    content: str, raw_schema: dict[str, Any] | None
) -> dict[str, dict[str, Any]]:
    variables = extract_template_variables(content)
    schema_source = raw_schema or {}
    normalized: dict[str, dict[str, Any]] = {}

    for variable in variables:
        normalized[variable] = _normalize_variable_config(
            schema_source.get(variable)
        ).model_dump()

    return normalized


def is_missing_value(value: Any, variable_type: TemplateVariableType) -> bool:
    if variable_type == TemplateVariableType.list:
        if not isinstance(value, list):
            return True
        return len([item for item in value if str(item).strip()]) == 0
    if value is None:
        return True
    return str(value).strip() == ""


def value_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        return ", ".join(cleaned)
    return str(value).strip()


def render_template_text(content: str, values: dict[str, Any]) -> str:
    def _replacement(match: re.Match[str]) -> str:
        variable = match.group(1)
        value = values.get(variable)
        return value_to_text(value)

    rendered = PLACEHOLDER_PATTERN.sub(_replacement, content)
    rendered = re.sub(r"\n{3,}", "\n\n", rendered)
    return rendered.strip()
