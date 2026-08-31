from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


PHASE_0_TABLES = {
    "manufacturer",
    "vehicle_model",
    "vehicle_configuration",
    "vehicle_fitment",
    "axle",
    "steering_relation",
    "load_condition",
    "source_document",
    "source_observation",
    "parameter_definition",
    "normalized_value",
    "evidence_link",
    "parameter_assessment",
    "derivation_rule",
    "derivation_run",
    "derivation_input",
    "conflict_decision",
    "geometry_asset",
    "readiness_result",
    "qa_finding",
    "avt_mapping_result",
}


def test_migration_upgrade_downgrade_and_reupgrade(tmp_path):
    database_path = tmp_path / "migration.sqlite"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database_path}")
    tables = set(inspect(engine).get_table_names())
    assert tables == PHASE_0_TABLES | {"alembic_version"}
    command.downgrade(config, "base")
    assert set(inspect(engine).get_table_names()) == {"alembic_version"}
    command.upgrade(config, "head")
    assert set(inspect(engine).get_table_names()) == PHASE_0_TABLES | {"alembic_version"}
    engine.dispose()


def test_revision_0001_is_frozen_and_self_contained():
    source = Path("alembic/versions/0001_phase0_foundation.py").read_text(encoding="utf-8")
    assert "from app.db.base import Base" not in source
    assert "Base.metadata" not in source
    assert "create_all(" not in source
    assert "drop_all(" not in source
    assert source.count("op.create_table(") == len(PHASE_0_TABLES)
    assert source.count("op.drop_table(") == len(PHASE_0_TABLES)


def test_revision_0001_generates_postgresql_compatible_offline_ddl():
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", "postgresql://phase0:phase0@example.invalid/phase0")
    output = StringIO()
    with redirect_stdout(output):
        command.upgrade(config, "head", sql=True)
    ddl = output.getvalue()
    assert "CREATE TABLE manufacturer" in ddl
    assert "CREATE TABLE normalized_value" in ddl
    assert "CREATE TABLE derivation_input" in ddl
    assert "CREATE INDEX ix_normalized_value_states" in ddl
