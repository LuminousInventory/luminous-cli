"""HTTP client for the Luminous API."""

from __future__ import annotations

import time
from typing import Any

import httpx
import orjson

from luminous_cli.client.auth import resolve_auth
from luminous_cli.client.query import QueryParams
from luminous_cli.errors import (
    AuthenticationError,
    ConflictError,
    LuminousError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

_client: LuminousClient | None = None


def get_client() -> LuminousClient:
    """Lazy singleton. Created once per CLI invocation.

    Reads flag overrides from the active Click/Typer context if available.
    """
    global _client
    if _client is None:
        import click

        # Pull overrides from Typer context (set in cli/__init__.py callback)
        ctx = click.get_current_context(silent=True)
        obj = (ctx.find_root().obj or {}) if ctx else {}

        auth = resolve_auth(
            flag_company=obj.get("flag_company"),
            flag_api_key=obj.get("flag_api_key"),
            flag_profile=obj.get("flag_profile"),
        )
        _client = LuminousClient(base_url=auth.base_url, api_key=auth.api_key)
    return _client


def reset_client() -> None:
    """Reset the singleton (for testing)."""
    global _client
    if _client is not None:
        _client.close()
    _client = None


class APIResponse:
    """Wrapper for list endpoint responses."""

    def __init__(self, data: list[dict[str, Any]], pagination: dict[str, Any] | None = None):
        self.data = data
        self.pagination = pagination


class LuminousClient:
    MAX_RETRIES = 3
    RETRY_BACKOFF_BASE = 1.0

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self._http = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def close(self) -> None:
        self._http.close()

    # -- Public interface --------------------------------------------------

    def list(self, path: str, *, params: QueryParams | None = None) -> APIResponse:
        """GET a list endpoint with optional filters/sort/pagination."""
        raw_params = params.to_dict() if params else {}
        body = self._request("GET", path, params=raw_params)
        return APIResponse(
            data=body.get("data", []),
            # API uses "meta" for pagination, not "pagination"
            pagination=body.get("meta") or body.get("pagination"),
        )

    def get(self, path: str, resource_id: int | str) -> dict[str, Any]:
        """GET a single resource by ID."""
        body = self._request("GET", f"{path}/{resource_id}")
        return body.get("data", body)

    def create(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """POST to create a resource."""
        body = self._request("POST", path, json_body=payload)
        return body.get("data", body)

    def update(
        self, path: str, resource_id: int | str, payload: dict[str, Any], *, method: str = "POST"
    ) -> dict[str, Any]:
        """Update a resource. Method varies by endpoint (POST or PUT)."""
        body = self._request(method, f"{path}/{resource_id}", json_body=payload)
        return body.get("data", body)

    def upsert(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """PATCH to upsert a resource."""
        body = self._request("PATCH", path, json_body=payload)
        return body.get("data", body)

    def delete(self, path: str, resource_id: int | str) -> dict[str, Any] | None:
        """DELETE a resource."""
        body = self._request("DELETE", f"{path}/{resource_id}")
        return body

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Raw request for custom endpoints."""
        return self._request(method, path, params=params, json_body=json_body)

    # -- Internals ---------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        if params:
            kwargs["params"] = params
        if json_body is not None:
            kwargs["content"] = orjson.dumps(json_body)

        last_exc: Exception | None = None
        for attempt in range(self.MAX_RETRIES):
            try:
                resp = self._http.request(method, path, **kwargs)
                self._check_status(resp)
                if not resp.content:
                    return {}
                return orjson.loads(resp.content)
            except RateLimitError as exc:
                last_exc = exc
                wait = exc.retry_after or (self.RETRY_BACKOFF_BASE * (2**attempt))
                time.sleep(wait)
            except httpx.ConnectError as exc:
                raise NetworkError(f"Could not connect: {exc}") from exc
            except httpx.TimeoutException as exc:
                raise NetworkError(f"Request timed out: {exc}") from exc

        raise last_exc  # type: ignore[misc]

    def _check_status(self, response: httpx.Response) -> None:
        if response.is_success:
            return

        status = response.status_code
        body: dict = {}
        if response.content:
            try:
                body = orjson.loads(response.content)
            except orjson.JSONDecodeError:
                pass

        msg = body.get("message", response.reason_phrase or f"HTTP {status}")

        match status:
            case 401:
                raise AuthenticationError(msg)
            case 404:
                raise NotFoundError(msg)
            case 409:
                raise ConflictError(msg)
            case 422:
                raise ValidationError.from_response(body)
            case 429:
                raise RateLimitError(
                    retry_after=float(response.headers.get("Retry-After", 1))
                )
            case _:
                raise LuminousError(f"{status}: {msg}")
