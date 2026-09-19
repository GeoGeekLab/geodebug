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


def test_rules_list_contains_usable_core_rules() -> None:
    result = runner.invoke(app, ["rules", "list"])

    assert result.exit_code == 0
    for rule_id in ("GEO101", "GEO201", "GEO402", "GEO404", "GEO501"):
        assert rule_id in result.stdout


def test_check_json_exit_code_is_zero_for_clean_geojson(tmp_path) -> None:
    path = tmp_path / "point.geojson"
    path.write_text(
        json.dumps(
            {
                "type": "Feature",
                "properties": {},
                "geometry": {"type": "Point", "coordinates": [0, 0]},
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check", str(path), "--format", "json"])

    assert result.exit_code == 0
    report = json.loads(result.stdout)
    assert report["diagnostics"] == []
