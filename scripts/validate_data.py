#!/usr/bin/env python3
"""Verify the checked-in CSV files without printing their record contents."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_manifest(path: Path) -> list[dict]:
    """Load and check the small manifest before opening any data files."""
    with path.open(encoding="utf-8") as source:
        manifest = json.load(source)
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("manifest must have schema_version 1")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("manifest must contain a nonempty files list")
    seen = set()
    for entry in files:
        if not isinstance(entry, dict):
            raise ValueError("each manifest file must be an object")
        name = entry.get("path")
        if not isinstance(name, str):
            raise ValueError("each manifest file must have a relative path")
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or "\\" in name or ":" in name:
            raise ValueError("manifest paths must stay within the repository")
        if relative.suffix.lower() != ".csv" or name in seen:
            raise ValueError("manifest paths must be unique CSV files")
        seen.add(name)
        for field in ("rows", "bytes"):
            if type(entry.get(field)) is not int or entry[field] < 0:
                raise ValueError(f"{name}: {field} must be a nonnegative integer")
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"{name}: sha256 must be 64 lowercase hexadecimal characters")
        columns = entry.get("columns")
        if not isinstance(columns, list) or not columns or not all(
            isinstance(column, str) and column for column in columns
        ):
            raise ValueError(f"{name}: columns must be a nonempty list of column names")
    return files


def validate_file(path: Path, expected: dict, quick: bool = False) -> list[str]:
    """Return integrity errors; CSV records and hash chunks are never accumulated."""
    errors = []
    label = expected["path"]
    try:
        if not path.is_file():
            return [f"{label}: missing file"]
        size = path.stat().st_size
        if size != expected["bytes"]:
            errors.append(f"{label}: size mismatch (expected {expected['bytes']}, got {size})")
        # Buffered decoding may read past the header. In quick mode, an invalid
        # body byte must not turn a header-only check into a full encoding check.
        decoding_errors = "surrogateescape" if quick else "strict"
        with path.open(encoding="utf-8-sig", errors=decoding_errors, newline="") as source:
            reader = csv.reader(source, strict=True)
            header = next(reader, None)
            if header != expected["columns"]:
                errors.append(f"{label}: header mismatch")
            if not quick:
                rows = 0
                invalid_width = 0
                first_invalid_line = None
                width = len(expected["columns"])
                for record in reader:
                    rows += 1
                    if len(record) != width:
                        invalid_width += 1
                        if first_invalid_line is None:
                            first_invalid_line = reader.line_num
                if invalid_width:
                    errors.append(
                        f"{label}: row width mismatch in {invalid_width} record(s) "
                        f"(first ending at CSV line {first_invalid_line})"
                    )
                if rows != expected["rows"]:
                    errors.append(f"{label}: row count mismatch (expected {expected['rows']}, got {rows})")
        if not quick:
            digest = hashlib.sha256()
            with path.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != expected["sha256"]:
                errors.append(f"{label}: SHA-256 mismatch")
    except csv.Error as error:
        errors.append(f"{label}: invalid CSV ({error})")
    except UnicodeError:
        errors.append(f"{label}: invalid UTF-8 encoding")
    except OSError as error:
        errors.append(f"{label}: cannot read file ({error.strerror})")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="check only existence, byte size and header")
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "data" / "manifest.json")
    parser.add_argument("--data-dir", type=Path, help="override the directory containing the manifest's CSV filenames")
    args = parser.parse_args(argv)
    try:
        files = load_manifest(args.manifest)
    except (OSError, ValueError, UnicodeError) as error:
        print(f"ERROR: cannot load manifest: {error}", file=sys.stderr)
        return 2
    errors = []
    for entry in files:
        relative = PurePosixPath(entry["path"])
        path = args.data_dir / relative.name if args.data_dir else REPO_ROOT.joinpath(*relative.parts)
        errors.extend(validate_file(path, entry, args.quick))
    mode = "quick" if args.quick else "full"
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAIL: {len(files)} file(s), {len(errors)} error(s) ({mode})", file=sys.stderr)
        return 1
    print(f"PASS: {len(files)} file(s) ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
