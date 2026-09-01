"""Compatibility entry point for reproducing the accepted Wave 1 release.

The generic release builder is the maintained implementation.  This module is
kept because historical tests and qualification notes use the Wave 1 command.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import build_curated_db as generic


ROOT = generic.ROOT
LEGACY_RELEASE_PATH = Path("data/curation/releases/release_2026_08_wave1.json")
BuildError = generic.BuildError
ManifestInventory = generic.ManifestInventory


def collect_inventory(root: Path = ROOT) -> ManifestInventory:
    """Return the explicit historical 21-manifest Wave 1 inventory."""

    return generic.collect_inventory(LEGACY_RELEASE_PATH, root=root)


def _parser() -> argparse.ArgumentParser:
    parser = generic._parser()
    parser.description = "Build the historical accepted Wave 1 curated SQLite database"
    parser.set_defaults(
        release=LEGACY_RELEASE_PATH,
        csv=Path("vehicle_engineering_curated.wave1.csv"),
        xlsx=Path("vehicle_engineering_curated.wave1.xlsx"),
    )
    return parser


def build(args: argparse.Namespace) -> dict:
    """Run the generic builder against the historical Wave 1 release set."""

    args.release = LEGACY_RELEASE_PATH
    return generic.build(args)


def main(argv: list[str] | None = None) -> int:
    try:
        report = build(_parser().parse_args(argv))
    except (BuildError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
