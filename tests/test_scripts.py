from __future__ import annotations

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storage_made_simple.catalog import CatalogDocument, CatalogEntry
from scripts import catalog_folder, check_rclone, sync_catalog, update_catalog_entry


class ScriptTests(unittest.TestCase):
    def test_check_rclone_main(self) -> None:
        status = SimpleNamespace(installed=True, configured=True, to_dict=lambda: {"installed": True, "configured": True})
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = check_rclone.main(["--json"], detector=lambda: status)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue()), {"installed": True, "configured": True})

    def test_catalog_folder_main(self) -> None:
        document = CatalogDocument(context="tgod:_Money/2026", entries=[CatalogEntry(filename="a.csv", tags=["from:irs"])])
        builder = Mock(return_value=document)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = catalog_folder.main(["tgod:_Money/2026", "--json"], builder=builder)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["@context"], "tgod:_Money/2026")
        builder.assert_called_once_with("tgod:_Money/2026")

    def test_sync_catalog_main(self) -> None:
        document = CatalogDocument(context="tgod:_Money/2026", entries=[CatalogEntry(filename="a.csv", tags=["from:irs"])])
        syncer = Mock(return_value=document)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = sync_catalog.main(["tgod:_Money/2026"], syncer=syncer)
        self.assertEqual(code, 0)
        self.assertIn("synced=tgod:_Money/2026", stdout.getvalue())
        syncer.assert_called_once_with("tgod:_Money/2026")

    def test_update_catalog_entry_main(self) -> None:
        document = CatalogDocument(context="tgod:_Money/2026", entries=[CatalogEntry(filename="a.csv", tags=["from:irs"])])
        add_handler = Mock(return_value=document)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = update_catalog_entry.main(["add", "tgod:_Money/2026", "a.csv"], add_handler=add_handler)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["@context"], "tgod:_Money/2026")
        add_handler.assert_called_once_with("tgod:_Money/2026", "a.csv")


if __name__ == "__main__":
    unittest.main()
