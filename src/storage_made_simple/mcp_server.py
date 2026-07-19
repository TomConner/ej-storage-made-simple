from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from typing import Any, Callable

from storage_made_simple import operations, rclone


@dataclass(slots=True)
class ToolSpec:
    name: str
    description: str
    handler: Callable[..., Any]


@dataclass(slots=True)
class SimpleMCPServer:
    name: str
    description: str
    tools: list[ToolSpec] = field(default_factory=list)

    def tool(self, name: str | None = None, description: str = "") -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            tool_name = name or func.__name__
            self.tools.append(ToolSpec(name=tool_name, description=description or func.__doc__ or "", handler=func))
            return func

        return decorator

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "tools": [
                {"name": tool.name, "description": tool.description}
                for tool in self.tools
            ],
        }


def build_server() -> SimpleMCPServer:
    server = SimpleMCPServer(
        name="storage-made-simple",
        description="MCP-style scaffold for rclone-backed document catalogs.",
    )

    @server.tool(description="Detect whether rclone is installed and configured.")
    def detect_rclone_setup() -> dict[str, Any]:
        return rclone.detect_rclone_setup().to_dict()

    @server.tool(description="List supported files in an rclone folder without modifying the catalog.")
    def scan_folder(remote_folder: str) -> list[str]:
        return operations.scan_folder(remote_folder)

    @server.tool(description="Build a fresh `_catalog.jsonld` for an rclone folder.")
    def build_catalog(remote_folder: str) -> dict[str, Any]:
        return operations.build_catalog(remote_folder).to_dict()

    @server.tool(description="Reconcile folder contents with `_catalog.jsonld`.")
    def sync_catalog(remote_folder: str) -> dict[str, Any]:
        return operations.sync_catalog(remote_folder).to_dict()

    @server.tool(description="Add one file entry to `_catalog.jsonld` after the file appears in the folder.")
    def add_file(remote_folder: str, filename: str) -> dict[str, Any]:
        return operations.add_file(remote_folder, filename).to_dict()

    @server.tool(description="Remove one file entry from `_catalog.jsonld` after the file is deleted.")
    def remove_file(remote_folder: str, filename: str) -> dict[str, Any]:
        return operations.remove_file(remote_folder, filename).to_dict()

    @server.tool(description="Replace one file entry in `_catalog.jsonld` after a file swap.")
    def replace_file(remote_folder: str, filename: str, previous_filename: str | None = None) -> dict[str, Any]:
        return operations.replace_file(remote_folder, filename, previous_filename).to_dict()

    return server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect the storage-made-simple MCP scaffold.")
    parser.add_argument("--json", action="store_true", help="Print the server description as JSON.")
    args = parser.parse_args(argv)

    server = build_server()
    if args.json:
        print(json.dumps(server.describe(), indent=2))
    else:
        for tool in server.tools:
            print(f"{tool.name}: {tool.description}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
