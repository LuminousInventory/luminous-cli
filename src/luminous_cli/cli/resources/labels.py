"""Labels resource."""

from __future__ import annotations

import typer

from luminous_cli.cli._options import FileOption, FormatOption, JsonOption
from luminous_cli.cli.resources._input import resolve_input
from luminous_cli.client import get_client
from luminous_cli.output.json_out import render_json

group = typer.Typer(name="labels", help="Label rendering")


@group.command("render")
def label_render(
    json_input: JsonOption = None,
    file: FileOption = None,
    format: FormatOption = None,
) -> None:
    """Render a label (returns label data/URL)."""
    payload = resolve_input(json_input=json_input, file_input=file)
    if not payload:
        typer.echo("Provide label data via --json or --file.", err=True)
        raise typer.Exit(code=1)
    client = get_client()
    data = client.request("POST", "/labels/render", json_body=payload)
    render_json(data)
