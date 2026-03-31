"""Config management commands."""

from __future__ import annotations

import typer
from rich.console import Console

from luminous_cli.config.files import CONFIG_FILE, load_config, save_config

config_app = typer.Typer(name="config", help="Manage CLI configuration")
stderr = Console(stderr=True)


@config_app.command("get")
def config_get(
    key: str = typer.Argument(..., help="Config key (e.g., default_format)"),
) -> None:
    """Read a config value."""
    config = load_config()
    profile = config.profiles.get(config.default_profile)
    if not profile:
        stderr.print("[yellow]No active profile.[/yellow]")
        raise typer.Exit(code=1)

    value = getattr(profile, key, None)
    if value is None:
        stderr.print(f"[yellow]Unknown key: {key}[/yellow]")
        raise typer.Exit(code=1)

    typer.echo(value)


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key"),
    value: str = typer.Argument(..., help="Value to set"),
) -> None:
    """Set a config value for the active profile."""
    config = load_config()
    profile_name = config.default_profile
    profile = config.profiles.get(profile_name)
    if not profile:
        stderr.print("[yellow]No active profile. Run 'luminous auth login' first.[/yellow]")
        raise typer.Exit(code=1)

    if key == "default_format":
        if value not in ("table", "json", "ndjson", "csv"):
            stderr.print(f"[red]Invalid format: {value}. Use table|json|ndjson|csv[/red]")
            raise typer.Exit(code=1)
        profile.default_format = value
    elif key == "per_page":
        profile.per_page = int(value)
    elif key == "company":
        profile.company = value
    else:
        stderr.print(f"[yellow]Unknown key: {key}. Valid: default_format, per_page, company[/yellow]")
        raise typer.Exit(code=1)

    save_config(config)
    stderr.print(f"[green]Set {key}={value} for profile '{profile_name}'[/green]")


@config_app.command("list")
def config_list() -> None:
    """Show all configuration."""
    config = load_config()
    stderr.print(f"Config file: [dim]{CONFIG_FILE}[/dim]")
    stderr.print(f"Active profile: [cyan]{config.default_profile}[/cyan]")
    stderr.print()

    if not config.profiles:
        stderr.print("[yellow]No profiles configured.[/yellow]")
        return

    for name, profile in config.profiles.items():
        marker = " *" if name == config.default_profile else ""
        stderr.print(f"[cyan]{name}[/cyan]{marker}")
        stderr.print(f"  company: {profile.company}")
        stderr.print(f"  format:  {profile.default_format}")
        stderr.print(f"  per_page: {profile.per_page}")
