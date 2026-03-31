# Luminous CLI

A command-line interface for the [Luminous](https://joinluminous.com) API. Manage products, orders, inventory, companies, and more from your terminal.

## Features

- **14 resource types** with full CRUD support
- **Interactive shell** with auto-completion and command history
- **Flexible input** — JSON strings, files, stdin, or repeatable flags
- **Smart output** — Rich tables in the terminal, JSON/CSV/NDJSON for piping
- **Filtering & pagination** — query params mapped directly to CLI flags
- **Profile management** — switch between multiple Luminous accounts
- **Secure credential storage** — system keyring with file fallback

## Installation

```bash
# With pip
pip install luminous-cli

# With pipx (recommended)
pipx install luminous-cli

# From source
git clone https://github.com/LuminousInventory/luminous-cli.git
cd luminous-cli
pip install -e .
```

## Quick Start

### Authenticate

```bash
luminous auth login
# Company subdomain: mycompany
# API key: ****
```

Or use environment variables:

```bash
export LUMINOUS_COMPANY=mycompany
export LUMINOUS_API_KEY=your_api_key
```

### Run Commands

```bash
luminous products list
luminous sales-orders list --filter "order_status=shipped" --per-page 10
luminous products get 123
```

### Interactive Shell

Run `luminous` with no arguments to enter the interactive REPL:

```
$ luminous

Luminous CLI — interactive mode
Connected to: mycompany
Type a command, 'help' for commands, or 'exit' to quit.

luminous (mycompany) > products list --per-page 5
┏━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃ ID   ┃ SKU    ┃ Name        ┃ Type    ┃ Retail ┃ Wholesale ┃ Sellable ┃
┡━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩
│ 101  │ W-001  │ Widget      │ PRODUCT │ 29.99  │ 12.50     │ Yes      │
│ 102  │ W-002  │ Gadget      │ PRODUCT │ 49.99  │ 25.00     │ Yes      │
└──────┴────────┴─────────────┴─────────┴────────┴───────────┴──────────┘
Page 1 of 12 (58 total)

luminous (mycompany) > exit
```

Features: tab completion, command history (persisted), colored prompt with profile name.

## Commands

### Resources

| Resource | Commands |
|---|---|
| **products** | `list` `get` `create` `update` `upsert` `delete` `tags` `custom-fields` |
| **sales-orders** | `list` `get` `create` `export` `shipments` `tags` `custom-fields` |
| **purchase-orders** | `list` `get` `create` `update` `delete` `items` `payments` |
| **inventory** | `stocks` `adjust` |
| **transfer-orders** | `list` `get` `create` |
| **receiving-reports** | `list` `get` `create` |
| **invoices** | `list` `get` `tags` `custom-fields` |
| **companies** | `list` `get` `create` `update` `delete` `contacts` `products` `price-overrides` `tags` `custom-fields` |
| **contacts** | `list` `get` `create` `update` `delete` |
| **boms** | `list` `get` `create` `update` `delete` |
| **warehouses** | `list` `get` |
| **locations** | `list` `get` |
| **price-schedules** | `list` `get` |
| **price-levels** | `list` `get` |

### Auth & Config

```bash
luminous auth login              # Interactive login
luminous auth logout             # Remove credentials
luminous auth status             # Show current auth info
luminous auth switch <profile>   # Switch between profiles

luminous config set default_format json
luminous config set per_page 100
luminous config list
```

## Querying Data

### Filtering

Use `--filter` with the format `field[operator]=value`:

```bash
# Exact match
luminous products list --filter "sku[eq]=SKU-001"

# Range
luminous products list --filter "retail_price[gte]=50" --filter "retail_price[lte]=100"

# Contains
luminous products list --filter "name[contains]=Widget"

# Multiple values
luminous sales-orders list --filter "order_status[in]=pending,shipped,processing"

# Null checks
luminous products list --filter "supplier_id[set]"
luminous products list --filter "upc[notset]"

# Shorthand (implies eq)
luminous products list --filter "type=PRODUCT"
```

**Available operators:** `eq` `neq` `gt` `gte` `lt` `lte` `contains` `notcontains` `in` `notin` `set` `notset`

### Sorting

```bash
luminous products list --sort "name:asc"
luminous sales-orders list --sort "order_date:desc"
```

### Pagination

```bash
luminous products list --page 2 --per-page 100   # Specific page
luminous products list --all                       # Fetch every page
```

### Output Formats

```bash
luminous products list                    # Rich table (default in terminal)
luminous products list --format json      # JSON (default when piped)
luminous products list --format csv       # CSV
luminous products list --format ndjson    # Newline-delimited JSON

# Pipe to other tools
luminous products list --format json | jq '.[].sku'
luminous warehouses list --format csv > warehouses.csv
```

## Creating & Updating Records

### JSON Input

```bash
# Inline JSON
luminous products create --json '{"name": "Widget", "sku": "W-001", "category_id": 1}'

# From file
luminous sales-orders create --file order.json

# From stdin
cat order.json | luminous sales-orders create --json -
```

### Repeatable Flags for Line Items

For resources with nested arrays (items, tags, extra costs), use repeatable flags:

```bash
luminous purchase-orders create \
  --json '{"order_date": "2025-06-01", "supplier_id": 5}' \
  --item "sku=W-001,quantity=10,unit_price=12.50" \
  --item "sku=W-002,quantity=5,unit_price=8.00" \
  --tag "urgent" \
  --tag "Q2"

luminous boms create \
  --json '{"name": "Assembly Kit"}' \
  --item "sku=PART-001,quantity=2" \
  --item "sku=PART-002,quantity=1" \
  --extra-cost "name=Labor,quantity=1,unit_price=25.00"
```

### Hybrid: Template + Override

Use a JSON file as a base and override specific fields with flags:

```bash
luminous sales-orders create --file template.json --json '{"order_number": "SO-2001"}'
```

### Updates

```bash
luminous products update 123 --json '{"name": "Updated Name"}'
luminous purchase-orders update 456 --file updated_po.json
```

**Array replacement safety:** When an update payload includes `items`, `payments`, or other array fields, the CLI warns that existing entries will be replaced. Use `--yes` to skip the prompt.

### Tags & Custom Fields

```bash
# Tags
luminous products tags list 123
luminous products tags add 123 --tag "clearance" --tag "seasonal"
luminous products tags replace 123 --tag "new-arrival"
luminous products tags remove 123 "clearance"

# Custom fields
luminous products custom-fields get 123
luminous products custom-fields set 123 --field "color=Red" --field "size=XL"
```

Tags and custom fields are available on: `products`, `sales-orders`, `invoices`, `companies`.

### Subresources

```bash
# Shipments
luminous sales-orders shipments list 456
luminous sales-orders shipments create 456 --file shipment.json

# Payments
luminous purchase-orders payments create 789 \
  --json '{"payment_date": "2025-06-15", "payment_type": "bank_transfer", "paid_amount": 5000}'
luminous purchase-orders payments delete 789 12 --yes

# Company subresources
luminous companies contacts list 42
luminous companies products list 42
luminous companies price-overrides list 42
```

## Configuration

Config is stored at `~/.config/luminous/config.toml`:

```toml
default_profile = "production"

[profiles.production]
company = "mycompany"
default_format = "table"
per_page = 50

[profiles.staging]
company = "mycompany-staging"
default_format = "json"
```

Credentials are stored in the system keyring (macOS Keychain, GNOME Keyring, Windows Credential Manager) with a file-based fallback for headless environments.

### Multiple Profiles

```bash
luminous auth login --profile staging     # Add a second profile
luminous auth switch staging              # Switch to it
luminous auth status                      # Verify
luminous products list --profile production  # One-off override
```

## Error Handling

Errors are displayed with context and structured exit codes:

```
$ luminous sales-orders create --file bad_order.json

╭─────────────────── Error ───────────────────╮
│ Validation failed                           │
│                                             │
│   items.0.product    not found              │
│   items.1.quantity   must be greater than 0 │
│   bill_to.name       required               │
╰─────────────────────────────────────────────╯
```

| Exit Code | Meaning |
|---|---|
| 0 | Success |
| 1 | API error |
| 65 | Validation error (422) |
| 69 | Not found (404) |
| 70 | Conflict (409) |
| 75 | Rate limited (429) |
| 76 | Network error |
| 77 | Authentication error (401) |

## Environment Variables

| Variable | Description |
|---|---|
| `LUMINOUS_COMPANY` | Company subdomain (overrides profile) |
| `LUMINOUS_API_KEY` | API key (overrides keyring) |

## Using with Claude Code

Add a `CLAUDE.md` to your project with the Luminous CLI reference so Claude can query your Luminous data directly. See [CLAUDE.md](./CLAUDE.md) for an example.

## Development

```bash
git clone https://github.com/LuminousInventory/luminous-cli.git
cd luminous-cli
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/
```

## License

MIT
