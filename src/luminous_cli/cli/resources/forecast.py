"""Materialized forecast data."""

from __future__ import annotations

from typing import Optional

import typer

from luminous_cli.cli._options import FilterOption, FormatOption, PageOption, PerPageOption, SortOption
from luminous_cli.client import get_client
from luminous_cli.client.query import QueryParams
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format
from luminous_cli.output.json_out import render_json

group = typer.Typer(name="forecast", help="Materialized forecast data (requires forecast feature)")

COLUMNS = [
    ("ID", "id", "dim"),
    ("SKU", "internal_sku", "cyan"),
    ("Product", "product_name", ""),
    ("On Hand", "qty_onhand", "green"),
    ("Incoming", "qty_incoming", ""),
    ("7d Sales", "sale_within_7_days", ""),
    ("30d Sales", "sale_within_30_days", ""),
    ("90d Sales", "sale_within_90_days", ""),
    ("Velocity 30d", "sale_velocity_30_days", ""),
    ("Days OH 30d", "days_onhand_30_day_vel", ""),
    ("Reorder Pt", "reorder_point", "yellow"),
    ("Lead Time", "lead_time", ""),
]

WH_COLUMNS = [
    ("ID", "id", "dim"),
    ("SKU", "internal_sku", "cyan"),
    ("Product", "product_name", ""),
    ("Warehouse", "warehouse_group_label", ""),
    ("On Hand", "qty_onhand", "green"),
    ("Incoming", "qty_incoming", ""),
    ("7d Sales", "sale_within_7_days", ""),
    ("30d Sales", "sale_within_30_days", ""),
    ("Velocity 30d", "sale_velocity_30_days", ""),
]


@group.command("list")
def forecast_list(
    filter: FilterOption = None,
    sort: SortOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List materialized forecast rows."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, page=page, per_page=per_page)
    resp = client.list("/forecast-data", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=COLUMNS, pagination=resp.pagination, fmt=fmt)


@group.command("get")
def forecast_get(
    forecast_id: int = typer.Argument(..., help="Forecast row ID"),
    format: FormatOption = None,
) -> None:
    """Get a single forecast row by ID."""
    client = get_client()
    data = client.get("/forecast-data", forecast_id)
    fmt = resolve_format(format)
    render(data, columns=COLUMNS, fmt=fmt)


@group.command("product")
def forecast_product(
    rfq_id: int = typer.Argument(..., help="Product RFQ ID"),
    format: FormatOption = None,
) -> None:
    """Get forecast row for a product by RFQ ID."""
    client = get_client()
    data = client.request("GET", f"/forecast-data/product/{rfq_id}")
    result = data.get("data", data)
    fmt = resolve_format(format)
    render(result, columns=COLUMNS, fmt=fmt)


@group.command("export")
def forecast_export(
    filter: FilterOption = None,
) -> None:
    """Export forecast data as CSV or Excel."""
    client = get_client()
    params: dict[str, str] = {}
    if filter:
        qp = QueryParams.from_cli_args(raw_filters=filter)
        params = qp.filters
    data = client.request("GET", "/forecast-data/export", params=params)
    render_json(data)


@group.command("refresh-status")
def forecast_refresh_status() -> None:
    """Check forecast data refresh status."""
    client = get_client()
    data = client.request("GET", "/forecast-data/refresh-status")
    from rich.console import Console
    stderr = Console(stderr=True)
    stderr.print(f"Last refreshed: [cyan]{data.get('refreshed_at', 'unknown')}[/cyan]")
    stderr.print(f"Total records:  [cyan]{data.get('total_records', 'unknown')}[/cyan]")
    stderr.print(f"Stale:          [{'red' if data.get('is_stale') else 'green'}]{data.get('is_stale', 'unknown')}[/]")


# --- Warehouse-level forecast ---

warehouse_app = typer.Typer(name="warehouse", help="Warehouse-level forecast data")


@warehouse_app.command("list")
def wh_forecast_list(
    filter: FilterOption = None,
    sort: SortOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """List warehouse-level forecast rows."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, page=page, per_page=per_page)
    resp = client.list("/forecast-warehouse-data", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=WH_COLUMNS, pagination=resp.pagination, fmt=fmt)


@warehouse_app.command("get")
def wh_forecast_get(
    forecast_id: int = typer.Argument(..., help="Warehouse forecast row ID"),
    format: FormatOption = None,
) -> None:
    """Get a single warehouse forecast row by ID."""
    client = get_client()
    data = client.get("/forecast-warehouse-data", forecast_id)
    fmt = resolve_format(format)
    render(data, columns=WH_COLUMNS, fmt=fmt)


@warehouse_app.command("product")
def wh_forecast_product(
    rfq_id: int = typer.Argument(..., help="Product RFQ ID"),
    format: FormatOption = None,
) -> None:
    """Get all warehouse forecast rows for a product."""
    client = get_client()
    data = client.request("GET", f"/forecast-warehouse-data/product/{rfq_id}")
    result = data.get("data", data)
    fmt = resolve_format(format)
    if isinstance(result, list):
        render(result, columns=WH_COLUMNS, fmt=fmt)
    else:
        render(result, columns=WH_COLUMNS, fmt=fmt)


@warehouse_app.command("export")
def wh_forecast_export(
    filter: FilterOption = None,
) -> None:
    """Export warehouse forecast data."""
    client = get_client()
    params: dict[str, str] = {}
    if filter:
        qp = QueryParams.from_cli_args(raw_filters=filter)
        params = qp.filters
    data = client.request("GET", "/forecast-warehouse-data/export", params=params)
    render_json(data)


@warehouse_app.command("refresh-status")
def wh_forecast_refresh_status() -> None:
    """Check warehouse forecast refresh status."""
    client = get_client()
    data = client.request("GET", "/forecast-warehouse-data/refresh-status")
    from rich.console import Console
    stderr = Console(stderr=True)
    stderr.print(f"Last refreshed: [cyan]{data.get('refreshed_at', 'unknown')}[/cyan]")
    stderr.print(f"Total records:  [cyan]{data.get('total_records', 'unknown')}[/cyan]")
    stderr.print(f"Stale:          [{'red' if data.get('is_stale') else 'green'}]{data.get('is_stale', 'unknown')}[/]")


group.add_typer(warehouse_app)
