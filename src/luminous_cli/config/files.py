"""TOML config file management."""

from __future__ import annotations

import sys
from pathlib import Path

import tomli_w
from platformdirs import user_config_dir

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from luminous_cli.config.models import AppConfig, Profile

CONFIG_DIR = Path(user_config_dir("luminous", ensure_exists=True))
CONFIG_FILE = CONFIG_DIR / "config.toml"


def load_config() -> AppConfig:
    if not CONFIG_FILE.exists():
        return AppConfig()

    with open(CONFIG_FILE, "rb") as f:
        data = tomllib.load(f)

    profiles: dict[str, Profile] = {}
    for name, prof_data in data.get("profiles", {}).items():
        profiles[name] = Profile(
            name=name,
            company=prof_data.get("company", ""),
            default_format=prof_data.get("default_format", "table"),
            per_page=prof_data.get("per_page", 50),
        )

    return AppConfig(
        default_profile=data.get("default_profile", "default"),
        profiles=profiles,
    )


def save_config(config: AppConfig) -> None:
    data: dict = {"default_profile": config.default_profile, "profiles": {}}
    for name, profile in config.profiles.items():
        data["profiles"][name] = {
            "company": profile.company,
            "default_format": profile.default_format,
            "per_page": profile.per_page,
        }

    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(data, f)
