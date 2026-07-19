from __future__ import annotations

import argparse
import json
from typing import Callable

from scripts._bootstrap import ensure_src_path

ensure_src_path()

from storage_made_simple import operations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synchronize a folder catalog with folder contents.")
    parser.add_argument("folder", help="rclone path to the folder")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None, syncer: Callable[[str], object] = operations.sync_catalog) -> int:
    args = build_parser().parse_args(argv)
    document = syncer(args.folder)
    payload = document.to_dict() if hasattr(document, "to_dict") else document
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        count = len(payload.get("files", [])) if isinstance(payload, dict) else "?"
        print(f"synced={args.folder} files={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
