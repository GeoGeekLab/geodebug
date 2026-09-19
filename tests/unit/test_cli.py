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
    for rule_id in ("GEO101", "GEO103", "GEO201", "GEO301", "GEO402", "GEO501", "GEO502"):
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


def test_config_can_suppress_rule_from_cli(tmp_path) -> None:
    data_path = tmp_path / "bad.geojson"
    data_path.write_text(
        json.dumps(
            {
                "type": "Point",
                "coordinates": [0, 95],
            }
        ),
        encoding="utf-8",
    )
    config_path = tmp_path / ".geodebug.toml"
    config_path.write_text(
        """
[[suppress]]
rule = "GEO103"
path = "*.geojson"
reason = "Fixture intentionally uses invalid latitude"
""".strip(),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "check",
            str(data_path),
            "--config",
            str(config_path),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    report = json.loads(result.stdout)
    assert report["diagnostics"] == []


def test_preflight_cli_detects_area_in_geographic_crs(tmp_path) -> None:
    data_path = tmp_path / "polygon.geojson"
    data_path.write_text(
        json.dumps(
            {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "preflight",
            str(data_path),
            "--operation",
            "area",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 1
    report = json.loads(result.stdout)
    assert [item["rule_id"] for item in report["diagnostics"]] == ["GEO502"]


def test_schema_command_emits_config_schema() -> None:
    result = runner.invoke(app, ["schema", "--kind", "config"])

    assert result.exit_code == 0
    schema = json.loads(result.stdout)
    assert schema["title"] == "GeoDebug Config"
    assert schema["properties"]["schema_version"]["const"] == "1"
