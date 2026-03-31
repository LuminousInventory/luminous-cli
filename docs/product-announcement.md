# Luminous CLI — Product Announcement (Internal)

**Date:** March 31, 2026
**Team:** Engineering
**Status:** Available now (v0.1.0)

---

## What is it?

The Luminous CLI is a command-line tool that lets users interact with the entire Luminous API from their terminal. Instead of clicking through the UI or writing custom API integration code, users type commands like:

```
luminous products list --filter "type=PRODUCT" --sort "name:asc"
luminous sales-orders list --filter "order_status=shipped" --per-page 100
luminous purchase-orders create --file po.json
```

It also includes an interactive shell mode — run `luminous` and you drop into a REPL with auto-completion, command history, and a persistent session. Think of it like a terminal-native interface to Luminous.

---

## Who is this for?

**Operations teams** who need to pull data quickly without navigating the UI — bulk lookups, inventory checks, order searches.

**Developers and integrators** building on top of Luminous who need a fast way to test API calls, inspect data, and prototype workflows without writing code.

**AI and automation workflows** — the CLI is designed to be used by AI coding assistants (like Claude Code) and scripts. JSON output, structured error codes, and stdin/pipe support make it a building block for automated processes.

**Power users** who manage large catalogs, process bulk orders, or need repeatable operations they can script and schedule.

---

## What can it do?

The CLI covers the full Luminous API surface:

| Area | What you can do |
|---|---|
| **Products** | List, search, create, update, upsert by SKU, delete. Manage tags and custom fields. |
| **Sales Orders** | List, search, create with line items and addresses. Manage shipments and packages. Export for sync. |
| **Purchase Orders** | Full lifecycle — create, update, delete. Manage payments. List PO items across all orders. |
| **Inventory** | View stock levels across warehouses. Create adjustments. |
| **Companies & Contacts** | Full CRUD. View company-specific products, pricing overrides, contacts. |
| **BOMs** | Create and manage Bills of Materials with items and extra costs. |
| **Transfers & Receiving** | Create transfer orders and receiving reports. |
| **Invoices** | View invoices with payment status. |
| **Pricing** | View price schedules and price levels. |
| **Warehouses & Locations** | List and inspect warehouse and location data. |

Every list command supports filtering (12 operators), sorting, pagination, and multiple output formats (table, JSON, CSV).

---

## Key capabilities for marketing to know about

### 1. Interactive Shell
Users can run `luminous` and work in a persistent session with tab completion and history. This is the headline UX feature — it feels like a dedicated Luminous terminal.

### 2. Flexible Data Input
Creating complex records (orders with line items, BOMs with components) doesn't require writing JSON by hand. Users can mix approaches:
- `--item "sku=W-001,quantity=10,unit_price=12.50"` for quick inline items
- `--file order.json` for templated workflows
- Piping from other tools: `cat data.json | luminous sales-orders create --json -`

### 3. AI-Ready
The CLI was built with AI assistant integration in mind. Claude Code (and similar tools) can use it as a tool to query and manage Luminous data during conversations. A `CLAUDE.md` reference file is included. This means customers using AI coding tools get Luminous data access for free in their AI workflows.

### 4. Script and Automation Friendly
- JSON output for machine parsing
- Structured exit codes (auth failure vs validation error vs not found)
- `--all` flag to paginate through entire datasets
- `--yes` flag to skip confirmation prompts in scripts
- Errors on stderr, data on stdout — safe for piping

### 5. Multi-Account Support
Named profiles let users switch between production, staging, and demo environments with `luminous auth switch`.

---

## What this means for customers

**For customers who currently integrate via API:** The CLI gives them a zero-code way to test, debug, and prototype. Instead of writing a script to check if an order was created correctly, they type one command.

**For customers who don't integrate via API:** The CLI opens up automation possibilities without requiring a developer. Operations staff can write simple shell scripts to automate repetitive tasks — bulk inventory adjustments, order exports, report generation.

**For customers using AI tools:** Their AI assistant can now read and write Luminous data directly. "Show me all pending orders from this week" or "Create a purchase order for these 5 SKUs" becomes a natural conversation.

---

## Messaging angles for marketing

- **"Your Luminous data, one command away"** — speed and directness
- **"Built for teams that automate"** — scripting, CI/CD, scheduled jobs
- **"AI-native from day one"** — designed to work with Claude Code and other AI assistants
- **"No code required"** — operations teams can use it without developer support
- **"Interactive terminal for your inventory"** — the shell mode is visually compelling for demos

---

## Technical details

- **Language:** Python 3.10+
- **Install:** `pip install luminous-cli`
- **Open source:** https://github.com/LuminousInventory/luminous-cli
- **Auth:** Bearer token, stored in system keyring
- **Dependencies:** typer, httpx, rich, prompt-toolkit, orjson

---

## What's next

- Resource-specific shortcut flags (e.g., `--sku` instead of `--filter "sku[eq]=..."`)
- Shell completions for bash/zsh/fish
- An MCP server wrapper for deeper AI tool integration
- Bulk operations (create/update many records from a CSV)
- `luminous watch` for real-time order monitoring

---

**Questions?** Reach out to Engineering. The repo has full documentation in the README and CLAUDE.md.
