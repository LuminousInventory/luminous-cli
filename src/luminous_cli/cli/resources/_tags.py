"""Reusable tags subcommand factory."""

from __future__ import annotations

from typing import Optional

import typer

from luminous_cli.cli._options import FormatOption
from luminous_cli.client import get_client
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format

TAG_COLUMNS = [
    ("ID", "id", "dim"),
    ("Name", "name", "cyan"),
]


def make_tags_group(resource_type: str) -> typer.Typer:
    """Generate a tags subcommand group for a taggable resource.

    Args:
        resource_type: API resource type slug (e.g., "sales-orders", "products", "invoices")
    """
    group = typer.Typer(name="tags", help=f"Manage tags on {resource_type}")

    @group.command("list")
    def tags_list(
        record_id: int = typer.Argument(..., help="Record ID"),
        format: FormatOption = None,
    ) -> None:
        """List tags on a record."""
        client = get_client()
        data = client.request("GET", f"/{resource_type}/{record_id}/tags")
        fmt = resolve_format(format)
        tags_data = data.get("data", data) if isinstance(data, dict) else data
        if isinstance(tags_data, dict):
            tags_data = [tags_data]
        render(tags_data, columns=TAG_COLUMNS, fmt=fmt)

    @group.command("add")
    def tags_add(
        record_id: int = typer.Argument(..., help="Record ID"),
        tag: list[str] = typer.Option(..., "--tag", help="Tag to attach. Repeatable."),
    ) -> None:
        """Attach tags to a record."""
        client = get_client()
        client.request("POST", f"/{resource_type}/{record_id}/tags", json_body={"tags": tag})
        typer.echo(f"Added {len(tag)} tag(s)")

    @group.command("replace")
    def tags_replace(
        record_id: int = typer.Argument(..., help="Record ID"),
        tag: list[str] = typer.Option(..., "--tag", help="Tag. Repeatable. Replaces all existing."),
    ) -> None:
        """Replace all tags on a record."""
        client = get_client()
        client.request("PUT", f"/{resource_type}/{record_id}/tags", json_body={"tags": tag})
        typer.echo(f"Replaced tags with {len(tag)} tag(s)")

    @group.command("remove")
    def tags_remove(
        record_id: int = typer.Argument(..., help="Record ID"),
        tag: str = typer.Argument(..., help="Tag name to remove"),
    ) -> None:
        """Remove a tag from a record."""
        client = get_client()
        client.request("DELETE", f"/{resource_type}/{record_id}/tags/{tag}")
        typer.echo(f"Removed tag '{tag}'")

    return group
