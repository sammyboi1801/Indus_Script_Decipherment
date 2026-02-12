#!/usr/bin/env python3
"""Validate config.yaml against scripts/config.schema.json."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.yaml"
SCHEMA_PATH = ROOT / "scripts" / "config.schema.json"


def main() -> None:
    with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
        schema = json.load(schema_file)

    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    jsonschema.validate(instance=config, schema=schema)
    print(f"Config is valid: {CONFIG_PATH}")


if __name__ == "__main__":
    main()
