from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from storage_made_simple.tagging import dedupe_tags, derive_tags_from_document, normalize_tag


class TaggingTests(unittest.TestCase):
    def test_normalize_and_dedupe(self) -> None:
        self.assertEqual(normalize_tag(" From:IRS "), "from:irs")
        self.assertEqual(dedupe_tags(["from:irs", "from:irs", "type:statement"]), ["from:irs", "type:statement"])

    def test_filename_based_tags(self) -> None:
        tags = derive_tags_from_document("citizens_bank_statement_2025-03-12.pdf")
        self.assertIn("from:citizens-bank", tags)
        self.assertIn("type:statement", tags)
        self.assertIn("date:2025-03-12", tags)

    def test_csv_signals(self) -> None:
        csv_bytes = b"Date,Amount,Description\n2025-03-12,10,IRS payment\n"
        tags = derive_tags_from_document("irs_2025.csv", csv_bytes)
        self.assertIn("from:irs", tags)
        self.assertIn("date:2025", tags)


if __name__ == "__main__":
    unittest.main()
