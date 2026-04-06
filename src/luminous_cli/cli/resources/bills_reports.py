"""Bills/AP aging reports."""

from __future__ import annotations

import typer

from luminous_cli.cli._options import FormatOption
from luminous_cli.client import get_client
from luminous_cli.output.detect import resolve_format
from luminous_cli.output.json_out import render_json

group = typer.Typer(name="bills", help="AP bills and aging reports")


@group.command("aging")
def bills_aging(
    format: FormatOption = None,
) -> None:
    """AP bills aging report grouped by vendor."""
    client = get_client()
    data = client.request("GET", "/bills/reports/aging")
    fmt = resolve_format(format)
    # This endpoint returns {as_of_date, vendors, totals} — not standard list format
    render_json(data)
