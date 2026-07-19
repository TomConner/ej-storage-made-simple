from __future__ import annotations

import argparse
import json
from typing import Callable

from scripts._bootstrap import ensure_src_path

ensure_src_path()

from storage_made_simple.rclone import detect_rclone_setup


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect rclone setup.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: list[str] | None = None, detector: Callable[[], object] = detect_rclone_setup) -> int:
    args = build_parser().parse_args(argv)
    status = detector()
    if hasattr(status, "to_dict"):
        payload = status.to_dict()
        installed = bool(payload.get("installed"))
        configured = bool(payload.get("configured"))
    else:
        payload = status
        installed = bool(getattr(status, "installed", False))
        configured = bool(getattr(status, "configured", False))

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"installed={installed} configured={configured}")
    return 0 if installed and configured else 1


if __name__ == "__main__":
    raise SystemExit(main())
