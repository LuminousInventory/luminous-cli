# Luminous CLI

The `luminous` CLI is installed and authenticated. Use it to interact with the Luminous API directly from the terminal via Bash.

## Authentication

Credentials are already stored. If you need to check: `luminous auth status`

## Command Pattern

```
luminous <resource> <action> [options]
```

## Available Resources & Commands

| Resource | Actions |
|---|---|
| `products` | `list`, `get <id>`, `create`, `update <id>`, `upsert`, `delete <id>`, `tags`, `custom-fields` |
| `sales-orders` | `list`, `get <id>`, `create`, `export`, `shipments list <id>`, `shipments create <id>`, `tags`, `custom-fields` |
| `purchase-orders` | `list`, `get <id>`, `create`, `update <id>`, `delete <id>`, `items`, `payments create <id>`, `payments update <id> <pid>`, `payments delete <id> <pid>` |
| `inventory` | `stocks`, `adjust` |
| `transfer-orders` | `list`, `get <id>`, `create` |
| `receiving-reports` | `list`, `get <id>`, `create` |
| `invoices` | `list`, `get <id>`, `tags`, `custom-fields` |
| `companies` | `list`, `get <id>`, `create`, `update <id>`, `delete <id>`, `contacts list <id>`, `products list <id>`, `price-overrides list <id>`, `tags`, `custom-fields` |
| `contacts` | `list`, `get <id>`, `create`, `update <id>`, `delete <id>` |
| `boms` | `list`, `get <id>`, `create`, `update <id>`, `delete <id>` |
| `warehouses` | `list`, `get <id>` |
| `locations` | `list`, `get <id>` |
| `price-schedules` | `list`, `get <id>` |
| `price-levels` | `list`, `get <id>` |

## Querying Data

```bash
# List with filters
luminous products list --filter "sku[eq]=SKU-001" --filter "type=PRODUCT"
luminous sales-orders list --filter "order_status[in]=pending,shipped" --filter "order_date[gte]=2025-01-01"

# Pagination
luminous products list --per-page 100 --page 2

# Fetch all pages
luminous products list --all

# Sort
luminous products list --sort "name:asc"

# Output formats: table (default), json (for parsing), csv, ndjson
luminous products list --format json
luminous warehouses list --format csv
```

### Filter Operators

`eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `contains`, `notcontains`, `in`, `notin`, `set`, `notset`

## Creating & Updating

```bash
# JSON string
luminous products create --json '{"name": "Widget", "sku": "W-001", "category_id": 1}'

# From file
luminous sales-orders create --file order.json

# From stdin
cat order.json | luminous sales-orders create --json -

# Repeatable --item for line items
luminous purchase-orders create --json '{"order_date": "2025-01-01", "supplier_id": 5}' \
  --item "sku=W-001,quantity=10,unit_price=12.50" \
  --item "sku=W-002,quantity=5,unit_price=8.00"

# Tags
luminous products tags add 123 --tag "clearance" --tag "seasonal"

# Custom fields
luminous products custom-fields set 123 --field "color=Red" --field "size=XL"
```

## Tips for AI Usage

- Always use `--format json` when you need to parse output programmatically
- Use `--per-page 100` to get more results per request (max 100)
- Use `--all` to fetch every record (streams all pages)
- Pipe JSON output to parse: `luminous products list --format json | ...`
- Get a single record for full details: `luminous products get <id> --format json`
- The `--filter` flag maps directly to the API's query params: `--filter "field[operator]=value"`
