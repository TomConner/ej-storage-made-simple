from __future__ import annotations

from pathlib import Path

from storage_made_simple import catalog, rclone, tagging

SUPPORTED_SUFFIXES = {".csv", ".pdf", ".xls", ".xlsx"}


def is_supported_document(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_SUFFIXES


def remote_catalog_path(remote_folder: str) -> str:
    return rclone.join_rclone_path(remote_folder, catalog.CATALOG_FILENAME)


def load_remote_catalog(remote_folder: str) -> catalog.CatalogDocument:
    try:
        raw = rclone.read_remote_bytes(remote_catalog_path(remote_folder))
    except rclone.RcloneError:
        return catalog.CatalogDocument.empty(remote_folder)
    if not raw.strip():
        return catalog.CatalogDocument.empty(remote_folder)
    return catalog.catalog_document_from_text(raw.decode("utf-8", errors="replace"), default_context=remote_folder)


def write_remote_catalog(remote_folder: str, document: catalog.CatalogDocument) -> None:
    normalized = catalog.normalize_document(document)
    rclone.write_remote_text(remote_catalog_path(remote_folder), catalog.catalog_document_to_text(normalized))


def list_supported_files(remote_folder: str) -> list[rclone.RemoteFile]:
    files = rclone.list_remote_files(remote_folder)
    return [item for item in files if item.path != catalog.CATALOG_FILENAME and is_supported_document(item.path)]


def derive_tags_for_remote_file(remote_folder: str, remote_file: rclone.RemoteFile) -> list[str]:
    raw = rclone.read_remote_bytes(rclone.join_rclone_path(remote_folder, remote_file.path))
    return tagging.derive_tags_from_document(remote_file.path, raw)


def scan_folder(remote_folder: str) -> list[str]:
    rclone.ensure_rclone_ready()
    return [item.path for item in list_supported_files(remote_folder)]


def build_catalog(remote_folder: str) -> catalog.CatalogDocument:
    rclone.ensure_rclone_ready()
    entries: list[catalog.CatalogEntry] = []
    for remote_file in list_supported_files(remote_folder):
        tags = derive_tags_for_remote_file(remote_folder, remote_file)
        entries.append(catalog.CatalogEntry(filename=remote_file.path, tags=tags))
    document = catalog.CatalogDocument(context=remote_folder, entries=entries)
    write_remote_catalog(remote_folder, document)
    return catalog.normalize_document(document)


def sync_catalog(remote_folder: str) -> catalog.CatalogDocument:
    rclone.ensure_rclone_ready()
    current_files = {item.path: item for item in list_supported_files(remote_folder)}
    existing = load_remote_catalog(remote_folder)
    existing_by_name = {entry.filename: entry for entry in existing.entries}

    entries: list[catalog.CatalogEntry] = []
    for filename in sorted(current_files):
        derived = derive_tags_for_remote_file(remote_folder, current_files[filename])
        previous = existing_by_name.get(filename)
        merged = tagging.merge_tags(previous.tags if previous else [], derived)
        entries.append(catalog.CatalogEntry(filename=filename, tags=merged))

    document = catalog.CatalogDocument(context=remote_folder, entries=entries)
    write_remote_catalog(remote_folder, document)
    return catalog.normalize_document(document)


def add_file(remote_folder: str, filename: str) -> catalog.CatalogDocument:
    rclone.ensure_rclone_ready()
    supported_files = {item.path: item for item in list_supported_files(remote_folder)}
    if filename not in supported_files:
        raise FileNotFoundError(f"{filename!r} is not present in {remote_folder!r}")

    document = load_remote_catalog(remote_folder)
    tags = derive_tags_for_remote_file(remote_folder, supported_files[filename])
    updated = catalog.upsert_entry(document, filename, tags)
    write_remote_catalog(remote_folder, updated)
    return updated


def remove_file(remote_folder: str, filename: str) -> catalog.CatalogDocument:
    rclone.ensure_rclone_ready()
    document = load_remote_catalog(remote_folder)
    updated = catalog.remove_entry(document, filename)
    write_remote_catalog(remote_folder, updated)
    return updated


def replace_file(remote_folder: str, filename: str, previous_filename: str | None = None) -> catalog.CatalogDocument:
    rclone.ensure_rclone_ready()
    supported_files = {item.path: item for item in list_supported_files(remote_folder)}
    if filename not in supported_files:
        raise FileNotFoundError(f"{filename!r} is not present in {remote_folder!r}")

    document = load_remote_catalog(remote_folder)
    if previous_filename and previous_filename != filename:
        document = catalog.remove_entry(document, previous_filename)

    tags = derive_tags_for_remote_file(remote_folder, supported_files[filename])
    updated = catalog.upsert_entry(document, filename, tags)
    write_remote_catalog(remote_folder, updated)
    return updated

