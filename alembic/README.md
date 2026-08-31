# Migrations

The Phase 0 schema is represented by the SQLAlchemy metadata imported by
`alembic/versions/0001_phase0_foundation.py`. Alembic owns the upgrade and
rollback boundary; the same metadata is portable across SQLite and PostgreSQL.
