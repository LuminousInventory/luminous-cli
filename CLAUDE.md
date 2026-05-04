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
| `products` | `list`, `get`, `create`, `update`, `upsert`, `delete`, `export`, `pricing`, `company-pricing`, `get-pricing`, `get-company-pricing`, `add-alt-sku`, `attach-boms`, `detach-boms`, `tags`, `custom-fields` |
| `sales-orders` | `list`, `get`, `create`, `update` (PATCH), `export`, `shipments` (incl. `force-push-source-fulfillment`), `tags`, `custom-fields` |
| `purchase-orders` | `list`, `get`, `create`, `update`, `delete`, `items`, `payments`, `payment-obligations`, `billable-lines`, `shipments` |
| `purchase-order-shipments` | `list`, `get` |
| `inventory` | `stocks`, `adjust` |
| `transfer-orders` | `list`, `get`, `create`, `update` |
| `receiving-reports` | `list`, `get`, `create`, `billable-lines` |
| `invoices` | `list`, `get`, `create`, `tags`, `custom-fields` |
| `companies` | `list`, `get`, `create`, `update`, `delete`, `contacts`, `products`, `price-overrides`, `tags`, `custom-fields` |
| `contacts` | `list`, `get`, `create`, `update`, `delete`, `set-password`, `set-b2b-portal-password` |
| `boms` | `list`, `get`, `create`, `update`, `delete` |
| `warehouses` | `list`, `get`, `create`, `update`, `delete` |
| `warehouse-groups` | `list`, `get`, `create`, `update`, `delete` |
| `locations` | `list`, `get` |
| `price-schedules` | `list`, `get` |
| `price-levels` | `list`, `get` |
| `bills` | `list`, `get`, `create`, `update` (PUT), `delete`, `post`, `hold`, `unhold`, `reopen`, `variance`, `resolve-variance`, `auto-allocate`, `duplicate-check`, `summary`, `inbox`, `by-vendor`, `by-po`, `aging`, `calculate-due-date`, `from-shipments-prefill`, `billable-lines`, `candidate-lines`, `status`, `import-parse`, `payments`, `allocations`, `attachments`, `bill-items` |
| `stock-snapshot` | `get --start-date --end-date` |
| `consumption` | `list`, `export` |
| `inventory-aging` | `list`, `export` |
| `forecast` | `list`, `get`, `product`, `export`, `refresh-status`, `warehouse` |
| `reports` | `cogs`, `cogs-update-costs`, `close-books`, `discrepancy`, `edi` |
| `currency` | `list`, `base`, `set-base`, `rates`, `create-rate`, `convert` |
| `inbound-shipments` | `list`, `get` |
| `fulfillment-orders` | `list`, `get`, `push`, `unpush`, `remove-so-item`, `create-shipment` |
| `channels` | `list`, `get`, `create`, `update`, `delete`, `create-sales`, `sync-integration-products`, `lock` |
| `unit-classes` | `list`, `get`, `create`, `update`, `delete`, `set-default-uom` |
| `unit-of-measures` | `list`, `get`, `create`, `update`, `delete` |
| `unit-conversion-rules` | `list`, `get`, `create`, `update`, `delete`, `resolve` |
| `payment-obligations` | `list`, `get`, `update`, `update-status`, `dashboard`, `link-bill`, `unlink-bill` |
| `prepayments` | `list`, `create`, `apply`, `reverse` |
| `vendor-credits` | `list`, `get`, `create`, `apply`, `cancel`, `reverse`, `delete-application`, `vendor-statement` |
| `vendor-returns` | `list`, `get`, `create`, `process`, `cancel`, `generate-credit` |
| `integration-accounts` | `shipping-methods` |
| `integration-field-mappings` | `list`, `get`, `create`, `update`, `delete`, `bulk-create`, `bulk-delete`, `field-names`, `groups`, `suggest-carrier`, `create-and-retry`, `auto-carrier-mapping`, `quick-add` |
| `integration-mappings` | `list`, `get`, `create`, `update`, `delete` |
| `custom-fields` | `list`, `get`, `create`, `update`, `delete` |
| `suppliers` | `list`, `get`, `create`, `update`, `delete` |
| `labels` | `render` |

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
