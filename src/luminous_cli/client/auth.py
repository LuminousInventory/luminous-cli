"""Credential resolution: flag > env > keyring."""

from __future__ import annotations

import os

from luminous_cli.config.credentials import get_api_key
from luminous_cli.config.files import load_config
from luminous_cli.config.models import ResolvedAuth
from luminous_cli.errors import AuthenticationError


def resolve_auth(
    *,
    flag_company: str | None = None,
    flag_api_key: str | None = None,
    flag_profile: str | None = None,
) -> ResolvedAuth:
    """Resolve credentials from flags, env vars, or stored config/keyring."""
    config = load_config()

    # Determine which profile to use
    profile_name = flag_profile or config.default_profile
    profile = config.profiles.get(profile_name)

    # Resolve company
    company = (
        flag_company
        or os.environ.get("LUMINOUS_COMPANY")
        or (profile.company if profile else None)
    )

    # Resolve API key
    api_key = (
        flag_api_key
        or os.environ.get("LUMINOUS_API_KEY")
        or (get_api_key(profile_name) if profile_name else None)
    )

    if not company or not api_key:
        raise AuthenticationError(
            "No credentials found. Run 'luminous auth login' or set "
            "LUMINOUS_COMPANY and LUMINOUS_API_KEY environment variables."
        )

    return ResolvedAuth(company=company, api_key=api_key)
