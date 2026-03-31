"""Input resolver: merges JSON/file/stdin/flags into a single payload."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import orjson
import typer
from rich.console import Console

stderr = Console(stderr=True)

# Fields that the API calculates — must not be sent in requests
READ_ONLY_FIELDS = frozenset({
    "order_cost",
    "total_cost",
    "total_paid",
    "total_due",
    "line_total",
    "created_at",
    "updated_at",
    "id",
})

# Array fields that trigger replacement warnings on update
ARRAY_FIELDS = frozenset({
    "items",
    "payments",
    "extra_costs",
    "variants",
    "kit_items",
    "shipping_addresses",
})


def parse_kv_item(raw: str) -> dict[str, Any]:
    """Parse 'key=value,key=value' into a dict, coercing numeric values.

    Example: "sku=W-001,quantity=10,unit_price=12.50"
    -> {"sku": "W-001", "quantity": 10, "unit_price": 12.50}
    """
    result: dict[str, Any] = {}
    for pair in raw.split(","):
        key, _, value = pair.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        # Try to coerce to numeric
        result[key] = _coerce_value(value)
    return result


def _coerce_value(value: str) -> Any:
    """Coerce a string value to int, float, bool, or leave as string."""
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def resolve_input(
    *,
    json_input: str | None = None,
    file_input: str | None = None,
    flags: dict[str, Any] | None = None,
    items: list[str] | None = None,
    tags: list[str] | None = None,
    extra_costs: list[str] | None = None,
    is_update: bool = False,
    skip_confirm: bool = False,
) -> dict[str, Any]:
    """Build a request payload from all input sources.

    Resolution order:
    1. Load base from --file or --json (mutually exclusive)
    2. Overlay flag values (flags win for top-level keys)
    3. Parse --item values into items[] array
    4. Parse --tag values into tags[] array
    5. Parse --extra-cost values into extra_costs[] array
    6. Strip read-only fields with warning
    7. On update: warn about array replacement
    """
    # Step 1: Base payload
    payload = _load_base_payload(json_input=json_input, file_input=file_input)

    # Step 2: Overlay flags
    if flags:
        for key, value in flags.items():
            if value is not None:
                payload[key] = value

    # Step 3: Repeatable --item
    if items:
        payload["items"] = [parse_kv_item(item) for item in items]

    # Step 4: Repeatable --tag
    if tags:
        payload["tags"] = list(tags)

    # Step 5: Repeatable --extra-cost
    if extra_costs:
        payload["extra_costs"] = [parse_kv_item(ec) for ec in extra_costs]

    # Step 6: Strip read-only fields
    stripped = [k for k in payload if k in READ_ONLY_FIELDS]
    for k in stripped:
        del payload[k]
    if stripped:
        stderr.print(f"[dim]Stripped read-only fields: {', '.join(stripped)}[/dim]")

    # Step 7: Array replacement warning on updates
    if is_update and not skip_confirm:
        present_arrays = [k for k in ARRAY_FIELDS if k in payload]
        if present_arrays:
            stderr.print(
                f"[yellow]Warning: Providing {', '.join(present_arrays)} in update "
                f"will REPLACE all existing entries.[/yellow]"
            )
            if not typer.confirm("Proceed?", default=False):
                raise typer.Abort()

    return payload


def _load_base_payload(
    *,
    json_input: str | None = None,
    file_input: str | None = None,
) -> dict[str, Any]:
    """Load base payload from --json or --file."""
    if json_input and file_input:
        stderr.print("[red]Cannot use both --json and --file[/red]")
        raise typer.Exit(code=1)

    if file_input:
        path = Path(file_input)
        if not path.exists():
            stderr.print(f"[red]File not found: {file_input}[/red]")
            raise typer.Exit(code=1)
        return orjson.loads(path.read_bytes())

    if json_input:
        if json_input == "-":
            return orjson.loads(sys.stdin.buffer.read())
        return orjson.loads(json_input)

    return {}
