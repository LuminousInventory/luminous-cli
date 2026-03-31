"""Filter, sort, and pagination query parameter builder."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

VALID_OPERATORS = frozenset({
    "eq", "neq", "gt", "gte", "lt", "lte",
    "set", "notset", "contains", "notcontains",
    "in", "notin",
})

# Matches "field[operator]=value" or "field[operator]" (for set/notset)
_FILTER_RE = re.compile(r"^([a-zA-Z0-9_.]+)\[([a-z]+)\](?:=(.*))?$")
# Matches "field=value" (shorthand for eq)
_SHORTHAND_RE = re.compile(r"^([a-zA-Z0-9_.]+)=(.+)$")


@dataclass
class QueryParams:
    filters: dict[str, str] = field(default_factory=dict)
    sort: str | None = None
    page: int = 1
    per_page: int = 50

    def add_filter(self, api_field: str, operator: str, value: str = "") -> None:
        if operator not in VALID_OPERATORS:
            raise ValueError(
                f"Unknown filter operator '{operator}'. "
                f"Valid: {', '.join(sorted(VALID_OPERATORS))}"
            )
        self.filters[f"{api_field}[{operator}]"] = value

    def to_dict(self) -> dict[str, str]:
        params: dict[str, str] = {**self.filters}
        if self.sort:
            params["sort"] = self.sort
        params["page"] = str(self.page)
        params["per_page"] = str(self.per_page)
        return params

    @classmethod
    def from_cli_args(
        cls,
        *,
        raw_filters: list[str] | None = None,
        sort: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> QueryParams:
        qp = cls(page=page, per_page=per_page, sort=sort)

        for raw in raw_filters or []:
            # Try "field[operator]=value" first
            m = _FILTER_RE.match(raw)
            if m:
                qp.add_filter(m.group(1), m.group(2), m.group(3) or "")
                continue

            # Try "field=value" shorthand (implies eq)
            m = _SHORTHAND_RE.match(raw)
            if m:
                qp.add_filter(m.group(1), "eq", m.group(2))
                continue

            raise ValueError(
                f"Invalid filter format: '{raw}'. "
                "Use 'field[operator]=value' or 'field=value'."
            )

        return qp
