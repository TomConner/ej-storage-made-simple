from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Iterable

CATALOG_FILENAME = "_catalog.jsonld"


@dataclass(slots=True)
class CatalogEntry:
    filename: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"filename": self.filename, "tags": list(self.tags)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CatalogEntry":
        filename = str(data.get("filename", "")).strip()
        tags = [str(tag).strip() for tag in data.get("tags", []) if str(tag).strip()]
        return cls(filename=filename, tags=tags)


@dataclass(slots=True)
class CatalogDocument:
    context: str
    entries: list[CatalogEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "@context": self.context,
            "files": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, default_context: str = "") -> "CatalogDocument":
        context = str(data.get("@context", default_context)).strip() or default_context
        raw_entries = data.get("files")
        if raw_entries is None:
            raw_entries = data.get("entries", [])
        entries = [CatalogEntry.from_dict(item) for item in raw_entries if isinstance(item, dict)]
        return cls(context=context, entries=entries)

    @classmethod
    def empty(cls, context: str) -> "CatalogDocument":
        return cls(context=context, entries=[])


def catalog_document_to_text(document: CatalogDocument) -> str:
    return json.dumps(document.to_dict(), indent=2, sort_keys=False, ensure_ascii=False) + "\n"


def catalog_document_from_text(text: str, *, default_context: str = "") -> CatalogDocument:
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Catalog JSON-LD must be a JSON object.")
    return CatalogDocument.from_dict(data, default_context=default_context)


def sort_entries(entries: Iterable[CatalogEntry]) -> list[CatalogEntry]:
    return sorted(entries, key=lambda entry: entry.filename.lower())


def normalize_document(document: CatalogDocument) -> CatalogDocument:
    normalized_entries: list[CatalogEntry] = []
    for entry in sort_entries(document.entries):
        deduped_tags: list[str] = []
        seen: set[str] = set()
        for tag in entry.tags:
            tag = str(tag).strip()
            if not tag or tag in seen:
                continue
            deduped_tags.append(tag)
            seen.add(tag)
        normalized_entries.append(CatalogEntry(filename=entry.filename, tags=deduped_tags))
    return CatalogDocument(context=document.context, entries=normalized_entries)


def upsert_entry(document: CatalogDocument, filename: str, tags: Iterable[str]) -> CatalogDocument:
    updated_entries = [entry for entry in document.entries if entry.filename != filename]
    updated_entries.append(CatalogEntry(filename=filename, tags=list(tags)))
    return normalize_document(CatalogDocument(context=document.context, entries=updated_entries))


def remove_entry(document: CatalogDocument, filename: str) -> CatalogDocument:
    updated_entries = [entry for entry in document.entries if entry.filename != filename]
    return normalize_document(CatalogDocument(context=document.context, entries=updated_entries))

