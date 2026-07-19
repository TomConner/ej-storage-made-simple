---
name: storage-sync-catalog
description: Reconcile an rclone storage folder with `_catalog.jsonld`. Use when folder contents and catalog entries may have drifted and need a full refresh.
---

# Storage Sync Catalog

## Overview

Use this skill when the folder and catalog may be out of sync. It should compare the rclone folder contents against `_catalog.jsonld`, then add missing entries, remove stale ones, and refresh tags.

## Workflow

1. Verify `rclone` is installed and the remote path is reachable.
2. Load the current catalog and list the folder contents.
3. Remove catalog entries for missing files.
4. Add catalog entries for newly discovered files.
5. Refresh tags for files that still exist.
6. Write the normalized catalog back to the same folder.

## Rules

- Do not auto-configure `rclone`.
- Keep one entry per file.
- Deduplicate tags and normalize the entry order.
- Use this skill whenever more than one file changed or the catalog drifted.
