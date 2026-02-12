#!/usr/bin/env python3
"""Validate that all JSON files under data/ parse successfully."""

from __future__ import annotations

import json
import sys
from pathlib import Path


DATA_ROOT = Path("data")


def main() -> int:
    json_files = sorted(DATA_ROOT.glob("**/*.json"))

    if not json_files:
        print("No JSON files found under data/.")
        return 0

    has_errors = False
    for json_file in json_files:
        try:
            json.loads(json_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            has_errors = True
            print(
                f"PARSE ERROR: {json_file}:{exc.lineno}:{exc.colno} - {exc.msg}",
                file=sys.stderr,
            )

    if has_errors:
        return 1

    print(f"Validated {len(json_files)} JSON file(s) under data/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
