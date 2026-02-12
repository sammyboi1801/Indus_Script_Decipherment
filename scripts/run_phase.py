#!/usr/bin/env python3
"""Simple phase runner scaffold for scripted pipeline steps."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a scaffolded pipeline phase.")
    parser.add_argument("phase", type=int, help="Pipeline phase ID from config.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    phase = next((p for p in config["pipeline"]["phases"] if p["id"] == args.phase), None)
    if phase is None:
        raise SystemExit(f"Unknown phase '{args.phase}'. Check config.yaml pipeline.phases.")

    phase_dir = ROOT / phase["script_dir"]
    print(f"[scaffold] Running phase {phase['id']}: {phase['name']}")
    print(f"[scaffold] Expected script directory: {phase_dir}")
    print("[scaffold] Add phase execution entrypoints in this directory.")


if __name__ == "__main__":
    main()
