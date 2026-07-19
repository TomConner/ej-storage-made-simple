from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from storage_made_simple.mcp_server import build_server


class ServerTests(unittest.TestCase):
    def test_expected_tools_are_registered(self) -> None:
        server = build_server()
        tool_names = [tool.name for tool in server.tools]

        self.assertEqual(
            tool_names,
            [
                "detect_rclone_setup",
                "scan_folder",
                "build_catalog",
                "sync_catalog",
                "add_file",
                "remove_file",
                "replace_file",
            ],
        )


if __name__ == "__main__":
    unittest.main()
