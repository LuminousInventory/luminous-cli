"""Integration field mappings and integration mappings."""

from __future__ import annotations

import typer

from luminous_cli.cli._options import (
    FileOption,
    FilterOption,
    FormatOption,
    JsonOption,
    PageOption,
    PerPageOption,
    SortOption,
    YesOption,
)
from luminous_cli.cli.resources._input import resolve_input
from luminous_cli.client import get_client
from luminous_cli.client.query import QueryParams
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format
from luminous_cli.output.json_out import render_json

# --- Integration Field Mappings ---

group = typer.Typer(name="integration-field-mappings", help="Integration field mappings")

COLUMNS = [
    ("ID", "id", "dim"),
    ("Field", "field_name", "cyan"),
    ("Luminous Value", "luminous_value", ""),
    ("External Value", "external_value", ""),
    ("Group", "mapping_group", ""),
]


@group.command("list")
def ifm_list(
    filter: FilterOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List integration field mappings."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, page=page, per_page=per_page)
    resp = client.list("/integration-field-mappings", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=COLUMNS, pagination=resp.pagination, fmt=fmt)


@group.command("get")
def ifm_get(
    mapping_id: int = typer.Argument(..., help="Mapping ID"),
    format: FormatOption = None,
) -> None:
    """Get an integration field mapping."""
    client = get_client()
    data = client.get("/integration-field-mappings", mapping_id)
    fmt = resolve_format(format)
    render(data, columns=COLUMNS, fmt=fmt)


@group.command("create")
def ifm_create(
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Create an integration field mapping."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.request("POST", "/integration-field-mappings", json_body=payload)
    render_json(data)


@group.command("update")
def ifm_update(
    mapping_id: int = typer.Argument(..., help="Mapping ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Update an integration field mapping."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.update("/integration-field-mappings", mapping_id, payload)
    render_json(data)


@group.command("delete")
def ifm_delete(
    mapping_id: int = typer.Argument(..., help="Mapping ID"),
    yes: YesOption = False,
) -> None:
    """Delete an integration field mapping."""
    if not yes:
        typer.confirm(f"Delete mapping {mapping_id}?", abort=True)
    client = get_client()
    client.delete("/integration-field-mappings", mapping_id)
    typer.echo(f"Deleted mapping {mapping_id}")


@group.command("bulk-create")
def ifm_bulk_create(
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Bulk create integration field mappings."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.request("POST", "/integration-field-mappings/bulk", json_body=payload)
    render_json(data)


@group.command("bulk-delete")
def ifm_bulk_delete(
    json_input: JsonOption = None,
    file: FileOption = None,
    yes: YesOption = False,
) -> None:
    """Bulk delete integration field mappings."""
    if not yes:
        typer.confirm("Bulk delete mappings?", abort=True)
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    client.request("POST", "/integration-field-mappings/bulk-delete", json_body=payload)
    typer.echo("Bulk delete complete")


@group.command("field-names")
def ifm_field_names() -> None:
    """List distinct field name values."""
    client = get_client()
    data = client.request("GET", "/integration-field-mappings/field-names")
    render_json(data)


@group.command("groups")
def ifm_groups() -> None:
    """List distinct mapping group values."""
    client = get_client()
    data = client.request("GET", "/integration-field-mappings/groups")
    render_json(data)


@group.command("suggest-carrier")
def ifm_suggest_carrier(
    carrier: str = typer.Argument(..., help="Carrier value to fuzzy match"),
) -> None:
    """Suggest carrier mapping via fuzzy match."""
    client = get_client()
    data = client.request("GET", "/integration-field-mappings/suggest-carrier", params={"carrier": carrier})
    render_json(data)


@group.command("create-and-retry")
def ifm_create_and_retry(
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Create an integration field mapping and retry failed records."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.request("POST", "/integration-field-mappings/create-and-retry", json_body=payload)
    render_json(data)


@group.command("auto-carrier-mapping")
def ifm_auto_carrier_mapping(
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Toggle automatic carrier mapping."""
    payload = resolve_input(json_input=json_input, file_input=file) or {}
    client = get_client()
    data = client.request("POST", "/integration-field-mappings/auto-carrier-mapping", json_body=payload)
    render_json(data)


# --- Integration Mappings ---

mappings_group = typer.Typer(name="integration-mappings", help="Integration mappings")

MAPPING_COLUMNS = [
    ("ID", "id", "dim"),
    ("Name", "name", "cyan"),
    ("Type", "type", ""),
]


@mappings_group.command("list")
def im_list(
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List integration mappings."""
    client = get_client()
    qp = QueryParams(page=page, per_page=per_page)
    resp = client.list("/integration-mappings", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=MAPPING_COLUMNS, pagination=resp.pagination, fmt=fmt)


@mappings_group.command("get")
def im_get(
    mapping_id: int = typer.Argument(..., help="Mapping ID"),
    format: FormatOption = None,
) -> None:
    """Get an integration mapping."""
    client = get_client()
    data = client.get("/integration-mappings", mapping_id)
    fmt = resolve_format(format)
    render(data, columns=MAPPING_COLUMNS, fmt=fmt)


@mappings_group.command("create")
def im_create(
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Create an integration mapping."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.request("POST", "/integration-mappings", json_body=payload)
    render_json(data)


@mappings_group.command("update")
def im_update(
    mapping_id: int = typer.Argument(..., help="Mapping ID"),
    json_input: JsonOption = None,
    file: FileOption = None,
) -> None:
    """Update an integration mapping."""
    payload = resolve_input(json_input=json_input, file_input=file)
    client = get_client()
    data = client.update("/integration-mappings", mapping_id, payload)
    render_json(data)


@mappings_group.command("delete")
def im_delete(
    mapping_id: int = typer.Argument(..., help="Mapping ID"),
    yes: YesOption = False,
) -> None:
    """Delete an integration mapping."""
    if not yes:
        typer.confirm(f"Delete mapping {mapping_id}?", abort=True)
    client = get_client()
    client.delete("/integration-mappings", mapping_id)
    typer.echo(f"Deleted mapping {mapping_id}")
