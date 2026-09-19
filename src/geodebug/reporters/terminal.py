from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.table import Table
from rich.text import Text

from geodebug.models.facts import FactRecord
from geodebug.models.report import Report
from geodebug.models.subjects import DatasetSnapshot


def print_snapshot(snapshot: DatasetSnapshot, *, console: Console) -> None:
    console.print(f"[bold]{snapshot.subject.label or snapshot.subject.id}[/bold]")
    console.print(
        f"{snapshot.subject.kind.value} · adapter={snapshot.subject.adapter or 'unknown'}"
    )
    table = Table(show_header=True, header_style="bold")
    table.add_column("Fact")
    table.add_column("State")
    table.add_column("Value")
    table.add_column("Certainty")
    for fact in snapshot.facts:
        table.add_row(
            fact.key,
            fact.state.value,
            Text(_format_value(fact)),
            fact.certainty.value,
        )
    console.print(table)


def print_report(report: Report, *, console: Console) -> None:
    for subject in report.subjects:
        console.print(f"[bold]{subject.label or subject.id}[/bold]")

    if not report.diagnostics:
        console.print("[green]No diagnostics.[/green]")
    else:
        for diagnostic in report.diagnostics:
            style = {
                "error": "bold red",
                "warning": "bold yellow",
                "note": "bold cyan",
            }[diagnostic.severity.value]
            console.print(
                f"[{style}]{diagnostic.severity.value.upper()}[/{style}] "
                f"[bold]{diagnostic.rule_id}[/bold]  {diagnostic.message}"
            )
            for evidence in diagnostic.evidence:
                console.print(f"  {evidence.key}: {_format_json_value(evidence.value)}")

    summary = report.summary
    console.print(
        f"{summary.errors} error(s) · {summary.warnings} warning(s) · "
        f"{summary.notes} note(s) · {summary.unknown_rules} unknown"
    )


def _format_value(fact: FactRecord) -> str:
    if fact.state.value != "known":
        return "—"
    return _format_json_value(fact.value)


def _format_json_value(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    return str(value)
