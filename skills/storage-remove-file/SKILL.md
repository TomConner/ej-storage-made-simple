---
name: storage-remove-file
description: Update `_catalog.jsonld` after a file has been removed from an rclone storage folder. Use when one document was deleted and the matching catalog row needs to be pruned.
---

# Storage Remove File

## Overview

Remove a single catalog row after a document has already been deleted from the rclone folder. Use this when the folder contents changed and only one entry needs pruning.

## Workflow

1. Verify `rclone` is installed and the remote path is reachable.
2. Confirm the document is no longer present in the target folder.
3. Remove the matching filename from `_catalog.jsonld`.
4. Write the pruned catalog back to the same rclone folder.

## Rules

- Do not auto-configure `rclone`.
- Do not leave stale entries behind.
- Keep the rest of the catalog untouched.
- Use `storage-sync-catalog` if several files changed together.
