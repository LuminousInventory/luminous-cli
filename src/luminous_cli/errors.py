"""Exception hierarchy and exit codes for the Luminous CLI."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

stderr = Console(stderr=True)

# Exit codes (BSD sysexits.h inspired)
EXIT_OK = 0
EXIT_API_ERROR = 1
EXIT_USAGE = 64
EXIT_VALIDATION = 65
EXIT_NOT_FOUND = 69
EXIT_CONFLICT = 70
EXIT_RATE_LIMIT = 75
EXIT_NETWORK = 76
EXIT_AUTH = 77


class LuminousError(Exception):
    """Base for all CLI errors."""

    exit_code: int = EXIT_API_ERROR

    def render(self) -> str:
        return str(self)


class AuthenticationError(LuminousError):
    exit_code = EXIT_AUTH


class NotFoundError(LuminousError):
    exit_code = EXIT_NOT_FOUND


class ConflictError(LuminousError):
    exit_code = EXIT_CONFLICT


class RateLimitError(LuminousError):
    exit_code = EXIT_RATE_LIMIT

    def __init__(self, retry_after: float | None = None):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after}s.")


@dataclass
class FieldError:
    path: str
    messages: list[str]


class ValidationError(LuminousError):
    exit_code = EXIT_VALIDATION

    def __init__(self, message: str, field_errors: list[FieldError] | None = None):
        self.field_errors = field_errors or []
        super().__init__(message)

    @classmethod
    def from_response(cls, body: dict) -> ValidationError:
        msg = body.get("message", "Validation failed")
        errors: list[FieldError] = []
        for path, messages in body.get("errors", {}).items():
            if isinstance(messages, list):
                errors.append(FieldError(path=path, messages=messages))
            else:
                errors.append(FieldError(path=path, messages=[str(messages)]))
        return cls(msg, errors)

    def render(self) -> str:
        if not self.field_errors:
            return str(self)
        table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
        table.add_column("Field", style="yellow")
        table.add_column("Error")
        for fe in self.field_errors:
            for msg in fe.messages:
                table.add_row(fe.path, msg)
        console = Console(stderr=True, file=sys.stderr)
        with console.capture() as capture:
            console.print(table)
        return f"{self}\n{capture.get()}"


class NetworkError(LuminousError):
    exit_code = EXIT_NETWORK


def handle_error(exc: LuminousError) -> None:
    """Render an error to stderr and exit."""
    stderr.print(Panel(exc.render(), title="Error", border_style="red"))
    sys.exit(exc.exit_code)
