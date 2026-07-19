from __future__ import annotations

import argparse
import json
from typing import Callable

from scripts._bootstrap import ensure_src_path

ensure_src_path()

from storage_made_simple import operations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update one catalog entry.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    add_parser = subparsers.add_parser("add", help="Add or refresh one entry.")
    add_parser.add_argument("folder", help="rclone path to the folder")
    add_parser.add_argument("filename", help="file name inside the folder")

    remove_parser = subparsers.add_parser("remove", help="Remove one entry.")
    remove_parser.add_argument("folder", help="rclone path to the folder")
    remove_parser.add_argument("filename", help="file name inside the folder")

    replace_parser = subparsers.add_parser("replace", help="Replace one entry.")
    replace_parser.add_argument("folder", help="rclone path to the folder")
    replace_parser.add_argument("filename", help="current file name inside the folder")
    replace_parser.add_argument(
        "--previous-filename",
        dest="previous_filename",
        help="stale filename to remove before writing the new entry",
    )
    return parser


def main(
    argv: list[str] | None = None,
    *,
    add_handler: Callable[[str, str], object] = operations.add_file,
    remove_handler: Callable[[str, str], object] = operations.remove_file,
    replace_handler: Callable[[str, str, str | None], object] = operations.replace_file,
) -> int:
    args = build_parser().parse_args(argv)
    if args.action == "add":
        document = add_handler(args.folder, args.filename)
    elif args.action == "remove":
        document = remove_handler(args.folder, args.filename)
    else:
        document = replace_handler(args.folder, args.filename, args.previous_filename)
    payload = document.to_dict() if hasattr(document, "to_dict") else document
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
