from __future__ import annotations

import argparse
from typing import Sequence

from app.curate.loader import import_manifest, initialize_registry
from app.curate.report import render_init_report, render_validation_report
from app.curate.validation import CurationError, load_manifest
from app.db.session import SessionLocal


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create-only Phase 1 curation manifest importer")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("init", help="seed the parameter registry only")

    validate = commands.add_parser("validate", help="validate one curation manifest without writes")
    validate.add_argument("manifest", help="path to a manifest JSON file")

    import_command = commands.add_parser("import", help="import one curation manifest")
    import_command.add_argument("manifest", help="path to a manifest JSON file")
    import_command.add_argument(
        "--dry-run",
        action="store_true",
        help="run the complete import path and roll back all writes",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    session = SessionLocal()
    try:
        if args.command == "init":
            count = initialize_registry(session)
            print(render_init_report(count))
            return 0

        manifest = load_manifest(args.manifest)
        if args.command == "validate":
            import_manifest(session, manifest, dry_run=True)
            print(render_validation_report(manifest.vehicle.stable_vehicle_code))
            return 0

        report = import_manifest(session, manifest, dry_run=args.dry_run)
        print(report.render())
        return 0
    except (CurationError, ValueError) as exc:
        session.rollback()
        print(f"FAIL: {exc}")
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
