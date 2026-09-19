import json
from importlib.resources import files
from pathlib import Path

from jsonschema import Draft202012Validator

from geodebug.config.model import GeoDebugConfig
from geodebug.engine.defaults import build_default_registry
from geodebug.engine.evaluator import Evaluator
from geodebug.models.context import EvaluationContext

SCHEMA_DIR = Path(__file__).parents[2] / "schemas"


def test_report_schema_is_valid_and_packaged_verbatim() -> None:
    source_text = (SCHEMA_DIR / "report.schema.json").read_text(encoding="utf-8")
    packaged_text = files("geodebug.schemas").joinpath("report.schema.json").read_text(
        encoding="utf-8"
    )
    assert packaged_text == source_text

    schema = json.loads(source_text)
    Draft202012Validator.check_schema(schema)
    report = Evaluator(build_default_registry()).evaluate(EvaluationContext(subjects=()))
    Draft202012Validator(schema).validate(report.model_dump(mode="json"))


def test_config_schema_is_valid_and_packaged_verbatim() -> None:
    source_text = (SCHEMA_DIR / "config.schema.json").read_text(encoding="utf-8")
    packaged_text = files("geodebug.schemas").joinpath("config.schema.json").read_text(
        encoding="utf-8"
    )
    assert packaged_text == source_text

    schema = json.loads(source_text)
    Draft202012Validator.check_schema(schema)
    config = GeoDebugConfig()
    Draft202012Validator(schema).validate(config.model_dump(mode="json"))
