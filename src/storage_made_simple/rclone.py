from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class RcloneError(RuntimeError):
    """Raised when an rclone command fails."""


@dataclass(slots=True)
class RemoteFile:
    path: str
    name: str
    size: int | None = None
    mime_type: str | None = None
    mod_time: str | None = None
    is_dir: bool = False

    @classmethod
    def from_lsjson(cls, payload: dict[str, Any]) -> "RemoteFile":
        path = str(payload.get("Path") or payload.get("Name") or "").strip()
        name = str(payload.get("Name") or path).strip()
        return cls(
            path=path,
            name=name,
            size=payload.get("Size"),
            mime_type=payload.get("MimeType"),
            mod_time=payload.get("ModTime"),
            is_dir=bool(payload.get("IsDir", False)),
        )


@dataclass(slots=True)
class RcloneStatus:
    installed: bool
    configured: bool
    version: str | None = None
    config_file: str | None = None
    remotes: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "installed": self.installed,
            "configured": self.configured,
            "version": self.version,
            "config_file": self.config_file,
            "remotes": list(self.remotes),
            "notes": list(self.notes),
        }


def is_rclone_path(value: str) -> bool:
    return ":" in value and not value.startswith(":")


def split_rclone_path(value: str) -> tuple[str, str]:
    if not is_rclone_path(value):
        raise ValueError(f"Not an rclone path: {value!r}")
    remote, relative = value.split(":", 1)
    return remote, relative.lstrip("/")


def join_rclone_path(base: str, member: str) -> str:
    if not is_rclone_path(base):
        raise ValueError(f"Not an rclone path: {base!r}")
    base = base.rstrip("/")
    member = member.lstrip("/")
    if not member:
        return base
    return f"{base}/{member}"


def _decode_output(result: subprocess.CompletedProcess[bytes]) -> str:
    return (result.stdout or b"").decode("utf-8", errors="replace").strip()


def run_rclone(args: list[str], *, input_bytes: bytes | None = None, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        ["rclone", *args],
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        stderr = (completed.stderr or b"").decode("utf-8", errors="replace").strip()
        raise RcloneError(stderr or f"rclone {' '.join(args)} failed")
    return completed


def detect_rclone_setup() -> RcloneStatus:
    binary = shutil.which("rclone")
    if not binary:
        return RcloneStatus(
            installed=False,
            configured=False,
            notes=("rclone is not installed",),
        )

    notes: list[str] = []
    version: str | None = None
    config_file: str | None = None
    remotes: tuple[str, ...] = ()

    try:
        version_result = run_rclone(["--version"], check=True)
        version_lines = _decode_output(version_result).splitlines()
        if version_lines:
            version = version_lines[0].strip()
    except RcloneError as exc:
        notes.append(str(exc))

    try:
        config_result = run_rclone(["config", "file"], check=True)
        config_text = _decode_output(config_result)
        match = re.search(r"(?P<path>(?:[A-Za-z]:)?[\\/][^\n\r]+(?:rclone\.conf|\.conf))", config_text)
        if match:
            config_file = match.group("path")
        else:
            lines = [line.strip() for line in config_text.splitlines() if line.strip()]
            if lines:
                config_file = lines[-1]
    except RcloneError as exc:
        notes.append(str(exc))

    try:
        remotes_result = run_rclone(["listremotes"], check=True)
        remote_names = []
        for line in _decode_output(remotes_result).splitlines():
            line = line.strip()
            if not line:
                continue
            remote_names.append(line[:-1] if line.endswith(":") else line)
        remotes = tuple(remote_names)
    except RcloneError as exc:
        notes.append(str(exc))

    configured = bool(remotes) or bool(config_file)
    if not configured:
        notes.append("rclone is installed but no remotes were detected")

    return RcloneStatus(
        installed=True,
        configured=configured,
        version=version,
        config_file=config_file,
        remotes=remotes,
        notes=tuple(notes),
    )


def ensure_rclone_ready() -> RcloneStatus:
    status = detect_rclone_setup()
    if not status.installed:
        raise RcloneError("rclone is not installed")
    if not status.configured:
        raise RcloneError("rclone is installed, but no configured remotes were detected")
    return status


def list_remote_files(remote_folder: str) -> list[RemoteFile]:
    result = run_rclone(["lsjson", "--files-only", remote_folder], check=True)
    payload = json.loads(_decode_output(result) or "[]")
    if not isinstance(payload, list):
        raise RcloneError("Unexpected lsjson output")
    return [RemoteFile.from_lsjson(item) for item in payload if isinstance(item, dict)]


def read_remote_bytes(remote_file: str) -> bytes:
    result = run_rclone(["cat", remote_file], check=True)
    return result.stdout or b""


def write_remote_text(remote_file: str, text: str) -> None:
    run_rclone(["rcat", remote_file], input_bytes=text.encode("utf-8"), check=True)

