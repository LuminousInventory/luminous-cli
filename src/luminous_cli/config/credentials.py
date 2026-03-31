"""Credential storage with keyring -> file fallback."""

from __future__ import annotations

import os
import stat
from pathlib import Path

from platformdirs import user_config_dir

SERVICE_NAME = "luminous-cli"
_CREDS_DIR = Path(user_config_dir("luminous", ensure_exists=True)) / "credentials"
_keyring_available: bool | None = None


def _has_keyring() -> bool:
    """Check if system keyring is usable (cached)."""
    global _keyring_available
    if _keyring_available is None:
        try:
            import keyring
            from keyring.backends.fail import Keyring as FailKeyring

            _keyring_available = not isinstance(keyring.get_keyring(), FailKeyring)
        except Exception:
            _keyring_available = False
    return _keyring_available


def _cred_path(profile: str) -> Path:
    """Path to a file-based credential for a profile."""
    return _CREDS_DIR / f"{profile}.key"


def store_api_key(profile: str, api_key: str) -> None:
    if _has_keyring():
        import keyring

        keyring.set_password(SERVICE_NAME, profile, api_key)
    else:
        _creds_dir_ensure()
        path = _cred_path(profile)
        path.write_text(api_key)
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600


def get_api_key(profile: str) -> str | None:
    if _has_keyring():
        import keyring

        try:
            return keyring.get_password(SERVICE_NAME, profile)
        except Exception:
            return None
    else:
        path = _cred_path(profile)
        if path.exists():
            return path.read_text().strip()
        return None


def delete_api_key(profile: str) -> None:
    if _has_keyring():
        import keyring

        try:
            keyring.delete_password(SERVICE_NAME, profile)
        except Exception:
            pass
    else:
        path = _cred_path(profile)
        if path.exists():
            path.unlink()


def _creds_dir_ensure() -> None:
    _CREDS_DIR.mkdir(parents=True, exist_ok=True)
    _CREDS_DIR.chmod(stat.S_IRWXU)  # 700
