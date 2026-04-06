"""Reports: Close the Books, Discrepancy, Transaction COGS, EDI."""

from __future__ import annotations

from typing import Optional

import typer

from luminous_cli.cli._options import FilterOption, FormatOption, PageOption, PerPageOption, SortOption
from luminous_cli.client import get_client
from luminous_cli.client.query import QueryParams
from luminous_cli.output import render
from luminous_cli.output.detect import resolve_format
from luminous_cli.output.json_out import render_json

group = typer.Typer(name="reports", help="Financial and operational reports")

# --- Close the Books ---

close_books_app = typer.Typer(name="close-books", help="Close the Books reports")


@close_books_app.command("sales-summary")
def sales_summary(
    start_date: str = typer.Option(..., "--start-date", help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(..., "--end-date", help="End date (YYYY-MM-DD, max 3 months from start)"),
    format: FormatOption = None,
) -> None:
    """Sales summary by channel for a date range."""
    client = get_client()
    data = client.request("GET", "/reports/close-books/sales-summary", params={
        "start_date": start_date, "end_date": end_date,
    })
    render_json(data)


@close_books_app.command("zero-cost-items")
def zero_cost_items(
    start_date: str = typer.Option(..., "--start-date"),
    end_date: str = typer.Option(..., "--end-date"),
    format: FormatOption = None,
) -> None:
    """Line items with zero cost in a date range."""
    client = get_client()
    data = client.request("GET", "/reports/close-books/zero-cost-items", params={
        "start_date": start_date, "end_date": end_date,
    })
    render_json(data)


@close_books_app.command("zero-valuation")
def zero_valuation(
    format: FormatOption = None,
) -> None:
    """Inventory items with zero valuation."""
    client = get_client()
    data = client.request("GET", "/reports/close-books/zero-valuation-inventory")
    render_json(data)


@close_books_app.command("invoice-sync-errors")
def invoice_sync_errors(
    start_date: str = typer.Option(..., "--start-date"),
    end_date: str = typer.Option(..., "--end-date"),
    format: FormatOption = None,
) -> None:
    """Invoice sync errors (e.g. QuickBooks) in a date range."""
    client = get_client()
    data = client.request("GET", "/reports/close-books/invoice-sync-errors", params={
        "start_date": start_date, "end_date": end_date,
    })
    render_json(data)


group.add_typer(close_books_app)

# --- Inventory Discrepancy ---

discrepancy_app = typer.Typer(name="discrepancy", help="Inventory discrepancy reports")


@discrepancy_app.command("list")
def discrepancy_list(
    warehouse_id: Optional[int] = typer.Option(None, "--warehouse-id"),
    format: FormatOption = None,
) -> None:
    """Stock and cost-layer discrepancy rows."""
    client = get_client()
    params: dict[str, str] = {}
    if warehouse_id is not None:
        params["warehouse_id"] = str(warehouse_id)
    data = client.request("GET", "/reports/inventory-discrepancy", params=params)
    render_json(data)


@discrepancy_app.command("dashboard")
def discrepancy_dashboard(
    warehouse_id: Optional[int] = typer.Option(None, "--warehouse-id"),
    format: FormatOption = None,
) -> None:
    """Discrepancy dashboard summary."""
    client = get_client()
    params: dict[str, str] = {}
    if warehouse_id is not None:
        params["warehouse_id"] = str(warehouse_id)
    data = client.request("GET", "/reports/inventory-discrepancy/dashboard", params=params)
    render_json(data)


group.add_typer(discrepancy_app)

# --- Transaction COGS ---

COGS_COLUMNS = [
    ("ID", "id", "dim"),
    ("Date", "date", ""),
    ("Product", "product_name", ""),
    ("SKU", "sku", "cyan"),
    ("Qty", "quantity", ""),
    ("COGS", "cogs", "green"),
    ("Order #", "order_number", ""),
]


@group.command("cogs")
def transaction_cogs(
    filter: FilterOption = None,
    sort: SortOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """Transaction-level cost of goods sold data."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, page=page, per_page=per_page)
    resp = client.list("/reports/transaction-cogs", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=COGS_COLUMNS, pagination=resp.pagination, fmt=fmt)


# --- EDI ---

edi_app = typer.Typer(name="edi", help="EDI document reports")

EDI_COLUMNS = [
    ("ID", "id", "dim"),
    ("Type", "type", ""),
    ("Direction", "direction", ""),
    ("Status", "status", ""),
    ("Partner", "partner", ""),
    ("Date", "created_at", ""),
]


@edi_app.command("list")
def edi_list(
    filter: FilterOption = None,
    sort: SortOption = None,
    page: PageOption = 1,
    per_page: PerPageOption = 50,
    format: FormatOption = None,
) -> None:
    """Paginated list of EDI documents."""
    client = get_client()
    qp = QueryParams.from_cli_args(raw_filters=filter, sort=sort, page=page, per_page=per_page)
    resp = client.list("/reports/edi", params=qp)
    fmt = resolve_format(format)
    render(resp.data, columns=EDI_COLUMNS, pagination=resp.pagination, fmt=fmt)


@edi_app.command("summary")
def edi_summary(
    format: FormatOption = None,
) -> None:
    """EDI aggregate summary with counts by status and type."""
    client = get_client()
    data = client.request("GET", "/reports/edi/summary")
    render_json(data)


@edi_app.command("export")
def edi_export(
    filter: FilterOption = None,
) -> None:
    """Export EDI documents as CSV (max 50,000 rows)."""
    client = get_client()
    params: dict[str, str] = {}
    if filter:
        qp = QueryParams.from_cli_args(raw_filters=filter)
        params = qp.filters
    data = client.request("GET", "/reports/edi/export", params=params)
    render_json(data)


group.add_typer(edi_app)
