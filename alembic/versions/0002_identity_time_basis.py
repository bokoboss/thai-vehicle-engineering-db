"""Add an evidence-backed temporal identity basis to vehicle configurations.

Revision ID: 0002_identity_time_basis
Revises: 0001_phase0_foundation
Create Date: 2026-08-31
"""

from alembic import context, op
import sqlalchemy as sa


revision = "0002_identity_time_basis"
down_revision = "0001_phase0_foundation"
branch_labels = None
depends_on = None


IDENTITY_TIME_BASIS_VALUES = (
    "MODEL_YEAR",
    "OEM_REVISION_LABEL",
    "EDITION_RELEASE",
    "SALE_PERIOD",
    "MULTIPLE",
    "UNKNOWN",
)
IDENTITY_TIME_BASIS_CHECK = "identity_time_basis IN (" + ", ".join(
    f"'{value}'" for value in IDENTITY_TIME_BASIS_VALUES
) + ")"
OLD_MODEL_YEAR_RANGE_CHECK = "model_year_to IS NULL OR model_year_to >= model_year_from"
NULLABLE_MODEL_YEAR_RANGE_CHECK = "model_year_from IS NULL OR model_year_to IS NULL OR model_year_to >= model_year_from"


def _dialect_name() -> str:
    if context.is_offline_mode():
        return context.get_context().dialect.name
    return op.get_bind().dialect.name


def _add_identity_columns_and_nullable_model_year() -> None:
    if _dialect_name() == "sqlite":
        with op.batch_alter_table("vehicle_configuration", recreate="always") as batch_op:
            batch_op.add_column(sa.Column("identity_time_basis", sa.String(length=32), nullable=True))
            batch_op.add_column(sa.Column("identity_time_label_raw", sa.String(length=240), nullable=True))
            batch_op.alter_column("model_year_from", existing_type=sa.Integer(), nullable=True)
            batch_op.drop_constraint("ck_vehicle_configuration_valid_model_year_range", type_="check")
            batch_op.create_check_constraint(
                "ck_vehicle_configuration_valid_model_year_range",
                NULLABLE_MODEL_YEAR_RANGE_CHECK,
            )
        return

    op.add_column(
        "vehicle_configuration",
        sa.Column("identity_time_basis", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "vehicle_configuration",
        sa.Column("identity_time_label_raw", sa.String(length=240), nullable=True),
    )
    op.alter_column("vehicle_configuration", "model_year_from", existing_type=sa.Integer(), nullable=True)
    op.drop_constraint("ck_vehicle_configuration_valid_model_year_range", "vehicle_configuration", type_="check")
    op.create_check_constraint(
        "ck_vehicle_configuration_valid_model_year_range",
        "vehicle_configuration",
        NULLABLE_MODEL_YEAR_RANGE_CHECK,
    )


def _make_identity_basis_required() -> None:
    if _dialect_name() == "sqlite":
        with op.batch_alter_table("vehicle_configuration", recreate="always") as batch_op:
            batch_op.alter_column("identity_time_basis", existing_type=sa.String(length=32), nullable=False)
            batch_op.create_check_constraint(
                "ck_vehicle_configuration_valid_identity_time_basis",
                IDENTITY_TIME_BASIS_CHECK,
            )
        return

    op.alter_column("vehicle_configuration", "identity_time_basis", existing_type=sa.String(length=32), nullable=False)
    op.create_check_constraint(
        "ck_vehicle_configuration_valid_identity_time_basis",
        "vehicle_configuration",
        IDENTITY_TIME_BASIS_CHECK,
    )


def _assert_backfill_complete() -> None:
    if context.is_offline_mode():
        return
    remaining = op.get_bind().execute(
        sa.text("SELECT COUNT(*) FROM vehicle_configuration WHERE identity_time_basis IS NULL")
    ).scalar_one()
    if remaining:
        raise RuntimeError(
            "0002_identity_time_basis backfill failed: "
            f"{remaining} vehicle_configuration row(s) have NULL identity_time_basis"
        )


def upgrade() -> None:
    """Make model year optional and backfill the new controlled time basis."""

    _add_identity_columns_and_nullable_model_year()
    op.execute(
        sa.text(
            "UPDATE vehicle_configuration "
            "SET identity_time_basis = 'MODEL_YEAR' "
            "WHERE model_year_from IS NOT NULL"
        )
    )
    _assert_backfill_complete()
    _make_identity_basis_required()


def _assert_safe_downgrade_precondition() -> None:
    if context.is_offline_mode():
        raise RuntimeError(
            "Cannot safely downgrade 0002_identity_time_basis in offline mode; "
            "run the downgrade online so NULL model_year_from rows can be checked"
        )
    non_model_year_rows = op.get_bind().execute(
        sa.text("SELECT COUNT(*) FROM vehicle_configuration WHERE model_year_from IS NULL")
    ).scalar_one()
    if non_model_year_rows:
        raise RuntimeError(
            "Cannot safely downgrade 0002_identity_time_basis: "
            f"{non_model_year_rows} vehicle_configuration row(s) have NULL model_year_from; "
            "the old NOT NULL model-year contract cannot be restored without fabricating a year"
        )


def _restore_required_model_year_and_remove_identity_columns() -> None:
    if _dialect_name() == "sqlite":
        with op.batch_alter_table("vehicle_configuration", recreate="always") as batch_op:
            batch_op.drop_constraint("ck_vehicle_configuration_valid_identity_time_basis", type_="check")
            batch_op.drop_constraint("ck_vehicle_configuration_valid_model_year_range", type_="check")
            batch_op.drop_column("identity_time_label_raw")
            batch_op.drop_column("identity_time_basis")
            batch_op.alter_column("model_year_from", existing_type=sa.Integer(), nullable=False)
            batch_op.create_check_constraint(
                "ck_vehicle_configuration_valid_model_year_range",
                OLD_MODEL_YEAR_RANGE_CHECK,
            )
        return

    op.drop_constraint("ck_vehicle_configuration_valid_identity_time_basis", "vehicle_configuration", type_="check")
    op.drop_constraint("ck_vehicle_configuration_valid_model_year_range", "vehicle_configuration", type_="check")
    op.drop_column("vehicle_configuration", "identity_time_label_raw")
    op.drop_column("vehicle_configuration", "identity_time_basis")
    op.alter_column("vehicle_configuration", "model_year_from", existing_type=sa.Integer(), nullable=False)
    op.create_check_constraint(
        "ck_vehicle_configuration_valid_model_year_range",
        "vehicle_configuration",
        OLD_MODEL_YEAR_RANGE_CHECK,
    )


def downgrade() -> None:
    """Restore 0001 only when every configuration still has a model year."""

    _assert_safe_downgrade_precondition()
    _restore_required_model_year_and_remove_identity_columns()
