from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, inspect, text


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


def _migration_config(database_path: Path) -> Config:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")
    return config


def _insert_phase0_configuration(engine, *, model_year_from: int | None, identity_time_basis: str | None = None) -> str:
    manufacturer_id = str(uuid4())
    model_id = str(uuid4())
    configuration_id = str(uuid4())
    values = {
        "manufacturer_id": manufacturer_id,
        "model_id": model_id,
        "configuration_id": configuration_id,
        "stable_vehicle_code": f"MIGRATION-{configuration_id[:8]}",
        "model_year_from": model_year_from,
        "identity_time_basis": identity_time_basis,
    }
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO manufacturer "
                "(id, canonical_name, display_name, country_of_origin, active) "
                "VALUES (:manufacturer_id, 'Migration Fixtures', 'Migration Fixtures', 'TH', 1)"
            ),
            values,
        )
        connection.execute(
            text(
                "INSERT INTO vehicle_model "
                "(id, manufacturer_id, canonical_model_name, display_model_name) "
                "VALUES (:model_id, :manufacturer_id, 'Migration model', 'Migration model')"
            ),
            values,
        )
        if identity_time_basis is None:
            connection.execute(
                text(
                    "INSERT INTO vehicle_configuration "
                    "(id, stable_vehicle_code, vehicle_model_id, market_code, generation_name, "
                    "chassis_platform_code, body_style, model_year_from, model_year_to, "
                    "sale_period_from, sale_period_to, variant_trim, powertrain, drivetrain, "
                    "body_configuration, identity_notes, identity_verification_state, created_at, updated_at) "
                    "VALUES (:configuration_id, :stable_vehicle_code, :model_id, 'TEST', "
                    "'migration generation', 'MIGRATION', 'fixture', :model_year_from, NULL, NULL, NULL, "
                    "'migration variant', NULL, NULL, NULL, 'migration fixture', 'RESOLVED_EXACT', "
                    "'2026-08-31 00:00:00.000000', '2026-08-31 00:00:00.000000')"
                ),
                values,
            )
        else:
            values["identity_time_label_raw"] = "35th Anniversary Edition"
            connection.execute(
                text(
                    "INSERT INTO vehicle_configuration "
                    "(id, stable_vehicle_code, vehicle_model_id, market_code, generation_name, "
                    "chassis_platform_code, body_style, model_year_from, model_year_to, identity_time_basis, "
                    "identity_time_label_raw, sale_period_from, sale_period_to, variant_trim, powertrain, "
                    "drivetrain, body_configuration, identity_notes, identity_verification_state, created_at, updated_at) "
                    "VALUES (:configuration_id, :stable_vehicle_code, :model_id, 'TEST', "
                    "'migration generation', 'MIGRATION', 'fixture', :model_year_from, NULL, :identity_time_basis, "
                    ":identity_time_label_raw, NULL, NULL, 'migration variant', NULL, NULL, NULL, 'migration fixture', "
                    "'RESOLVED_EXACT', '2026-08-31 00:00:00.000000', '2026-08-31 00:00:00.000000')"
                ),
                values,
            )
    return values["stable_vehicle_code"]


def test_existing_phase0_rows_upgrade_and_backfill_without_data_loss(tmp_path):
    database_path = tmp_path / "existing-phase0.sqlite"
    config = _migration_config(database_path)
    command.upgrade(config, "0001_phase0_foundation")
    engine = create_engine(f"sqlite:///{database_path}")
    stable_code = _insert_phase0_configuration(engine, model_year_from=2024)

    command.upgrade(config, "head")

    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT model_year_from, model_year_to, identity_time_basis, identity_time_label_raw "
                "FROM vehicle_configuration WHERE stable_vehicle_code = :stable_code"
            ),
            {"stable_code": stable_code},
        ).one()
    assert row == (2024, None, "MODEL_YEAR", None)
    columns = {column["name"]: column for column in inspect(engine).get_columns("vehicle_configuration")}
    assert columns["model_year_from"]["nullable"] is True
    assert columns["identity_time_basis"]["nullable"] is False
    assert columns["identity_time_label_raw"]["nullable"] is True
    engine.dispose()


def test_downgrade_refuses_non_model_year_rows_without_fabricating_a_year(tmp_path):
    database_path = tmp_path / "non-model-year.sqlite"
    config = _migration_config(database_path)
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database_path}")
    stable_code = _insert_phase0_configuration(
        engine,
        model_year_from=None,
        identity_time_basis="EDITION_RELEASE",
    )

    with pytest.raises(RuntimeError, match="cannot be restored without fabricating a year"):
        command.downgrade(config, "0001_phase0_foundation")

    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT model_year_from, identity_time_basis, identity_time_label_raw "
                "FROM vehicle_configuration WHERE stable_vehicle_code = :stable_code"
            ),
            {"stable_code": stable_code},
        ).one()
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    assert row == (None, "EDITION_RELEASE", "35th Anniversary Edition")
    assert revision == "0002_identity_time_basis"
    engine.dispose()


def test_model_year_rows_can_downgrade_to_0001_and_reupgrade_safely(tmp_path):
    database_path = tmp_path / "roundtrip-existing.sqlite"
    config = _migration_config(database_path)
    command.upgrade(config, "0001_phase0_foundation")
    engine = create_engine(f"sqlite:///{database_path}")
    stable_code = _insert_phase0_configuration(engine, model_year_from=2025)
    command.upgrade(config, "head")

    command.downgrade(config, "0001_phase0_foundation")
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT model_year_from FROM vehicle_configuration WHERE stable_vehicle_code = :stable_code"),
            {"stable_code": stable_code},
        ).scalar_one()
        columns = {column["name"] for column in inspect(engine).get_columns("vehicle_configuration")}
    assert row == 2025
    assert "identity_time_basis" not in columns
    assert "identity_time_label_raw" not in columns

    command.upgrade(config, "head")
    with engine.connect() as connection:
        assert connection.execute(
            text("SELECT identity_time_basis FROM vehicle_configuration WHERE stable_vehicle_code = :stable_code"),
            {"stable_code": stable_code},
        ).scalar_one() == "MODEL_YEAR"
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
    assert "ADD COLUMN identity_time_basis VARCHAR(32)" in ddl
    assert "ADD COLUMN identity_time_label_raw VARCHAR(240)" in ddl
    assert "ALTER COLUMN model_year_from DROP NOT NULL" in ddl
    assert "identity_time_basis IN ('MODEL_YEAR', 'OEM_REVISION_LABEL', 'EDITION_RELEASE', 'SALE_PERIOD', 'MULTIPLE', 'UNKNOWN')" in ddl
