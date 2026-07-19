---
name: storage-catalog-folder
description: Catalog an rclone storage folder for the first time, create or refresh `_catalog.jsonld`, and derive tags for PDF, CSV, and Excel documents. Use when scanning a new folder, rebuilding a catalog, or establishing the baseline file list and tags.
---

# Storage Catalog Folder

## Overview

Create the first catalog for a single rclone path. Use this when the folder has never been cataloged or when the catalog should be rebuilt from the current file set.

## Workflow

1. Verify `rclone` is installed and the remote path is reachable.
2. List the files in the folder, excluding `_catalog.jsonld`.
3. Read supported documents and derive normalized tags.
4. Write `_catalog.jsonld` with `@context` equal to the rclone folder path.
5. Keep one entry per file and dedupe the tag list.

## Rules

- Do not attempt to configure `rclone`.
- Support only PDF, CSV, and Excel files.
- Preserve filenames exactly as they appear in the folder.
- If extraction is partial, keep the file listed and use the best available tags.
