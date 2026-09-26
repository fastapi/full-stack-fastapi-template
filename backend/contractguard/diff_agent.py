"""
Diff Agent — Mahi's core deliverable.

Usage:
    python diff_agent.py <old_openapi.json> <new_openapi.json> <output_diff_report.json>
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_spec(path: str) -> dict:
    return json.loads(Path(path).read_text())


def _resolve_ref(obj: dict) -> str | None:
    if not isinstance(obj, dict):
        return None
    if "$ref" in obj:
        return obj["$ref"].split("/")[-1]
    if "items" in obj and isinstance(obj["items"], dict) and "$ref" in obj["items"]:
        return obj["items"]["$ref"].split("/")[-1]
    return None


def _extract_type(field_def: dict) -> str:
    if not isinstance(field_def, dict):
        return "unknown"
    if "type" in field_def:
        t = field_def["type"]
        if isinstance(t, list):
            types = [x for x in t if x != "null"]
            return types[0] if types else "null"
        return str(t)
    if "anyOf" in field_def or "oneOf" in field_def:
        variants = field_def.get("anyOf") or field_def.get("oneOf") or []
        for v in variants:
            if isinstance(v, dict):
                if "$ref" in v:
                    return v["$ref"].split("/")[-1]
                if "type" in v:
                    return str(v["type"])
    if "$ref" in field_def:
        return field_def["$ref"].split("/")[-1]
    return "unknown"


def _extract_fields_from_schema(schema: dict, components: dict) -> dict[str, str]:
    fields = {}
    if not isinstance(schema, dict):
        return fields

    ref_name = _resolve_ref(schema)
    if ref_name and ref_name in components:
        schema = components[ref_name]

    # Unwrap allOf / anyOf wrappers
    if "allOf" in schema:
        for sub in schema["allOf"]:
            fields.update(_extract_fields_from_schema(sub, components))

    props = schema.get("properties", {})
    if isinstance(props, dict):
        for fname, fdef in props.items():
            fields[fname] = _extract_type(fdef)

    return fields


def get_endpoint_schemas(spec: dict) -> dict:
    result = {}
    paths = spec.get("paths", {})
    components = spec.get("components", {}).get("schemas", {})

    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, details in methods.items():
            m = method.upper()
            if m not in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                continue

            key = f"{m} {path}"
            fields = {}

            # 1. Extract from Request Body (POST, PUT, PATCH)
            req_body = details.get("requestBody", {})
            if isinstance(req_body, dict):
                content = req_body.get("content", {}).get("application/json", {})
                req_schema = content.get("schema", {})
                fields.update(_extract_fields_from_schema(req_schema, components))

            # 2. Extract from Responses (200, 201, 204, or default)
            responses = details.get("responses", {})
            if isinstance(responses, dict):
                res_obj = (
                    responses.get("200")
                    or responses.get("201")
                    or responses.get("204")
                    or responses.get("200 OK")
                    or {}
                )
                if isinstance(res_obj, dict):
                    content = res_obj.get("content", {}).get("application/json", {})
                    res_schema = content.get("schema", {})
                    fields.update(_extract_fields_from_schema(res_schema, components))

            # Fallback if no explicit fields resolved
            if not fields:
                fields["$response"] = "void" if m == "DELETE" else "unknown"

            result[key] = fields

    return result


def diff_specs(old_spec: dict, new_spec: dict) -> list[dict]:
    old_endpoints = get_endpoint_schemas(old_spec)
    new_endpoints = get_endpoint_schemas(new_spec)
    changes: list[dict] = []
    now = datetime.now(timezone.utc).isoformat()

    def base_entry(key: str, change_type: str, breaking: bool, old_frag: dict, new_frag: dict, severity: str) -> dict:
        method, endpoint = key.split(" ", 1)
        return {
            "endpoint": endpoint,
            "method": method,
            "change_type": change_type,
            "breaking": breaking,
            "old_schema_fragment": old_frag,
            "new_schema_fragment": new_frag,
            "severity": severity,
            "detected_at": now,
        }

    for key, old_fields in old_endpoints.items():
        if key not in new_endpoints:
            changes.append(base_entry(key, "endpoint_removed", True, old_fields, {}, "high"))
            continue

        new_fields = new_endpoints[key]
        removed = set(old_fields) - set(new_fields)
        added = set(new_fields) - set(old_fields)
        common = set(old_fields) & set(new_fields)

        # Rename heuristic: removed key + added key with matching type
        for r in list(removed):
            match = next((a for a in added if old_fields[r] == new_fields[a]), None)
            if match:
                changes.append(base_entry(
                    key, "field_renamed", True,
                    {r: old_fields[r]}, {match: new_fields[match]}, "high"
                ))
                removed.discard(r)
                added.discard(match)

        for r in removed:
            changes.append(base_entry(key, "field_removed", True, {r: old_fields[r]}, {}, "medium"))

        for a in added:
            changes.append(base_entry(key, "field_added_required", False, {}, {a: new_fields[a]}, "low"))

        for f in common:
            if old_fields[f] != new_fields[f]:
                changes.append(base_entry(
                    key, "field_type_changed", True,
                    {f: old_fields[f]}, {f: new_fields[f]}, "high"
                ))

    return changes


def main():
    if len(sys.argv) != 4:
        print("Usage: python diff_agent.py <old_openapi.json> <new_openapi.json> <output.json>")
        sys.exit(1)

    old_path, new_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    old_spec = load_spec(old_path)
    new_spec = load_spec(new_path)

    changes = diff_specs(old_spec, new_spec)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(changes, indent=2))
    print(f"Wrote {len(changes)} change(s) to {out_path}")
    for c in changes:
        print(f"  - [{c['severity']}] {c['change_type']} on {c['method']} {c['endpoint']}")


if __name__ == "__main__":
    main()