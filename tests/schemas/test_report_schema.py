import json
from importlib.resources import files
from pathlib import Path

from jsonschema import Draft202012Validator

from geodebug.engine.defaults import build_default_registry
from geodebug.engine.evaluator import Evaluator
from geodebug.models.context import EvaluationContext

SCHEMA_PATH = Path(__file__).parents[2] / "schemas" / "report.schema.json"


def test_reports_validate_against_checked_in_schema() -> None:
    source_text = SCHEMA_PATH.read_text(encoding="utf-8")
    packaged_text = files("geodebug.schemas").joinpath("report.schema.json").read_text(
        encoding="utf-8"
    )
    assert packaged_text == source_text

    schema = json.loads(source_text)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    report = Evaluator(build_default_registry()).evaluate(EvaluationContext(subjects=()))

    validator.validate(report.model_dump(mode="json"))
