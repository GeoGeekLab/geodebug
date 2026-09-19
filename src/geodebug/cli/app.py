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
from geodebug.engine.defaults import build_default_registry
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


class FailOn(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    NONE = "none"


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
    deep: Annotated[bool, typer.Option(help="Allow full geometry scans.")] = False,
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
    deep: Annotated[bool, typer.Option(help="Allow full geometry scans.")] = False,
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", help="Output format."),
    ] = OutputFormat.TERMINAL,
    fail_on: Annotated[
        FailOn,
        typer.Option(help="Diagnostic severity that fails the command."),
    ] = FailOn.ERROR,
) -> None:
    """Run diagnostics against one dataset."""
    try:
        report = check_target(target, deep=deep)
    except AdapterError as exc:
        error_console.print(str(exc), style="bold red")
        raise typer.Exit(code=2) from None
    _emit_report(report, output_format)
    raise typer.Exit(code=_exit_code(report, fail_on))


@app.command("compare")
def compare_command(
    left: Path,
    right: Path,
    deep: Annotated[bool, typer.Option(help="Allow full geometry scans.")] = False,
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", help="Output format."),
    ] = OutputFormat.TERMINAL,
    fail_on: Annotated[
        FailOn,
        typer.Option(help="Diagnostic severity that fails the command."),
    ] = FailOn.ERROR,
) -> None:
    """Run dataset and relational diagnostics against two datasets."""
    try:
        report = compare_targets(left, right, deep=deep)
    except AdapterError as exc:
        error_console.print(str(exc), style="bold red")
        raise typer.Exit(code=2) from None
    _emit_report(report, output_format)
    raise typer.Exit(code=_exit_code(report, fail_on))


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
def schema() -> None:
    """Print the canonical report JSON Schema."""
    typer.echo(
        files("geodebug.schemas").joinpath("report.schema.json").read_text(encoding="utf-8"),
        nl=False,
    )


def _emit_report(report: Report, output_format: OutputFormat) -> None:
    if output_format is OutputFormat.JSON:
        typer.echo(report.model_dump_json(indent=2))
        return
    print_report(report, console=console)


def _exit_code(report: Report, fail_on: FailOn) -> int:
    if fail_on is FailOn.NONE:
        return 0
    if fail_on is FailOn.WARNING:
        return 1 if report.summary.errors or report.summary.warnings else 0
    return 1 if report.summary.errors else 0


def main() -> None:
    app()
