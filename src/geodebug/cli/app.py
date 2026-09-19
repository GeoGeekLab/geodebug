from __future__ import annotations

from importlib.resources import files
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from geodebug.engine.defaults import build_default_registry
from geodebug.version import __version__

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
rules_app = typer.Typer(no_args_is_help=True)
app.add_typer(rules_app, name="rules")
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def root(
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version_callback, is_eager=True, help="Show the version."),
    ] = False,
) -> None:
    """Deterministic diagnostics for geospatial data and workflows."""


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


def main() -> None:
    app()
