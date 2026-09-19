from geodebug.engine.defaults import build_default_registry
from geodebug.engine.evaluator import Evaluator
from geodebug.facts.keys import CRS_AXIS_UNITS, CRS_KIND, CRS_PRESENT
from geodebug.models.enums import Severity
from geodebug.models.facts import FactRecord
from geodebug.models.operations import OperationContext


def test_evaluator_builds_stable_diagnostic_report(make_context) -> None:
    context = make_context(
        facts=[
            FactRecord.known(CRS_PRESENT, True),
            FactRecord.known(CRS_KIND, "geographic"),
            FactRecord.known(CRS_AXIS_UNITS, ("degree", "degree")),
        ],
        operation=OperationContext(name="buffer", parameters={"distance": 500}),
    )

    report = Evaluator(build_default_registry()).evaluate(context)

    assert [item.rule_id for item in report.diagnostics] == ["GEO501"]
    assert report.diagnostics[0].severity is Severity.ERROR
    assert report.diagnostics[0].fingerprint.startswith("geo501:")
    assert report.summary.errors == 1
