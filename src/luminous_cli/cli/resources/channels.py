"""Channels resource."""

from __future__ import annotations

import typer

from luminous_cli.cli._options import FileOption, FormatOption, JsonOption
from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.cli.resources._input import resolve_input
from luminous_cli.client import get_client
from luminous_cli.output.json_out import render_json

spec = ResourceSpec(
    name="channels",
    singular="channel",
    api_path="/channels",
    columns=[
        ("ID", "id", "dim"),
        ("Label", "label", "cyan"),
        ("Type", "channelType", ""),
        ("Status", "status", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
    update_method="PUT",
)

group = make_resource_group(spec)


@group.command("create-sales")
def channels_create_sales(
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Create a sales channel (legacy endpoint POST /channels/sales)."""
    payload = resolve_input(json_input=json_input, file_input=file)
    if not payload:
        typer.echo("Provide channel data via --json or --file.", err=True)
        raise typer.Exit(code=1)
    client = get_client()
    data = client.request("POST", "/channels/sales", json_body=payload)
    render_json(data)


@group.command("sync-integration-products")
def channels_sync_integration_products(
    channel_id: int = typer.Argument(..., help="Channel ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Sync integration products to a channel."""
    payload = resolve_input(json_input=json_input, file_input=file)
    if not payload:
        typer.echo("Provide items payload via --json or --file.", err=True)
        raise typer.Exit(code=1)
    client = get_client()
    data = client.request(
        "POST", f"/channels/{channel_id}/integration-products", json_body=payload
    )
    render_json(data)


@group.command("lock")
def channels_lock(
    channel_id: int = typer.Argument(..., help="Channel ID"),
    api_locked: bool = typer.Option(
        ..., "--api-locked/--api-unlocked", help="Lock state for API access"
    ),
) -> None:
    """Lock or unlock a channel for API access (PATCH)."""
    client = get_client()
    data = client.request(
        "PATCH", f"/channels/{channel_id}/lock", json_body={"apiLocked": api_locked}
    )
    render_json(data)
