from __future__ import annotations

from enum import StrEnum
from importlib.resources import files
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from geodebug.adapters.base import AdapterError
from geodebug.api import check as check_target
from geodebug.api import compare as compare_targets
from geodebug.api import inspect as inspect_target
from geodebug.api import preflight as preflight_target
from geodebug.config.loader import ConfigError, load_config
from geodebug.config.model import FailOnName, ProfileName
from geodebug.engine.defaults import build_default_registry
from geodebug.engine.policy import Policy
from geodebug.models.report import Report
from geodebug.reporters.terminal import print_report, print_snapshot
from geodebug.version import __version__

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
rules_app = typer.Typer(no_args_is_help=True)
app.add_typer(rules_app, name="rules")
console = Console()
error_console = Console(stderr=True)


class OutputFormat(StrEnum):
    TERMINAL = "terminal"
    JSON = "json"


class SchemaKind(StrEnum):
    REPORT = "report"
    CONFIG = "config"


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def root(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show the version.",
        ),
    ] = False,
) -> None:
    """Deterministic diagnostics for geospatial data and workflows."""


@app.command("inspect")
def inspect_command(
    target: Path,
    deep: Annotated[bool, typer.Option(help="Allow full data scans.")] = False,
) -> None:
    """Inspect normalized facts without running diagnostic rules."""
    try:
        snapshot = inspect_target(target, deep=deep)
    except AdapterError as exc:
        error_console.print(str(exc), style="bold red")
        raise typer.Exit(code=2) from None
    print_snapshot(snapshot, console=console)


@app.command("check")
def check_command(
    target: Path,
    deep: Annotated[bool, typer.Option(help="Allow full data scans.")] = False,
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", help="Output format."),
    ] = OutputFormat.TERMINAL,
    config_path: Annotated[
        Path | None,
        typer.Option("--config", help="Path to .geodebug.toml."),
    ] = None,
    profile: Annotated[
        ProfileName | None,
        typer.Option(help="Override the configured policy profile."),
    ] = None,
    fail_on: Annotated[
        FailOnName | None,
        typer.Option(help="Override the configured CI failure threshold."),
    ] = None,
) -> None:
    """Run diagnostics against one dataset."""
    try:
        policy, threshold = _runtime_policy(config_path, profile, fail_on)
        report = check_target(target, deep=deep, policy=policy)
    except (AdapterError, ConfigError) as exc:
        error_console.print(str(exc), style="bold red")
        raise typer.Exit(code=2) from None
    _emit_report(report, output_format)
    raise typer.Exit(code=_exit_code(report, threshold))


@app.command("compare")
def compare_command(
    left: Path,
    right: Path,
    deep: Annotated[bool, typer.Option(help="Allow full data scans.")] = False,
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", help="Output format."),
    ] = OutputFormat.TERMINAL,
    config_path: Annotated[
        Path | None,
        typer.Option("--config", help="Path to .geodebug.toml."),
    ] = None,
    profile: Annotated[
        ProfileName | None,
        typer.Option(help="Override the configured policy profile."),
    ] = None,
    fail_on: Annotated[
        FailOnName | None,
        typer.Option(help="Override the configured CI failure threshold."),
    ] = None,
) -> None:
    """Run dataset and relational diagnostics against two datasets."""
    try:
        policy, threshold = _runtime_policy(config_path, profile, fail_on)
        report = compare_targets(left, right, deep=deep, policy=policy)
    except (AdapterError, ConfigError) as exc:
        error_console.print(str(exc), style="bold red")
        raise typer.Exit(code=2) from None
    _emit_report(report, output_format)
    raise typer.Exit(code=_exit_code(report, threshold))


@app.command("preflight")
def preflight_command(
    target: Path,
    operation: Annotated[
        str,
        typer.Option(help="Operation name, such as buffer, area, distance, or length."),
    ],
    distance: Annotated[
        float | None,
        typer.Option(help="Distance parameter for operations that require one."),
    ] = None,
    deep: Annotated[bool, typer.Option(help="Allow full data scans.")] = False,
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", help="Output format."),
    ] = OutputFormat.TERMINAL,
    config_path: Annotated[
        Path | None,
        typer.Option("--config", help="Path to .geodebug.toml."),
    ] = None,
    profile: Annotated[
        ProfileName | None,
        typer.Option(help="Override the configured policy profile."),
    ] = None,
    fail_on: Annotated[
        FailOnName | None,
        typer.Option(help="Override the configured CI failure threshold."),
    ] = None,
) -> None:
    """Check spatial semantics before executing an operation."""
    parameters = {"distance": distance} if distance is not None else {}
    try:
        policy, threshold = _runtime_policy(config_path, profile, fail_on)
        report = preflight_target(
            target,
            operation=operation,
            parameters=parameters,
            deep=deep,
            policy=policy,
        )
    except (AdapterError, ConfigError) as exc:
        error_console.print(str(exc), style="bold red")
        raise typer.Exit(code=2) from None
    _emit_report(report, output_format)
    raise typer.Exit(code=_exit_code(report, threshold))


@rules_app.command("list")
def list_rules() -> None:
    """List built-in diagnostic rules."""
    table = Table(show_header=True, header_style="bold")
    table.add_column("Rule")
    table.add_column("Name")
    table.add_column("Scope")
    table.add_column("Severity")
    for rule in build_default_registry().all():
        table.add_row(
            rule.spec.id,
            rule.spec.name,
            rule.spec.scope.value,
            rule.spec.default_severity.value,
        )
    console.print(table)


@rules_app.command("show")
def show_rule(rule_id: str) -> None:
    """Show the contract for one diagnostic rule."""
    registry = build_default_registry()
    try:
        rule = registry.get(rule_id.upper())
    except KeyError:
        console.print(f"Unknown rule: {rule_id}", style="bold red")
        raise typer.Exit(code=2) from None

    spec = rule.spec
    console.print(f"[bold]{spec.id}[/bold]  {spec.name}")
    console.print(f"Category:  {spec.category}")
    console.print(f"Scope:     {spec.scope.value}")
    console.print(f"Severity:  {spec.default_severity.value}")
    console.print(f"Certainty: {spec.certainty.value}")
    console.print(f"Cost:      {spec.cost.value}")
    console.print(f"Fix:       {spec.fix_safety.value}")
    if spec.requires:
        console.print("Requires:")
        for key in spec.requires:
            console.print(f"  - {key}")


@app.command("schema")
def schema(
    kind: Annotated[
        SchemaKind,
        typer.Option(help="Schema to print."),
    ] = SchemaKind.REPORT,
) -> None:
    """Print a canonical GeoDebug JSON Schema."""
    filename = "report.schema.json" if kind is SchemaKind.REPORT else "config.schema.json"
    typer.echo(
        files("geodebug.schemas").joinpath(filename).read_text(encoding="utf-8"),
        nl=False,
    )


def _runtime_policy(
    config_path: Path | None,
    profile: ProfileName | None,
    fail_on: FailOnName | None,
) -> tuple[Policy, FailOnName]:
    config = load_config(config_path)
    return (config.to_policy(profile=profile), fail_on or config.fail_on)


def _emit_report(report: Report, output_format: OutputFormat) -> None:
    if output_format is OutputFormat.JSON:
        typer.echo(report.model_dump_json(indent=2))
        return
    print_report(report, console=console)


def _exit_code(report: Report, fail_on: FailOnName) -> int:
    if fail_on is FailOnName.NONE:
        return 0
    if fail_on is FailOnName.WARNING:
        return 1 if report.summary.errors or report.summary.warnings else 0
    return 1 if report.summary.errors else 0


def main() -> None:
    app()
