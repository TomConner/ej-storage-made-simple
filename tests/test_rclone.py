from __future__ import annotations

import sys
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from storage_made_simple.rclone import RcloneStatus, detect_rclone_setup, is_rclone_path, join_rclone_path


class RcloneTests(unittest.TestCase):
    def test_path_helpers(self) -> None:
        self.assertTrue(is_rclone_path("tgod:_Money/2026"))
        self.assertEqual(join_rclone_path("tgod:_Money/2026", "file.pdf"), "tgod:_Money/2026/file.pdf")

    def test_detect_missing_rclone(self) -> None:
        with patch("storage_made_simple.rclone.shutil.which", return_value=None):
            status = detect_rclone_setup()

        self.assertFalse(status.installed)
        self.assertFalse(status.configured)

    def test_detect_configured_rclone(self) -> None:
        def fake_run(args, input_bytes=None, check=True):
            if args == ["--version"]:
                return CompletedProcess(args=["rclone", *args], returncode=0, stdout=b"rclone v1.67.0\n", stderr=b"")
            if args == ["config", "file"]:
                return CompletedProcess(
                    args=["rclone", *args],
                    returncode=0,
                    stdout=b"Configuration file is stored at:\n/Users/test/.config/rclone/rclone.conf\n",
                    stderr=b"",
                )
            if args == ["listremotes"]:
                return CompletedProcess(args=["rclone", *args], returncode=0, stdout=b"tgod:\n", stderr=b"")
            raise AssertionError(f"unexpected args: {args!r}")

        with patch("storage_made_simple.rclone.shutil.which", return_value="/usr/bin/rclone"), patch(
            "storage_made_simple.rclone.run_rclone", side_effect=fake_run
        ):
            status = detect_rclone_setup()

        self.assertIsInstance(status, RcloneStatus)
        self.assertTrue(status.installed)
        self.assertTrue(status.configured)
        self.assertEqual(status.remotes, ("tgod",))
        self.assertTrue(status.version.startswith("rclone v1.67.0"))


if __name__ == "__main__":
    unittest.main()
