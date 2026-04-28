"""Integration accounts resource."""

from __future__ import annotations

import typer

from luminous_cli.cli._options import FormatOption
from luminous_cli.client import get_client
from luminous_cli.output.json_out import render_json

group = typer.Typer(name="integration-accounts", help="Integration accounts")


@group.command("shipping-methods")
def ia_shipping_methods(
    integration_account_id: int = typer.Argument(..., help="Integration account ID"),
    format: FormatOption = None,
) -> None:
    """List OMS shipping methods for an integration account (live-fetched)."""
    client = get_client()
    data = client.request(
        "GET", f"/integration-accounts/{integration_account_id}/shipping-methods"
    )
    render_json(data)
