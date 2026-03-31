"""Shared Typer options used across resource commands."""

from __future__ import annotations

from typing import Annotated, Optional

import typer

FilterOption = Annotated[
    Optional[list[str]],
    typer.Option(
        "--filter",
        help='Filter: "field[op]=value" or "field=value". Repeatable.',
    ),
]

SortOption = Annotated[
    Optional[str],
    typer.Option("--sort", help="Sort: field:asc or field:desc"),
]

PageOption = Annotated[
    int,
    typer.Option("--page", help="Page number", min=1),
]

PerPageOption = Annotated[
    int,
    typer.Option("--per-page", help="Results per page (max 100)", min=1, max=100),
]

FormatOption = Annotated[
    Optional[str],
    typer.Option("--format", "-f", help="Output: table|json|ndjson|csv"),
]

JsonOption = Annotated[
    Optional[str],
    typer.Option("--json", help="JSON payload string, or '-' for stdin"),
]

FileOption = Annotated[
    Optional[str],
    typer.Option("--file", help="Path to JSON file"),
]

YesOption = Annotated[
    bool,
    typer.Option("--yes", "-y", help="Skip confirmation prompts"),
]
