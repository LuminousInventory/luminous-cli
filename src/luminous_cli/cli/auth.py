"""Authentication commands: login, logout, status, switch."""

from __future__ import annotations

import httpx
import typer
from rich.console import Console
from rich.prompt import Prompt

from luminous_cli.config.credentials import delete_api_key, get_api_key, store_api_key
from luminous_cli.config.files import load_config, save_config
from luminous_cli.config.models import Profile

auth_app = typer.Typer(name="auth", help="Manage authentication")
stderr = Console(stderr=True)


@auth_app.command()
def login(
    company: str = typer.Option("", help="Company subdomain"),
    profile: str = typer.Option("default", help="Profile name to save as"),
) -> None:
    """Authenticate with the Luminous API."""
    if not company:
        company = Prompt.ask("Company subdomain")

    api_key = Prompt.ask("API key", password=True)

    # Validate credentials
    stderr.print(f"[dim]Validating credentials for {company}...[/dim]")
    try:
        resp = httpx.get(
            f"https://{company}.api.joinluminous.com/external/api/v1/warehouses",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"per_page": "1"},
            timeout=10,
        )
        if resp.status_code == 401:
            stderr.print("[red]Authentication failed. Check your company slug and API key.[/red]")
            raise typer.Exit(code=1)
        if resp.status_code >= 400:
            stderr.print(f"[red]Unexpected response: HTTP {resp.status_code}[/red]")
            raise typer.Exit(code=1)
    except httpx.ConnectError:
        stderr.print("[red]Could not connect. Check your company subdomain.[/red]")
        raise typer.Exit(code=1)

    # Store credentials
    store_api_key(profile, api_key)
    config = load_config()
    config.profiles[profile] = Profile(name=profile, company=company)
    config.default_profile = profile
    save_config(config)

    stderr.print(f"[green]Authenticated as {company} (profile: {profile})[/green]")


@auth_app.command()
def logout(
    profile: str = typer.Option("", help="Profile to remove (default: current)"),
    all_profiles: bool = typer.Option(False, "--all", help="Remove all profiles"),
) -> None:
    """Remove stored credentials."""
    config = load_config()

    if all_profiles:
        for name in list(config.profiles.keys()):
            delete_api_key(name)
        config.profiles.clear()
        config.default_profile = "default"
        save_config(config)
        stderr.print("[green]All profiles removed.[/green]")
        return

    target = profile or config.default_profile
    if target in config.profiles:
        del config.profiles[target]
    delete_api_key(target)

    # Switch to next available profile
    if config.default_profile == target:
        config.default_profile = next(iter(config.profiles), "default")
    save_config(config)
    stderr.print(f"[green]Profile '{target}' removed.[/green]")


@auth_app.command()
def status() -> None:
    """Show current authentication status."""
    config = load_config()
    profile_name = config.default_profile
    profile = config.profiles.get(profile_name)

    if not profile:
        stderr.print("[yellow]No profile configured. Run 'luminous auth login'.[/yellow]")
        raise typer.Exit(code=1)

    key = get_api_key(profile_name)
    has_key = bool(key)

    stderr.print(f"Profile:  [cyan]{profile_name}[/cyan]")
    stderr.print(f"Company:  [cyan]{profile.company}[/cyan]")
    if has_key and key:
        masked = key[:4] + "..." + key[-4:] if len(key) > 8 else "****"
        stderr.print(f"API Key:  [green]{masked}[/green]")
    else:
        stderr.print("API Key:  [red]not set[/red]")


@auth_app.command()
def switch(
    profile: str = typer.Argument(..., help="Profile name to switch to"),
) -> None:
    """Switch the active profile."""
    config = load_config()
    if profile not in config.profiles:
        available = ", ".join(config.profiles.keys()) or "(none)"
        stderr.print(f"[red]Profile '{profile}' not found. Available: {available}[/red]")
        raise typer.Exit(code=1)

    config.default_profile = profile
    save_config(config)
    stderr.print(f"[green]Switched to profile '{profile}' ({config.profiles[profile].company})[/green]")
