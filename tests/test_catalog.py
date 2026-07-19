from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from storage_made_simple.catalog import (
    CATALOG_FILENAME,
    CatalogDocument,
    CatalogEntry,
    catalog_document_from_text,
    catalog_document_to_text,
    normalize_document,
    remove_entry,
    upsert_entry,
)


class CatalogTests(unittest.TestCase):
    def test_catalog_round_trip(self) -> None:
        document = CatalogDocument(
            context="tgod:_Money/2026",
            entries=[
                CatalogEntry(filename="b.pdf", tags=["type:statement", "type:statement"]),
                CatalogEntry(filename="a.csv", tags=["from:irs"]),
            ],
        )
        normalized = normalize_document(document)
        text = catalog_document_to_text(normalized)
        loaded = catalog_document_from_text(text, default_context="fallback")

        self.assertEqual(loaded.context, "tgod:_Money/2026")
        self.assertEqual([entry.filename for entry in loaded.entries], ["a.csv", "b.pdf"])
        self.assertEqual(loaded.entries[1].tags, ["type:statement"])

    def test_entry_updates(self) -> None:
        document = CatalogDocument.empty("tgod:_Money/2026")
        document = upsert_entry(document, "a.csv", ["from:irs", "from:irs"])
        document = upsert_entry(document, "b.pdf", ["type:summary"])
        document = remove_entry(document, "a.csv")

        self.assertEqual([entry.filename for entry in document.entries], ["b.pdf"])
        self.assertEqual(document.entries[0].tags, ["type:summary"])

    def test_catalog_filename_constant(self) -> None:
        self.assertEqual(CATALOG_FILENAME, "_catalog.jsonld")


if __name__ == "__main__":
    unittest.main()
