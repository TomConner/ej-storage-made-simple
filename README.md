# storage-made-simple

`storage-made-simple` is a small rclone-backed catalog toolkit for document folders.

It provides:

- five focused skills for cataloging, adding, removing, replacing, and syncing files
- a thin MCP-style tool surface for local automation
- CLI wrappers for checking `rclone` and updating catalogs

The catalog format is a JSON-LD file named `_catalog.jsonld` stored in the same rclone folder as the documents.

## Requirements

- Python 3.11 or newer
- `rclone` installed and already configured with at least one remote
- Optional document parsing libraries for richer tag extraction:
  - `pypdf` for PDFs
  - `openpyxl` for Excel files

The project does not try to install or configure `rclone` for you. If `rclone` is missing or unconfigured, the tooling will stop and report that setup is incomplete.

## Install

1. Clone the repository.
2. Create or sync the Python environment with `uv`:

```bash
uv sync
```

3. Verify that `rclone` is available and configured:

```bash
uv run python scripts/check_rclone.py --json
```

If you want PDF and Excel tag extraction to work, install the optional readers in the same environment:

```bash
uv pip install pypdf openpyxl
```

## Use In Codex

Codex can use the skills directly once the skill folders are available in a Codex skill location.

1. Make the skill folders available to Codex, typically by copying or symlinking the five folders under `skills/` into your local Codex skills directory.
2. Open the repo in Codex.
3. Reference the skill by name in your prompt:

```text
Use $storage-catalog-folder to catalog this rclone folder: tgod:_Money/2026
```

Available skills:

- `storage-catalog-folder`
- `storage-add-file`
- `storage-remove-file`
- `storage-replace-file`
- `storage-sync-catalog`

## Use In Claude

Claude workflows depend on the Claude client you use, but the pattern is the same:

1. Make the five skill folders available in the Claude skill location supported by your setup.
2. Point Claude at this repository or the local copy of the skill folders.
3. Ask Claude to use one of the skills by name.

Example prompts:

```text
Use $storage-sync-catalog to reconcile tgod:_Money/2026 with _catalog.jsonld.
```

```text
Use $storage-add-file to add the new PDF in tgod:_Money/2026 and refresh its catalog entry.
```

## Use The CLI

The repository ships command wrappers for the most common workflows.

Check `rclone` setup:

```bash
uv run python scripts/check_rclone.py
```

Build a fresh catalog for a folder:

```bash
uv run python scripts/catalog_folder.py tgod:_Money/2026
```

Sync a folder against the current catalog:

```bash
uv run python scripts/sync_catalog.py tgod:_Money/2026
```

Update one entry:

```bash
uv run python scripts/update_catalog_entry.py add tgod:_Money/2026 statement.pdf
uv run python scripts/update_catalog_entry.py remove tgod:_Money/2026 statement.pdf
uv run python scripts/update_catalog_entry.py replace tgod:_Money/2026 statement.pdf --previous-filename old-statement.pdf
```

Add `--json` to any of the main scripts when you want machine-readable output.

## Use The MCP-Style Server

The server scaffold exposes the same operations as named tools:

- `detect_rclone_setup`
- `scan_folder`
- `build_catalog`
- `sync_catalog`
- `add_file`
- `remove_file`
- `replace_file`

Inspect the tool surface:

```bash
uv run python -m storage_made_simple.mcp_server --json
```

The server is intentionally thin and testable. In a local MCP setup, wire these tools into the client or wrapper you use for Claude or Codex.

## Catalog Rules

- Keep `_catalog.jsonld` in the same rclone folder as the documents.
- Store `@context` as the rclone folder path.
- Keep one entry per file with `filename` and `tags`.
- Support PDF, CSV, and Excel documents.
- Normalize and dedupe tags before writing the catalog.

## Repository Layout

- `skills/` contains the five task-specific skills.
- `scripts/` contains CLI entry points and setup checks.
- `src/storage_made_simple/` contains the catalog, tagging, rclone, and server code.
- `tests/` contains the unit tests.
- `tasks/` contains stage checklists and implementation notes.
