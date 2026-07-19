from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from storage_made_simple import catalog, operations, rclone


class OperationsTests(unittest.TestCase):
    def test_build_catalog_uses_supported_files(self) -> None:
        remote_files = [
            rclone.RemoteFile(path="one.csv", name="one.csv"),
            rclone.RemoteFile(path="two.pdf", name="two.pdf"),
        ]

        with patch.object(operations.rclone, "ensure_rclone_ready", return_value=rclone.RcloneStatus(True, True)), patch.object(
            operations, "list_supported_files", return_value=remote_files
        ), patch.object(operations, "derive_tags_for_remote_file", side_effect=[["from:irs"], ["type:statement"]]), patch.object(
            operations, "write_remote_catalog"
        ) as write_catalog:
            document = operations.build_catalog("tgod:_Money/2026")

        self.assertEqual([entry.filename for entry in document.entries], ["one.csv", "two.pdf"])
        self.assertEqual(document.entries[0].tags, ["from:irs"])
        write_catalog.assert_called_once()

    def test_sync_catalog_removes_missing_files(self) -> None:
        existing = catalog.CatalogDocument(
            context="tgod:_Money/2026",
            entries=[catalog.CatalogEntry(filename="old.csv", tags=["type:summary"])],
        )
        remote_files = [rclone.RemoteFile(path="new.csv", name="new.csv")]

        with patch.object(operations.rclone, "ensure_rclone_ready", return_value=rclone.RcloneStatus(True, True)), patch.object(
            operations, "load_remote_catalog", return_value=existing
        ), patch.object(operations, "list_supported_files", return_value=remote_files), patch.object(
            operations, "derive_tags_for_remote_file", return_value=["from:irs"]
        ), patch.object(operations, "write_remote_catalog") as write_catalog:
            document = operations.sync_catalog("tgod:_Money/2026")

        self.assertEqual([entry.filename for entry in document.entries], ["new.csv"])
        self.assertEqual(document.entries[0].tags, ["from:irs"])
        write_catalog.assert_called_once()

    def test_add_and_remove_entry(self) -> None:
        existing = catalog.CatalogDocument(context="tgod:_Money/2026", entries=[])
        remote_files = [rclone.RemoteFile(path="added.csv", name="added.csv")]

        with patch.object(operations.rclone, "ensure_rclone_ready", return_value=rclone.RcloneStatus(True, True)), patch.object(
            operations, "load_remote_catalog", return_value=existing
        ), patch.object(operations, "list_supported_files", return_value=remote_files), patch.object(
            operations, "derive_tags_for_remote_file", return_value=["type:statement"]
        ), patch.object(operations, "write_remote_catalog"):
            document = operations.add_file("tgod:_Money/2026", "added.csv")

        self.assertEqual([entry.filename for entry in document.entries], ["added.csv"])
        self.assertEqual(document.entries[0].tags, ["type:statement"])

        with patch.object(operations.rclone, "ensure_rclone_ready", return_value=rclone.RcloneStatus(True, True)), patch.object(
            operations, "load_remote_catalog", return_value=document
        ), patch.object(operations, "write_remote_catalog") as write_catalog:
            updated = operations.remove_file("tgod:_Money/2026", "added.csv")

        self.assertEqual(updated.entries, [])
        write_catalog.assert_called_once()


if __name__ == "__main__":
    unittest.main()
