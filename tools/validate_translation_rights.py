#!/usr/bin/env python3
"""Validate translation-rights records and fail closed before publication."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VALID_STATUSES = {"review_required", "approved", "rejected"}
REQUIRED_FIELDS = {
    "schema_version", "edition_id", "display_name", "source_url",
    "rights_holder", "rights_status", "territories", "permissions",
    "evidence", "review",
}
PERMISSION_FIELDS = {"display", "cache", "redistribute", "transform", "ai_use"}


class RightsValidationError(ValueError):
    pass


def validate_record(record: Any, territory: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a JSON object"]

    missing = sorted(REQUIRED_FIELDS - record.keys())
    if missing:
        errors.append("missing required fields: " + ", ".join(missing))
        return errors

    if record["schema_version"] != 1:
        errors.append("schema_version must be 1")
    for field in ("edition_id", "display_name", "source_url", "rights_holder"):
        if not isinstance(record[field], str) or not record[field].strip():
            errors.append(f"{field} must be a non-empty string")

    status = record["rights_status"]
    if status not in VALID_STATUSES:
        errors.append("rights_status must be review_required, approved or rejected")

    territories = record["territories"]
    if not isinstance(territories, list) or any(not isinstance(x, str) or not x for x in territories):
        errors.append("territories must be an array of non-empty territory codes")
        territories = []

    permissions = record["permissions"]
    if not isinstance(permissions, dict) or set(permissions) != PERMISSION_FIELDS:
        errors.append("permissions must contain exactly: " + ", ".join(sorted(PERMISSION_FIELDS)))
    else:
        for key, value in permissions.items():
            if value not in (True, False, "conditional", "unknown"):
                errors.append(f"permissions.{key} must be true, false, conditional or unknown")

    evidence = record["evidence"]
    if not isinstance(evidence, list):
        errors.append("evidence must be an array")
        evidence = []

    review = record["review"]
    if not isinstance(review, dict):
        errors.append("review must be an object")
        review = {}

    if status == "approved":
        if not territories:
            errors.append("approved rights record must list at least one territory")
        if not evidence:
            errors.append("approved rights record must include evidence")
        if not review.get("reviewer") or not review.get("reviewed_at"):
            errors.append("approved rights record requires reviewer and reviewed_at")
        if not review.get("decision_reference"):
            errors.append("approved rights record requires decision_reference")
        if isinstance(permissions, dict):
            for key in ("display", "cache"):
                if permissions.get(key) is not True:
                    errors.append(f"approved reader edition requires permissions.{key}=true")

    if territory:
        if status != "approved":
            errors.append(f"edition is not approved for publication (status: {status})")
        elif territory not in territories:
            errors.append(f"territory {territory} is not covered by the approval")

    return errors


def validate_document(document: Any, territory: str | None = None) -> dict[str, Any]:
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        return {"valid": False, "errors": ["document must be an object with schema_version 1"]}
    editions = document.get("editions")
    if not isinstance(editions, list) or not editions:
        return {"valid": False, "errors": ["editions must be a non-empty array"]}

    errors: list[str] = []
    seen: set[str] = set()
    for index, record in enumerate(editions):
        for error in validate_record(record, territory):
            errors.append(f"editions[{index}]: {error}")
        if isinstance(record, dict):
            edition_id = record.get("edition_id")
            if isinstance(edition_id, str):
                if edition_id in seen:
                    errors.append(f"duplicate edition_id: {edition_id}")
                seen.add(edition_id)
    return {"valid": not errors, "edition_count": len(editions), "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("register", type=Path)
    parser.add_argument("--territory", help="Require publication approval for a territory code, e.g. IN")
    args = parser.parse_args()
    try:
        document = json.loads(args.register.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}))
        return 2
    result = validate_document(document, args.territory)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
