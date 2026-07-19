---
name: storage-add-file
description: Update `_catalog.jsonld` after a new file has been added to an rclone storage folder. Use when one document has been introduced and only that file's catalog entry needs to be added or refreshed.
---

# Storage Add File

## Overview

Update a single file entry after the document already exists in the target rclone folder. Use this when only one document changed and a full folder rescan would be unnecessary.

## Workflow

1. Verify `rclone` is installed and the remote path is reachable.
2. Confirm the new document already exists in the target folder.
3. Derive tags from the document and update only that file's catalog row.
4. Write the updated `_catalog.jsonld` back to the same rclone folder.

## Rules

- Do not auto-configure `rclone`.
- Do not rewrite the rest of the catalog when only one entry changed.
- Keep the filename stable and store a deduped tag list.
- Use `storage-sync-catalog` if more than one file changed.
