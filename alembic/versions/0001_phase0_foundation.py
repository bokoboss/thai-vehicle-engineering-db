"""Create the frozen evidence-first Phase 0 relational foundation.

Revision ID: 0001_phase0_foundation
Revises:
Create Date: 2026-08-31
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_phase0_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create exactly the schema owned by this revision.

    Keep this revision self-contained. Later ORM metadata changes must be
    represented by later migrations rather than changing the meaning of 0001.
    """

    op.create_table(
        "manufacturer",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("canonical_name", sa.String(length=160), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("country_of_origin", sa.String(length=80), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_manufacturer"),
        sa.UniqueConstraint("canonical_name", name="uq_manufacturer_canonical_name"),
    )
    op.create_table(
        "parameter_definition",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("parameter_code", sa.String(length=160), nullable=False),
        sa.Column("display_name", sa.String(length=240), nullable=False),
        sa.Column("family", sa.String(length=80), nullable=False),
        sa.Column("data_type", sa.String(length=16), nullable=False),
        sa.Column("canonical_unit", sa.String(length=32), nullable=True),
        sa.Column("semantic_definition", sa.Text(), nullable=True),
        sa.Column("applicability_notes", sa.Text(), nullable=True),
        sa.Column("requires_attributes", sa.JSON(none_as_null=True), nullable=True),
        sa.Column("deprecated", sa.Boolean(), nullable=False),
        sa.Column("replacement_parameter_code", sa.String(length=160), nullable=True),
        sa.Column("created_version", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_parameter_definition"),
        sa.UniqueConstraint("parameter_code", name="uq_parameter_definition_parameter_code"),
    )
    op.create_table(
        "source_document",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_code", sa.String(length=160), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("publisher", sa.String(length=200), nullable=False),
        sa.Column("authority_class", sa.String(length=64), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("market_code", sa.String(length=8), nullable=True),
        sa.Column("publication_year", sa.Integer(), nullable=True),
        sa.Column("model_year_from", sa.Integer(), nullable=True),
        sa.Column("model_year_to", sa.Integer(), nullable=True),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("local_snapshot_reference", sa.String(length=512), nullable=True),
        sa.Column("content_hash", sa.String(length=128), nullable=True),
        sa.Column("page_section_default", sa.String(length=240), nullable=True),
        sa.Column("access_licensing_notes", sa.Text(), nullable=True),
        sa.Column("applicability_notes", sa.Text(), nullable=True),
        sa.Column("archival_status", sa.String(length=80), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_source_document"),
        sa.UniqueConstraint("source_code", name="uq_source_document_source_code"),
    )
    op.create_table(
        "vehicle_model",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("manufacturer_id", sa.String(length=36), nullable=False),
        sa.Column("canonical_model_name", sa.String(length=160), nullable=False),
        sa.Column("display_model_name", sa.String(length=160), nullable=False),
        sa.ForeignKeyConstraint(
            ["manufacturer_id"],
            ["manufacturer.id"],
            name="fk_vehicle_model_manufacturer_id_manufacturer",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_vehicle_model"),
        sa.UniqueConstraint("manufacturer_id", "canonical_model_name", name="uq_vehicle_model_manufacturer_name"),
    )
    op.create_table(
        "vehicle_configuration",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("stable_vehicle_code", sa.String(length=160), nullable=False),
        sa.Column("vehicle_model_id", sa.String(length=36), nullable=False),
        sa.Column("market_code", sa.String(length=8), nullable=False),
        sa.Column("generation_name", sa.String(length=160), nullable=False),
        sa.Column("chassis_platform_code", sa.String(length=120), nullable=True),
        sa.Column("body_style", sa.String(length=80), nullable=False),
        sa.Column("model_year_from", sa.Integer(), nullable=False),
        sa.Column("model_year_to", sa.Integer(), nullable=True),
        sa.Column("sale_period_from", sa.Date(), nullable=True),
        sa.Column("sale_period_to", sa.Date(), nullable=True),
        sa.Column("variant_trim", sa.String(length=180), nullable=False),
        sa.Column("powertrain", sa.String(length=160), nullable=True),
        sa.Column("drivetrain", sa.String(length=80), nullable=True),
        sa.Column("body_configuration", sa.String(length=160), nullable=True),
        sa.Column("identity_notes", sa.Text(), nullable=True),
        sa.Column("identity_verification_state", sa.String(length=48), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "model_year_to IS NULL OR model_year_to >= model_year_from",
            name="ck_vehicle_configuration_valid_model_year_range",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_model_id"],
            ["vehicle_model.id"],
            name="fk_vehicle_configuration_vehicle_model_id_vehicle_model",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_vehicle_configuration"),
        sa.UniqueConstraint("stable_vehicle_code", name="uq_vehicle_configuration_stable_vehicle_code"),
    )
    op.create_table(
        "vehicle_fitment",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=False),
        sa.Column("fitment_code", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("wheel_package", sa.String(length=160), nullable=True),
        sa.Column("equipment_package", sa.String(length=160), nullable=True),
        sa.Column("model_year_from", sa.Integer(), nullable=True),
        sa.Column("model_year_to", sa.Integer(), nullable=True),
        sa.Column("default_for_configuration", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_vehicle_fitment_config",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_vehicle_fitment"),
        sa.UniqueConstraint("vehicle_configuration_id", "fitment_code", name="uq_fitment_configuration_code"),
    )
    op.create_table(
        "axle",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=False),
        sa.Column("axle_role", sa.String(length=32), nullable=False),
        sa.Column("axle_index", sa.Integer(), nullable=False),
        sa.Column("longitudinal_position_mm", sa.Numeric(precision=18, scale=6, asdecimal=False), nullable=True),
        sa.Column("axle_group", sa.String(length=80), nullable=True),
        sa.Column("driven", sa.Boolean(), nullable=True),
        sa.Column("steered", sa.Boolean(), nullable=True),
        sa.Column("retractable", sa.Boolean(), nullable=True),
        sa.Column("self_steering", sa.Boolean(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint("axle_index >= 0", name="ck_axle_nonnegative_axle_index"),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_axle_vehicle_configuration_id_vehicle_configuration",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_axle"),
        sa.UniqueConstraint("vehicle_configuration_id", "axle_index", name="uq_axle_configuration_index"),
    )
    op.create_table(
        "load_condition",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("mass_basis", sa.String(length=32), nullable=False),
        sa.Column("total_mass_kg", sa.Numeric(precision=14, scale=6, asdecimal=False), nullable=True),
        sa.Column("occupant_count", sa.Integer(), nullable=True),
        sa.Column("payload_kg", sa.Numeric(precision=14, scale=6, asdecimal=False), nullable=True),
        sa.Column("front_axle_load_kg", sa.Numeric(precision=14, scale=6, asdecimal=False), nullable=True),
        sa.Column("rear_axle_load_kg", sa.Numeric(precision=14, scale=6, asdecimal=False), nullable=True),
        sa.Column("front_tyre_pressure", sa.Numeric(precision=12, scale=6, asdecimal=False), nullable=True),
        sa.Column("rear_tyre_pressure", sa.Numeric(precision=12, scale=6, asdecimal=False), nullable=True),
        sa.Column("tyre_pressure_unit", sa.String(length=24), nullable=True),
        sa.Column("suspension_mode", sa.String(length=100), nullable=True),
        sa.Column("ride_height_mode", sa.String(length=100), nullable=True),
        sa.Column("raw_oem_wording", sa.Text(), nullable=True),
        sa.Column("source_document_id", sa.String(length=36), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["source_document_id"],
            ["source_document.id"],
            name="fk_load_condition_source_document_id_source_document",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_load_condition_config",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_load_condition"),
    )
    op.create_table(
        "source_observation",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=True),
        sa.Column("vehicle_identity_claim", sa.Text(), nullable=False),
        sa.Column("source_document_id", sa.String(length=36), nullable=False),
        sa.Column("raw_label", sa.String(length=240), nullable=False),
        sa.Column("raw_value", sa.Text(), nullable=False),
        sa.Column("raw_unit", sa.String(length=48), nullable=True),
        sa.Column("raw_qualifier", sa.Text(), nullable=True),
        sa.Column("raw_excerpt", sa.Text(), nullable=True),
        sa.Column("page_section_locator", sa.String(length=240), nullable=True),
        sa.Column("reported_precision", sa.String(length=80), nullable=True),
        sa.Column("uncertainty_value", sa.Numeric(precision=14, scale=6, asdecimal=False), nullable=True),
        sa.Column("uncertainty_unit", sa.String(length=48), nullable=True),
        sa.Column("extraction_method", sa.String(length=48), nullable=False),
        sa.Column("extracted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("extracted_by", sa.String(length=160), nullable=True),
        sa.Column("reviewer", sa.String(length=160), nullable=True),
        sa.Column("ambiguity_note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["source_document_id"],
            ["source_document.id"],
            name="fk_source_observation_source_document_id_source_document",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_source_observation_config",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_source_observation"),
    )
    op.create_table(
        "steering_relation",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=False),
        sa.Column("axle_id", sa.String(length=36), nullable=False),
        sa.Column("steering_role", sa.String(length=32), nullable=False),
        sa.Column("linkage_type", sa.String(length=32), nullable=False),
        sa.Column("max_steering_angle_deg", sa.Numeric(precision=12, scale=6, asdecimal=False), nullable=True),
        sa.Column("phase_behavior", sa.String(length=40), nullable=False),
        sa.Column("angle_ratio", sa.Numeric(precision=12, scale=6, asdecimal=False), nullable=True),
        sa.Column("relation_function", sa.Text(), nullable=True),
        sa.Column("speed_min_kph", sa.Numeric(precision=12, scale=6, asdecimal=False), nullable=True),
        sa.Column("speed_max_kph", sa.Numeric(precision=12, scale=6, asdecimal=False), nullable=True),
        sa.Column("mode_applicability", sa.String(length=160), nullable=True),
        sa.Column("source_observation_id", sa.String(length=36), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["axle_id"], ["axle.id"], name="fk_steering_relation_axle_id_axle"),
        sa.ForeignKeyConstraint(
            ["source_observation_id"],
            ["source_observation.id"],
            name="fk_steering_relation_source_observation_id_source_observation",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_steering_relation_config",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_steering_relation"),
    )
    op.create_table(
        "normalized_value",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_fitment_id", sa.String(length=36), nullable=True),
        sa.Column("parameter_definition_id", sa.String(length=36), nullable=False),
        sa.Column("numeric_value", sa.Numeric(precision=20, scale=8, asdecimal=False), nullable=True),
        sa.Column("text_value", sa.Text(), nullable=True),
        sa.Column("boolean_value", sa.Boolean(), nullable=True),
        sa.Column("enum_value", sa.String(length=120), nullable=True),
        sa.Column("json_value", sa.JSON(none_as_null=True), nullable=True),
        sa.Column("canonical_unit", sa.String(length=32), nullable=True),
        sa.Column("load_condition_id", sa.String(length=36), nullable=True),
        sa.Column("applicability_from", sa.Integer(), nullable=True),
        sa.Column("applicability_to", sa.Integer(), nullable=True),
        sa.Column("evidence_method", sa.String(length=16), nullable=False),
        sa.Column("resolution_state", sa.String(length=32), nullable=False),
        sa.Column("verification_state", sa.String(length=16), nullable=False),
        sa.Column("availability_state", sa.String(length=32), nullable=False),
        sa.Column("authority_grade", sa.String(length=16), nullable=True),
        sa.Column("applicability_grade", sa.String(length=64), nullable=True),
        sa.Column("precision", sa.String(length=80), nullable=True),
        sa.Column("uncertainty_value", sa.Numeric(precision=14, scale=6, asdecimal=False), nullable=True),
        sa.Column("uncertainty_unit", sa.String(length=48), nullable=True),
        sa.Column("normalization_rule_version", sa.String(length=80), nullable=True),
        sa.Column("semantic_metadata", sa.JSON(none_as_null=True), nullable=True),
        sa.Column("preferred", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewer", sa.String(length=160), nullable=True),
        sa.CheckConstraint(
            "(CASE WHEN numeric_value IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN text_value IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN boolean_value IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN enum_value IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN json_value IS NOT NULL THEN 1 ELSE 0 END) = "
            "CASE WHEN availability_state = 'AVAILABLE' THEN 1 ELSE 0 END",
            name="ck_normalized_value_typed_value_matches_availability",
        ),
        sa.CheckConstraint(
            "evidence_method != 'DERIVED' OR normalization_rule_version IS NOT NULL",
            name="ck_normalized_value_derived_value_has_rule_version",
        ),
        sa.CheckConstraint(
            "uncertainty_value IS NULL OR uncertainty_value >= 0",
            name="ck_normalized_value_nonnegative_uncertainty",
        ),
        sa.ForeignKeyConstraint(
            ["load_condition_id"],
            ["load_condition.id"],
            name="fk_normalized_value_load_condition",
        ),
        sa.ForeignKeyConstraint(
            ["parameter_definition_id"],
            ["parameter_definition.id"],
            name="fk_normalized_value_parameter",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_normalized_value_config",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_fitment_id"],
            ["vehicle_fitment.id"],
            name="fk_normalized_value_fitment",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_normalized_value"),
    )
    op.create_table(
        "parameter_assessment",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_fitment_id", sa.String(length=36), nullable=True),
        sa.Column("parameter_definition_id", sa.String(length=36), nullable=False),
        sa.Column("availability_state", sa.String(length=32), nullable=False),
        sa.Column("unknown_reason", sa.Text(), nullable=False),
        sa.Column("source_families_searched", sa.JSON(none_as_null=True), nullable=True),
        sa.Column("search_notes", sa.Text(), nullable=True),
        sa.Column("assessed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewer", sa.String(length=160), nullable=True),
        sa.Column("next_action", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "availability_state IN ('UNKNOWN', 'NOT_FOUND_AFTER_SEARCH', 'NOT_APPLICABLE')",
            name="ck_parameter_assessment_assessment_requires_nonavailable_state",
        ),
        sa.ForeignKeyConstraint(
            ["parameter_definition_id"],
            ["parameter_definition.id"],
            name="fk_parameter_assessment_parameter",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_parameter_assessment_config",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_fitment_id"],
            ["vehicle_fitment.id"],
            name="fk_parameter_assessment_vehicle_fitment_id_vehicle_fitment",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_parameter_assessment"),
    )
    op.create_table(
        "derivation_rule",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("rule_code", sa.String(length=160), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("output_parameter_definition_id", sa.String(length=36), nullable=False),
        sa.Column("formula_description", sa.Text(), nullable=False),
        sa.Column("validity_conditions", sa.Text(), nullable=False),
        sa.Column("uncertainty_method", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("reference_basis", sa.Text(), nullable=True),
        sa.Column("input_parameter_codes", sa.JSON(none_as_null=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["output_parameter_definition_id"],
            ["parameter_definition.id"],
            name="fk_derivation_rule_output_parameter",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_derivation_rule"),
        sa.UniqueConstraint("rule_code", "version", name="uq_derivation_rule_code_version"),
    )
    op.create_table(
        "derivation_run",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("derivation_rule_id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=False),
        sa.Column("output_normalized_value_id", sa.String(length=36), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("implementation_version", sa.String(length=80), nullable=False),
        sa.Column("result_notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["derivation_rule_id"],
            ["derivation_rule.id"],
            name="fk_derivation_run_derivation_rule_id_derivation_rule",
        ),
        sa.ForeignKeyConstraint(
            ["output_normalized_value_id"],
            ["normalized_value.id"],
            name="fk_derivation_run_output_normalized_value_id_normalized_value",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_derivation_run_config",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_derivation_run"),
        sa.UniqueConstraint("output_normalized_value_id", name="uq_derivation_run_output_value"),
    )
    op.create_table(
        "evidence_link",
        sa.Column("normalized_value_id", sa.String(length=36), nullable=False),
        sa.Column("source_observation_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_role", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(
            ["normalized_value_id"],
            ["normalized_value.id"],
            name="fk_evidence_link_normalized_value_id_normalized_value",
        ),
        sa.ForeignKeyConstraint(
            ["source_observation_id"],
            ["source_observation.id"],
            name="fk_evidence_link_source_observation_id_source_observation",
        ),
        sa.PrimaryKeyConstraint("normalized_value_id", "source_observation_id", name="pk_evidence_link"),
        sa.UniqueConstraint("normalized_value_id", "source_observation_id", name="uq_evidence_link_value_observation"),
    )
    op.create_table(
        "conflict_decision",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=False),
        sa.Column("parameter_definition_id", sa.String(length=36), nullable=False),
        sa.Column("selected_normalized_value_id", sa.String(length=36), nullable=True),
        sa.Column("decision_state", sa.String(length=32), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewer", sa.String(length=160), nullable=True),
        sa.Column("superseded_by_decision_id", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(
            ["parameter_definition_id"],
            ["parameter_definition.id"],
            name="fk_conflict_decision_parameter",
        ),
        sa.ForeignKeyConstraint(
            ["selected_normalized_value_id"],
            ["normalized_value.id"],
            name="fk_conflict_decision_value",
        ),
        sa.ForeignKeyConstraint(
            ["superseded_by_decision_id"],
            ["conflict_decision.id"],
            name="fk_conflict_decision_superseding",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_conflict_decision_config",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_conflict_decision"),
    )
    op.create_table(
        "geometry_asset",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_fitment_id", sa.String(length=36), nullable=True),
        sa.Column("geometry_role", sa.String(length=64), nullable=False),
        sa.Column("representation_type", sa.String(length=32), nullable=False),
        sa.Column("geometry_data", sa.JSON(none_as_null=True), nullable=True),
        sa.Column("file_reference", sa.String(length=512), nullable=True),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("coordinate_system_version", sa.String(length=80), nullable=False),
        sa.Column("source_coordinate_description", sa.Text(), nullable=True),
        sa.Column("normalization_transform", sa.JSON(none_as_null=True), nullable=True),
        sa.Column("load_condition_id", sa.String(length=36), nullable=True),
        sa.Column("body_mirror_inclusion", sa.String(length=80), nullable=True),
        sa.Column("geometry_method", sa.String(length=64), nullable=False),
        sa.Column("geometry_fidelity", sa.String(length=32), nullable=False),
        sa.Column("uncertainty_description", sa.Text(), nullable=True),
        sa.Column("uncertainty_value", sa.Numeric(precision=14, scale=6, asdecimal=False), nullable=True),
        sa.Column("uncertainty_unit", sa.String(length=32), nullable=True),
        sa.Column("source_document_id", sa.String(length=36), nullable=True),
        sa.Column("derivation_run_id", sa.String(length=36), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "length(coordinate_system_version) > 0",
            name="ck_geometry_asset_geometry_datum_required",
        ),
        sa.ForeignKeyConstraint(
            ["derivation_run_id"],
            ["derivation_run.id"],
            name="fk_geometry_asset_derivation_run_id_derivation_run",
        ),
        sa.ForeignKeyConstraint(
            ["load_condition_id"],
            ["load_condition.id"],
            name="fk_geometry_asset_load_condition_id_load_condition",
        ),
        sa.ForeignKeyConstraint(
            ["source_document_id"],
            ["source_document.id"],
            name="fk_geometry_asset_source_document_id_source_document",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_geometry_asset_config",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_fitment_id"],
            ["vehicle_fitment.id"],
            name="fk_geometry_asset_vehicle_fitment_id_vehicle_fitment",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_geometry_asset"),
    )
    op.create_table(
        "readiness_result",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_fitment_id", sa.String(length=36), nullable=True),
        sa.Column("readiness_type", sa.String(length=48), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("rule_version", sa.String(length=80), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("blocking_reasons", sa.JSON(), nullable=False),
        sa.Column("supporting_value_ids", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_readiness_result_config",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_fitment_id"],
            ["vehicle_fitment.id"],
            name="fk_readiness_result_vehicle_fitment_id_vehicle_fitment",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_readiness_result"),
        sa.UniqueConstraint(
            "vehicle_configuration_id",
            "vehicle_fitment_id",
            "readiness_type",
            name="uq_readiness_scope_type",
        ),
    )
    op.create_table(
        "qa_finding",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=True),
        sa.Column("source_document_id", sa.String(length=36), nullable=True),
        sa.Column("normalized_value_id", sa.String(length=36), nullable=True),
        sa.Column("finding_code", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["normalized_value_id"],
            ["normalized_value.id"],
            name="fk_qa_finding_normalized_value_id_normalized_value",
        ),
        sa.ForeignKeyConstraint(
            ["source_document_id"],
            ["source_document.id"],
            name="fk_qa_finding_source_document_id_source_document",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_qa_finding_vehicle_configuration_id_vehicle_configuration",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_qa_finding"),
    )
    op.create_table(
        "avt_mapping_result",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_configuration_id", sa.String(length=36), nullable=False),
        sa.Column("vehicle_fitment_id", sa.String(length=36), nullable=True),
        sa.Column("adapter_version", sa.String(length=80), nullable=False),
        sa.Column("target_avt_version", sa.String(length=80), nullable=True),
        sa.Column("mapping_status", sa.String(length=24), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mapping_payload", sa.JSON(), nullable=False),
        sa.Column("blocker_list", sa.JSON(), nullable=False),
        sa.Column("source_value_ids", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["vehicle_configuration_id"],
            ["vehicle_configuration.id"],
            name="fk_avt_mapping_result_config",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_fitment_id"],
            ["vehicle_fitment.id"],
            name="fk_avt_mapping_result_vehicle_fitment_id_vehicle_fitment",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_avt_mapping_result"),
    )
    op.create_table(
        "derivation_input",
        sa.Column("derivation_run_id", sa.String(length=36), nullable=False),
        sa.Column("input_normalized_value_id", sa.String(length=36), nullable=False),
        sa.Column("input_role", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(
            ["derivation_run_id"],
            ["derivation_run.id"],
            name="fk_derivation_input_derivation_run_id_derivation_run",
        ),
        sa.ForeignKeyConstraint(
            ["input_normalized_value_id"],
            ["normalized_value.id"],
            name="fk_derivation_input_input_normalized_value_id_normalized_value",
        ),
        sa.PrimaryKeyConstraint("derivation_run_id", "input_normalized_value_id", name="pk_derivation_input"),
        sa.UniqueConstraint("derivation_run_id", "input_normalized_value_id", name="uq_derivation_input_value"),
    )

    op.create_index("ix_parameter_definition_family", "parameter_definition", ["family"])
    op.create_index("ix_source_document_publisher", "source_document", ["publisher"])
    op.create_index("ix_source_document_market_year", "source_document", ["market_code", "publication_year"])
    op.create_index("ix_vehicle_model_display_name", "vehicle_model", ["display_model_name"])
    op.create_index(
        "ix_vehicle_configuration_identity",
        "vehicle_configuration",
        ["market_code", "generation_name", "variant_trim"],
    )
    op.create_index("ix_vehicle_configuration_stable_code", "vehicle_configuration", ["stable_vehicle_code"])
    op.create_index(
        "ix_source_observation_vehicle_source",
        "source_observation",
        ["vehicle_configuration_id", "source_document_id"],
    )
    op.create_index("ix_source_observation_parameter_label", "source_observation", ["raw_label"])
    op.create_index("ix_avt_mapping_status", "avt_mapping_result", ["mapping_status"])
    op.create_index(
        "ix_normalized_value_config_parameter",
        "normalized_value",
        ["vehicle_configuration_id", "parameter_definition_id"],
    )
    op.create_index(
        "ix_normalized_value_states",
        "normalized_value",
        ["availability_state", "resolution_state", "verification_state"],
    )
    op.create_index("ix_parameter_assessment_state", "parameter_assessment", ["availability_state"])
    op.create_index("ix_readiness_status", "readiness_result", ["readiness_type", "status"])
    op.create_index("ix_qa_finding_status_severity", "qa_finding", ["status", "severity"])
    op.create_index("ix_geometry_asset_role", "geometry_asset", ["geometry_role"])
    op.create_index("ix_derivation_rule_output", "derivation_rule", ["output_parameter_definition_id"])


def downgrade() -> None:
    """Drop the Phase 0 schema in explicit reverse dependency order."""

    op.drop_index("ix_derivation_rule_output", table_name="derivation_rule")
    op.drop_index("ix_geometry_asset_role", table_name="geometry_asset")
    op.drop_index("ix_qa_finding_status_severity", table_name="qa_finding")
    op.drop_index("ix_readiness_status", table_name="readiness_result")
    op.drop_index("ix_parameter_assessment_state", table_name="parameter_assessment")
    op.drop_index("ix_normalized_value_states", table_name="normalized_value")
    op.drop_index("ix_normalized_value_config_parameter", table_name="normalized_value")
    op.drop_index("ix_avt_mapping_status", table_name="avt_mapping_result")
    op.drop_index("ix_source_observation_parameter_label", table_name="source_observation")
    op.drop_index("ix_source_observation_vehicle_source", table_name="source_observation")
    op.drop_index("ix_vehicle_configuration_stable_code", table_name="vehicle_configuration")
    op.drop_index("ix_vehicle_configuration_identity", table_name="vehicle_configuration")
    op.drop_index("ix_vehicle_model_display_name", table_name="vehicle_model")
    op.drop_index("ix_source_document_market_year", table_name="source_document")
    op.drop_index("ix_source_document_publisher", table_name="source_document")
    op.drop_index("ix_parameter_definition_family", table_name="parameter_definition")

    op.drop_table("derivation_input")
    op.drop_table("avt_mapping_result")
    op.drop_table("qa_finding")
    op.drop_table("readiness_result")
    op.drop_table("geometry_asset")
    op.drop_table("conflict_decision")
    op.drop_table("evidence_link")
    op.drop_table("derivation_run")
    op.drop_table("derivation_rule")
    op.drop_table("parameter_assessment")
    op.drop_table("normalized_value")
    op.drop_table("steering_relation")
    op.drop_table("source_observation")
    op.drop_table("load_condition")
    op.drop_table("axle")
    op.drop_table("vehicle_fitment")
    op.drop_table("vehicle_configuration")
    op.drop_table("vehicle_model")
    op.drop_table("source_document")
    op.drop_table("parameter_definition")
    op.drop_table("manufacturer")
