"""Main CLI application entry point."""

from __future__ import annotations

import sys
from typing import Optional

import httpx
import typer

from luminous_cli import __version__
from luminous_cli.errors import EXIT_NETWORK, LuminousError, handle_error, stderr

app = typer.Typer(
    name="luminous",
    help="CLI for the Luminous API",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"luminous-cli {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-V", callback=_version_callback, is_eager=True, help="Show version"
    ),
    company: Optional[str] = typer.Option(None, "--company", envvar="LUMINOUS_COMPANY", help="Company subdomain"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="LUMINOUS_API_KEY", help="API key"),
    profile: Optional[str] = typer.Option(None, "--profile", help="Named profile"),
) -> None:
    """Luminous CLI - manage your Luminous data from the terminal."""
    ctx.ensure_object(dict)
    ctx.obj["flag_company"] = company
    ctx.obj["flag_api_key"] = api_key
    ctx.obj["flag_profile"] = profile


# Register sub-apps
from luminous_cli.cli.auth import auth_app  # noqa: E402
from luminous_cli.cli.config_cmd import config_app  # noqa: E402
from luminous_cli.cli.resources import register_all  # noqa: E402

app.add_typer(auth_app)
app.add_typer(config_app)
register_all(app)


def cli() -> None:
    """Entry point with global exception handling."""
    try:
        app()
    except LuminousError as exc:
        handle_error(exc)
    except httpx.ConnectError:
        stderr.print("[red]Error: Could not connect. Check your network and company slug.[/red]")
        sys.exit(EXIT_NETWORK)
    except httpx.TimeoutException:
        stderr.print("[red]Error: Request timed out.[/red]")
        sys.exit(EXIT_NETWORK)
    except KeyboardInterrupt:
        sys.exit(130)
