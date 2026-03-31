"""Reusable custom fields subcommand factory."""

from __future__ import annotations

import typer

from luminous_cli.cli._options import FormatOption
from luminous_cli.client import get_client
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format

CF_COLUMNS = [
    ("Field", "key", "cyan"),
    ("Value", "value", ""),
]


def make_custom_fields_group(resource_type: str) -> typer.Typer:
    """Generate a custom-fields subcommand group.

    Args:
        resource_type: API resource type slug (e.g., "sales-orders", "products")
    """
    group = typer.Typer(name="custom-fields", help=f"Manage custom fields on {resource_type}")

    @group.command("get")
    def cf_get(
        record_id: int = typer.Argument(..., help="Record ID"),
        format: FormatOption = None,
    ) -> None:
        """Get custom field values for a record."""
        client = get_client()
        data = client.request("GET", f"/{resource_type}/{record_id}/custom-fields")
        fields_data = data.get("data", data) if isinstance(data, dict) else data
        # Normalize dict-of-values to list-of-dicts for table display
        if isinstance(fields_data, dict) and not any(isinstance(v, dict) for v in fields_data.values()):
            fields_data = [{"key": k, "value": v} for k, v in fields_data.items()]
        fmt = resolve_format(format)
        render(fields_data, columns=CF_COLUMNS, fmt=fmt)

    @group.command("set")
    def cf_set(
        record_id: int = typer.Argument(..., help="Record ID"),
        field: list[str] = typer.Option(
            ..., "--field", help="Field as key=value. Repeatable."
        ),
    ) -> None:
        """Update custom field values for a record."""
        payload: dict = {}
        for f in field:
            key, _, value = f.partition("=")
            payload[key.strip()] = value.strip()

        client = get_client()
        client.request("PUT", f"/{resource_type}/{record_id}/custom-fields", json_body=payload)
        typer.echo(f"Updated {len(payload)} custom field(s)")

    return group
