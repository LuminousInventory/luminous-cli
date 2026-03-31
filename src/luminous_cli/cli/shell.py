"""Interactive REPL shell for the Luminous CLI."""

from __future__ import annotations

import shlex
import sys

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML
from platformdirs import user_data_dir
from pathlib import Path
from rich.console import Console

from luminous_cli.client.http import reset_client
from luminous_cli.errors import LuminousError

stderr = Console(stderr=True)


def _collect_commands(group: click.Group, prefix: str = "") -> dict[str, click.Command]:
    """Recursively collect all commands with their full paths."""
    commands: dict[str, click.Command] = {}
    for name, cmd in (group.commands or {}).items():
        full = f"{prefix} {name}".strip() if prefix else name
        commands[full] = cmd
        if isinstance(cmd, click.Group):
            commands.update(_collect_commands(cmd, full))
    return commands


class CommandCompleter(Completer):
    """Auto-complete command names, subcommands, and flags."""

    def __init__(self, click_app: click.Group) -> None:
        self._app = click_app
        self._all_commands = _collect_commands(click_app)
        # Build a tree for incremental completion
        self._command_names = sorted(self._all_commands.keys())

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = text.split()

        # If text ends with a space, we're completing the NEXT word
        completing_partial = not text.endswith(" ") and len(words) > 0

        if completing_partial:
            partial = words[-1]
            prefix_words = words[:-1]
        else:
            partial = ""
            prefix_words = words

        prefix = " ".join(prefix_words)

        # Check if current prefix resolves to a command with flags
        resolved_cmd = self._all_commands.get(prefix)
        if resolved_cmd and partial.startswith("-"):
            # Complete flags
            for param in resolved_cmd.params:
                for opt in param.opts:
                    if opt.startswith(partial):
                        help_text = param.help or ""
                        yield Completion(opt, start_position=-len(partial), display_meta=help_text)
            return

        # Complete command/subcommand names
        search_prefix = f"{prefix} {partial}".strip() if prefix else partial
        for cmd_name in self._command_names:
            if cmd_name.startswith(search_prefix):
                # Only show the next segment
                remaining = cmd_name[len(prefix):].strip() if prefix else cmd_name
                next_word = remaining.split()[0] if remaining else ""
                if next_word and next_word.startswith(partial):
                    # Avoid duplicate completions
                    yield Completion(
                        next_word,
                        start_position=-len(partial),
                    )


def _get_prompt(profile_name: str) -> HTML:
    return HTML(f"<ansigreen>luminous</ansigreen> <ansigray>({profile_name})</ansigray> <ansiblue>></ansiblue> ")


def run_shell(click_app: click.Group) -> None:
    """Launch the interactive REPL."""
    from luminous_cli.config.files import load_config

    config = load_config()
    profile_name = config.default_profile
    profile = config.profiles.get(profile_name)
    company = profile.company if profile else "not configured"

    # History file
    history_dir = Path(user_data_dir("luminous", ensure_exists=True))
    history_file = history_dir / "shell_history"

    session: PromptSession = PromptSession(
        history=FileHistory(str(history_file)),
        completer=CommandCompleter(click_app),
        complete_while_typing=True,
    )

    stderr.print(f"[bold]Luminous CLI[/bold] — interactive mode")
    stderr.print(f"[dim]Connected to: {company}[/dim]")
    stderr.print(f"[dim]Type a command, 'help' for commands, or 'exit' to quit.[/dim]")
    stderr.print()

    while True:
        try:
            text = session.prompt(_get_prompt(profile_name)).strip()
        except (EOFError, KeyboardInterrupt):
            stderr.print("\n[dim]Goodbye.[/dim]")
            break

        if not text:
            continue

        if text in ("exit", "quit", "q"):
            stderr.print("[dim]Goodbye.[/dim]")
            break

        if text == "help":
            _print_help(click_app)
            continue

        if text == "clear":
            click.clear()
            continue

        # Parse and run the command through Click
        try:
            args = shlex.split(text)
        except ValueError as e:
            stderr.print(f"[red]Parse error: {e}[/red]")
            continue

        try:
            # Reset client between commands so context is fresh
            reset_client()
            # standalone_mode=False prevents SystemExit on --help or errors
            click_app(args, standalone_mode=False)
        except SystemExit:
            pass  # --help or typer.Exit triggers this
        except LuminousError as exc:
            from luminous_cli.errors import handle_error
            # Print error but don't exit the shell
            from rich.panel import Panel
            stderr.print(Panel(exc.render(), title="Error", border_style="red"))
        except click.exceptions.UsageError as exc:
            stderr.print(f"[red]Usage error: {exc.format_message()}[/red]")
        except click.Abort:
            stderr.print("[dim]Aborted.[/dim]")
        except Exception as exc:
            stderr.print(f"[red]Error: {exc}[/red]")

        stderr.print()  # Blank line between commands


def _print_help(click_app: click.Group) -> None:
    """Print available commands in a compact format."""
    stderr.print("[bold]Available commands:[/bold]")
    stderr.print()
    for name, cmd in sorted(click_app.commands.items()):
        help_text = cmd.help or cmd.short_help or ""
        if isinstance(cmd, click.Group):
            subcmds = ", ".join(sorted(cmd.commands.keys()))
            stderr.print(f"  [cyan]{name:<20}[/cyan] {help_text}")
            stderr.print(f"  [dim]{'':<20} subcommands: {subcmds}[/dim]")
        else:
            stderr.print(f"  [cyan]{name:<20}[/cyan] {help_text}")
    stderr.print()
    stderr.print("[dim]  help                 Show this help[/dim]")
    stderr.print("[dim]  clear                Clear the screen[/dim]")
    stderr.print("[dim]  exit                 Exit the shell[/dim]")
