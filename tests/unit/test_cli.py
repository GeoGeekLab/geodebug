import json

from typer.testing import CliRunner

from geodebug.cli.app import app

runner = CliRunner()


def test_schema_command_emits_canonical_schema() -> None:
    result = runner.invoke(app, ["schema"])

    assert result.exit_code == 0
    schema = json.loads(result.stdout)
    assert schema["title"] == "GeoDebug Report"
    assert schema["properties"]["schema_version"]["const"] == "1.0.0"


def test_rules_list_contains_sentinel_rules() -> None:
    result = runner.invoke(app, ["rules", "list"])

    assert result.exit_code == 0
    assert "GEO101" in result.stdout
    assert "GEO201" in result.stdout
    assert "GEO501" in result.stdout
