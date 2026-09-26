"""
Diff Agent — Mahi's core deliverable.

Usage:
    python diff_agent.py <old_openapi.json> <new_openapi.json> <output_diff_report.json>

What it does:
    1. Loads two OpenAPI specs (before/after a backend change).
    2. Extracts a simplified {endpoint: {field: type}} view of each.
    3. Diffs them and classifies each difference into one of:
       field_renamed, field_type_changed, field_added_required,
       field_removed, endpoint_removed
    4. Writes a list of diff entries matching diff_report.schema.json

This is plain deterministic Python — no Bob calls needed here. Test it against
all 3 of your drift branches before handing off to Khushi.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_spec(path: str) -> dict:
    return json.loads(Path(path).read_text())


def _resolve_schema_name(schema_obj: dict) -> str | None:
    """Follow a $ref (including inside 'items' for arrays) to find the schema name."""
    if not schema_obj:
        return None
    if "$ref" in schema_obj:
        return schema_obj["$ref"].split("/")[-1]
    if "items" in schema_obj and "$ref" in schema_obj["items"]:
        return schema_obj["items"]["$ref"].split("/")[-1]
    return None


def _unwrap_list_envelope(schema_name: str, components: dict) -> str:
    """
    Some endpoints (e.g. GET /items/) return a paginated envelope like:
        { "data": [ {...ItemPublic...} ], "count": 5 }
    rather than the item schema directly (this is ItemsPublic in the
    standard tiangolo template). If `schema_name` looks like one of these
    envelopes — has a "data" property that's an array of $ref items — this
    resolves through to the *inner* item schema instead, since that's the
    schema whose fields (title, description, etc.) actually matter for
    drift detection. Non-envelope schemas pass through unchanged.
    """
    schema = components.get(schema_name, {})
    props = schema.get("properties", {})
    data_prop = props.get("data", {})
    if data_prop.get("type") == "array":
        inner_ref = data_prop.get("items", {}).get("$ref")
        if inner_ref:
            return inner_ref.split("/")[-1]
    return schema_name


def get_endpoint_schemas(spec: dict) -> dict:
    """
    Returns { "METHOD /path": { field_name: field_type } } using each
    endpoint's 200-response body schema. Automatically unwraps paginated
    "data"-envelope responses (e.g. ItemsPublic -> ItemPublic) so drift is
    detected on the actual item fields, not the envelope shape. Extend this
    if you also want to diff request bodies (POST/PUT) — same pattern, just
    read details["requestBody"] instead of details["responses"]["200"].
    """
    result = {}
    paths = spec.get("paths", {})
    components = spec.get("components", {}).get("schemas", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() not in ("get", "post", "put", "delete", "patch"):
                continue
            key = f"{method.upper()} {path}"
            fields = {}

            responses = details.get("responses", {})
            ok_response = responses.get("200", {})
            content = ok_response.get("content", {}).get("application/json", {})
            schema_name = _resolve_schema_name(content.get("schema", {}))

            if schema_name and schema_name in components:
                schema_name = _unwrap_list_envelope(schema_name, components)

            if schema_name and schema_name in components:
                props = components[schema_name].get("properties", {})
                for field_name, field_def in props.items():
                    fields[field_name] = field_def.get("type", "unknown")

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
        # Endpoint removed entirely
        if key not in new_endpoints:
            changes.append(base_entry(key, "endpoint_removed", True, old_fields, {}, "high"))
            continue

        new_fields = new_endpoints[key]
        removed = set(old_fields) - set(new_fields)
        added = set(new_fields) - set(old_fields)
        common = set(old_fields) & set(new_fields)

        # Heuristic: a removed field + an added field of the SAME type in the
        # same commit is treated as a rename, not two separate changes.
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
            # A genuinely new field on a response is usually non-breaking (additive),
            # but flagged low severity so the team can eyeball it.
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