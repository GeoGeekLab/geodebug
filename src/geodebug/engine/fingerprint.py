from __future__ import annotations

import hashlib
import json
import math
from typing import Any

from geodebug.models.evidence import Evidence


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("diagnostic evidence must contain finite numeric values")
        return value
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(value[key]) for key in sorted(value, key=str)}
    raise TypeError(f"diagnostic evidence is not JSON-compatible: {type(value).__name__}")


def diagnostic_fingerprint(
    *,
    rule_id: str,
    subject_ids: tuple[str, ...],
    operation_name: str | None,
    evidence: tuple[Evidence, ...],
) -> str:
    payload = {
        "rule_id": rule_id,
        "subject_ids": list(subject_ids),
        "operation": operation_name,
        "evidence": [
            {"key": item.key, "value": _json_value(item.value)}
            for item in sorted(evidence, key=lambda value: value.key)
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]
    return f"{rule_id.lower()}:{digest}"
