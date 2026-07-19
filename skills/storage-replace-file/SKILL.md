---
name: storage-replace-file
description: Update `_catalog.jsonld` after a file has been replaced in an rclone storage folder. Use when one document changed in place or was swapped for a newer version.
---

# Storage Replace File

## Overview

Refresh one catalog entry after a replacement. Use this when a document was swapped in place and the filename or contents may have changed.

## Workflow

1. Verify `rclone` is installed and the remote path is reachable.
2. Confirm the replacement file is present and the old version is no longer authoritative.
3. Remove the stale entry if the filename changed.
4. Re-derive tags for the current file and write the refreshed catalog.

## Rules

- Do not auto-configure `rclone`.
- If the replacement only changed contents, keep the filename and refresh tags in place.
- If the filename changed, remove the old filename entry before writing the new one.
- Use `storage-sync-catalog` if more than one file changed.
