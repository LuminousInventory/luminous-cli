"""Currency management."""

from __future__ import annotations

from typing import Optional

import typer

from luminous_cli.cli._options import FormatOption, JsonOption, FileOption
from luminous_cli.cli.resources._input import resolve_input
from luminous_cli.client import get_client
from luminous_cli.output.detect import resolve_format
from luminous_cli.output.json_out import render_json

group = typer.Typer(name="currency", help="Currency rates and conversion")


@group.command("list")
def currency_list(format: FormatOption = None) -> None:
    """List available currencies."""
    client = get_client()
    data = client.request("GET", "/currency/available")
    render_json(data)


@group.command("base")
def currency_base(format: FormatOption = None) -> None:
    """Get the configured base currency."""
    client = get_client()
    data = client.request("GET", "/currency/base")
    render_json(data)


@group.command("set-base")
def currency_set_base(
    currency: str = typer.Argument(..., help="Currency code (e.g. USD)"),
) -> None:
    """Set the base currency."""
    client = get_client()
    client.request("POST", "/currency/base", json_body={"currency": currency})
    typer.echo(f"Base currency set to {currency}")


@group.command("rates")
def currency_rates(format: FormatOption = None) -> None:
    """List currency exchange rates."""
    client = get_client()
    data = client.request("GET", "/currency/rates")
    render_json(data)


@group.command("create-rate")
def currency_create_rate(
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Create a new currency exchange rate."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.request("POST", "/currency/rates", json_body=payload)
    render_json(data)


@group.command("convert")
def currency_convert(
    amount: float = typer.Argument(..., help="Amount to convert"),
    source: str = typer.Option(..., "--from", help="Source currency code"),
    target: str = typer.Option(..., "--to", help="Target currency code"),
) -> None:
    """Convert an amount between currencies."""
    client = get_client()
    data = client.request("GET", "/currency/rates/convert", params={
        "amount": str(amount), "from": source, "to": target,
    })
    render_json(data)
