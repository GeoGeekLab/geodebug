import pytest

from geodebug.engine.fingerprint import diagnostic_fingerprint
from geodebug.models.evidence import Evidence


def test_fingerprint_rejects_non_finite_evidence() -> None:
    with pytest.raises(ValueError, match="finite"):
        diagnostic_fingerprint(
            rule_id="GEO999",
            subject_ids=("subject:test",),
            operation_name=None,
            evidence=(Evidence(key="value", value=float("nan")),),
        )
