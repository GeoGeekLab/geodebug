from enum import StrEnum


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    NOTE = "note"


class Certainty(StrEnum):
    DETERMINISTIC = "deterministic"
    INFERRED = "inferred"
    HEURISTIC = "heuristic"


class RuleState(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class SubjectKind(StrEnum):
    DATASET = "dataset"
    VECTOR = "vector"
    RASTER = "raster"


class RuleScope(StrEnum):
    DATASET = "dataset"
    RELATION = "relation"
    OPERATION = "operation"
    POSTCONDITION = "postcondition"


class CostClass(StrEnum):
    METADATA = "metadata"
    SAMPLE = "sample"
    FULL_SCAN = "full_scan"
    RUNTIME = "runtime"


class FixSafety(StrEnum):
    NONE = "none"
    SAFE = "safe"
    REVIEW_REQUIRED = "review_required"
    DESTRUCTIVE = "destructive"


class FactState(StrEnum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"
