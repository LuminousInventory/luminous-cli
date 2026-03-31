"""Configuration data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Profile:
    name: str
    company: str
    default_format: str = "table"
    per_page: int = 50


@dataclass
class AppConfig:
    default_profile: str = "default"
    profiles: dict[str, Profile] = field(default_factory=dict)


@dataclass
class ResolvedAuth:
    """Fully resolved credentials for a request context."""

    company: str
    api_key: str

    @property
    def base_url(self) -> str:
        return f"https://{self.company}.api.joinluminous.com/external/api/v1"
