"""Resource factory: generates CRUD command groups from ResourceSpec."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

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


@dataclass
class ResourceSpec:
    """Declarative specification for a REST resource."""

    name: str  # plural, kebab-case: "products", "sales-orders"
    singular: str  # "product", "sales order"
    api_path: str  # "/products", "/sales-orders"
    columns: list[tuple[str, str, str]]  # [(header, dot_path, style), ...]
    capabilities: set[str] = field(
        default_factory=lambda: {"list", "get", "create", "update", "delete"}
    )
    update_method: str = "POST"  # Some resources use PUT
    read_only_fields: list[str] = field(default_factory=list)
    # Optional hooks
    pre_create: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    pre_update: Callable[[dict[str, Any]], dict[str, Any]] | None = None


def make_resource_group(spec: ResourceSpec) -> typer.Typer:
    """Generate a Typer command group with CRUD commands from a ResourceSpec."""
    group = typer.Typer(name=spec.name, help=f"Manage {spec.name}")

    if "list" in spec.capabilities:

        @group.command("list")
        def list_cmd(
            filter: FilterOption = None,
            sort: SortOption = None,
            page: PageOption = 1,
            per_page: PerPageOption = 50,
            format: FormatOption = None,
            all_pages: bool = typer.Option(False, "--all", help="Fetch all pages"),
        ) -> None:
            client = get_client()
            fmt = resolve_format(format)

            if all_pages:
                _fetch_all_pages(client, spec, filter, sort, per_page, fmt)
                return

            qp = QueryParams.from_cli_args(
                raw_filters=filter,
                sort=sort,
                page=page,
                per_page=per_page,
            )
            resp = client.list(spec.api_path, params=qp)
            render(resp.data, columns=spec.columns, pagination=resp.pagination, fmt=fmt)

    if "get" in spec.capabilities:

        @group.command("get")
        def get_cmd(
            resource_id: int = typer.Argument(..., help=f"{spec.singular} ID"),
            format: FormatOption = None,
        ) -> None:
            client = get_client()
            data = client.get(spec.api_path, resource_id)
            fmt = resolve_format(format)
            render(data, columns=spec.columns, fmt=fmt)

    if "create" in spec.capabilities:

        @group.command("create")
        def create_cmd(
            json_input: JsonOption = None,
            file: FileOption = None,
            item: Optional[list[str]] = typer.Option(None, "--item", help="Item: key=val,key=val. Repeatable."),
            tag: Optional[list[str]] = typer.Option(None, "--tag", help="Tag string. Repeatable."),
            extra_cost: Optional[list[str]] = typer.Option(
                None, "--extra-cost", help="Extra cost: name=X,quantity=N,unit_price=N. Repeatable."
            ),
            format: FormatOption = None,
        ) -> None:
            payload = resolve_input(
                json_input=json_input,
                file_input=file,
                items=item,
                tags=tag,
                extra_costs=extra_cost,
            )
            if not payload:
                typer.echo(
                    f"Provide input via --json, --file, or --item flags.\n"
                    f"Example: luminous {spec.name} create --json '{{...}}'",
                    err=True,
                )
                raise typer.Exit(code=1)

            if spec.pre_create:
                payload = spec.pre_create(payload)

            client = get_client()
            data = client.create(spec.api_path, payload)
            fmt = resolve_format(format)
            render(data, columns=spec.columns, fmt=fmt)

    if "update" in spec.capabilities:

        @group.command("update")
        def update_cmd(
            resource_id: int = typer.Argument(..., help=f"{spec.singular} ID"),
            json_input: JsonOption = None,
            file: FileOption = None,
            item: Optional[list[str]] = typer.Option(None, "--item", help="Item: key=val,key=val. Repeatable."),
            tag: Optional[list[str]] = typer.Option(None, "--tag", help="Tag string. Repeatable."),
            extra_cost: Optional[list[str]] = typer.Option(
                None, "--extra-cost", help="Extra cost: name=X,quantity=N,unit_price=N. Repeatable."
            ),
            yes: YesOption = False,
            format: FormatOption = None,
        ) -> None:
            payload = resolve_input(
                json_input=json_input,
                file_input=file,
                items=item,
                tags=tag,
                extra_costs=extra_cost,
                is_update=True,
                skip_confirm=yes,
            )
            if not payload:
                typer.echo("Nothing to update. Provide --json, --file, or flags.", err=True)
                raise typer.Exit(code=1)

            if spec.pre_update:
                payload = spec.pre_update(payload)

            client = get_client()
            data = client.update(
                spec.api_path, resource_id, payload, method=spec.update_method
            )
            fmt = resolve_format(format)
            render(data, columns=spec.columns, fmt=fmt)

    if "upsert" in spec.capabilities:

        @group.command("upsert")
        def upsert_cmd(
            json_input: JsonOption = None,
            file: FileOption = None,
            format: FormatOption = None,
        ) -> None:
            payload = resolve_input(json_input=json_input, file_input=file)
            if not payload:
                typer.echo("Provide input via --json or --file.", err=True)
                raise typer.Exit(code=1)

            client = get_client()
            data = client.upsert(spec.api_path, payload)
            fmt = resolve_format(format)
            render(data, columns=spec.columns, fmt=fmt)

    if "delete" in spec.capabilities:

        @group.command("delete")
        def delete_cmd(
            resource_id: int = typer.Argument(..., help=f"{spec.singular} ID"),
            yes: YesOption = False,
        ) -> None:
            if not yes:
                typer.confirm(f"Delete {spec.singular} {resource_id}?", abort=True)
            client = get_client()
            client.delete(spec.api_path, resource_id)
            typer.echo(f"Deleted {spec.singular} {resource_id}")

    return group


def _fetch_all_pages(
    client: Any,
    spec: ResourceSpec,
    raw_filters: list[str] | None,
    sort: str | None,
    per_page: int,
    fmt: str,
) -> None:
    """Iterate all pages and render combined results."""
    import sys

    from rich.console import Console

    stderr = Console(stderr=True)
    all_data: list[dict[str, Any]] = []
    page = 1

    while True:
        qp = QueryParams.from_cli_args(
            raw_filters=raw_filters,
            sort=sort,
            page=page,
            per_page=per_page,
        )
        resp = client.list(spec.api_path, params=qp)
        all_data.extend(resp.data)

        last_page = resp.pagination.get("last_page", 1) if resp.pagination else 1
        total = resp.pagination.get("total", len(all_data)) if resp.pagination else len(all_data)
        stderr.print(f"[dim]Fetched page {page}/{last_page} ({len(all_data)}/{total} records)[/dim]")

        if page >= last_page:
            break
        page += 1

    render(all_data, columns=spec.columns, fmt=fmt)
