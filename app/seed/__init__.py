from __future__ import annotations

import argparse

from app.db.session import SessionLocal
from app.seed.fixtures import seed_phase0_fixtures
from app.seed.registry import seed_registry


def seed_database() -> None:
    session = SessionLocal()
    try:
        seed_registry(session)
        seed_phase0_fixtures(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the parameter registry and Phase 0 semantic fixtures")
    parser.parse_args()
    seed_database()
    print("Seeded parameter registry and Phase 0 semantic fixtures.")


if __name__ == "__main__":
    main()
