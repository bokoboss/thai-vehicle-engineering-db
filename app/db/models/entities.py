from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    MetaData,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def new_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class Manufacturer(Base):
    __tablename__ = "manufacturer"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    canonical_name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    country_of_origin: Mapped[str | None] = mapped_column(String(80))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    models: Mapped[list[VehicleModel]] = relationship(back_populates="manufacturer")


class VehicleModel(Base):
    __tablename__ = "vehicle_model"
    __table_args__ = (
        UniqueConstraint("manufacturer_id", "canonical_model_name", name="uq_vehicle_model_manufacturer_name"),
        Index("ix_vehicle_model_display_name", "display_model_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    manufacturer_id: Mapped[str] = mapped_column(ForeignKey("manufacturer.id"), nullable=False)
    canonical_model_name: Mapped[str] = mapped_column(String(160), nullable=False)
    display_model_name: Mapped[str] = mapped_column(String(160), nullable=False)

    manufacturer: Mapped[Manufacturer] = relationship(back_populates="models")
    configurations: Mapped[list[VehicleConfiguration]] = relationship(back_populates="vehicle_model")


class VehicleConfiguration(Base):
    __tablename__ = "vehicle_configuration"
    __table_args__ = (
        CheckConstraint(
            "model_year_to IS NULL OR model_year_to >= model_year_from",
            name="valid_model_year_range",
        ),
        Index("ix_vehicle_configuration_identity", "market_code", "generation_name", "variant_trim"),
        Index("ix_vehicle_configuration_stable_code", "stable_vehicle_code"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    stable_vehicle_code: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    vehicle_model_id: Mapped[str] = mapped_column(ForeignKey("vehicle_model.id"), nullable=False)
    market_code: Mapped[str] = mapped_column(String(8), nullable=False)
    generation_name: Mapped[str] = mapped_column(String(160), nullable=False)
    chassis_platform_code: Mapped[str | None] = mapped_column(String(120))
    body_style: Mapped[str] = mapped_column(String(80), nullable=False)
    model_year_from: Mapped[int] = mapped_column(Integer, nullable=False)
    model_year_to: Mapped[int | None] = mapped_column(Integer)
    sale_period_from: Mapped[date | None] = mapped_column(Date)
    sale_period_to: Mapped[date | None] = mapped_column(Date)
    variant_trim: Mapped[str] = mapped_column(String(180), nullable=False)
    powertrain: Mapped[str | None] = mapped_column(String(160))
    drivetrain: Mapped[str | None] = mapped_column(String(80))
    body_configuration: Mapped[str | None] = mapped_column(String(160))
    identity_notes: Mapped[str | None] = mapped_column(Text)
    identity_verification_state: Mapped[str] = mapped_column(String(48), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    vehicle_model: Mapped[VehicleModel] = relationship(back_populates="configurations")
    fitments: Mapped[list[VehicleFitment]] = relationship(back_populates="vehicle_configuration", cascade="all, delete-orphan")
    axles: Mapped[list[Axle]] = relationship(back_populates="vehicle_configuration", cascade="all, delete-orphan")
    steering_relations: Mapped[list[SteeringRelation]] = relationship(back_populates="vehicle_configuration", cascade="all, delete-orphan")
    load_conditions: Mapped[list[LoadCondition]] = relationship(back_populates="vehicle_configuration", cascade="all, delete-orphan")
    source_observations: Mapped[list[SourceObservation]] = relationship(back_populates="vehicle_configuration")
    normalized_values: Mapped[list[NormalizedValue]] = relationship(back_populates="vehicle_configuration", cascade="all, delete-orphan")
    parameter_assessments: Mapped[list[ParameterAssessment]] = relationship(back_populates="vehicle_configuration", cascade="all, delete-orphan")
    derivation_runs: Mapped[list[DerivationRun]] = relationship(back_populates="vehicle_configuration", cascade="all, delete-orphan")
    conflict_decisions: Mapped[list[ConflictDecision]] = relationship(back_populates="vehicle_configuration", cascade="all, delete-orphan")
    geometry_assets: Mapped[list[GeometryAsset]] = relationship(back_populates="vehicle_configuration", cascade="all, delete-orphan")
    readiness_results: Mapped[list[ReadinessResult]] = relationship(back_populates="vehicle_configuration", cascade="all, delete-orphan")
    qa_findings: Mapped[list[QAFinding]] = relationship(back_populates="vehicle_configuration")
    avt_mapping_results: Mapped[list[AVTMappingResult]] = relationship(back_populates="vehicle_configuration", cascade="all, delete-orphan")


class VehicleFitment(Base):
    __tablename__ = "vehicle_fitment"
    __table_args__ = (UniqueConstraint("vehicle_configuration_id", "fitment_code", name="uq_fitment_configuration_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    vehicle_configuration_id: Mapped[str] = mapped_column(ForeignKey("vehicle_configuration.id"), nullable=False)
    fitment_code: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    wheel_package: Mapped[str | None] = mapped_column(String(160))
    equipment_package: Mapped[str | None] = mapped_column(String(160))
    model_year_from: Mapped[int | None] = mapped_column(Integer)
    model_year_to: Mapped[int | None] = mapped_column(Integer)
    default_for_configuration: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text)

    vehicle_configuration: Mapped[VehicleConfiguration] = relationship(back_populates="fitments")
    normalized_values: Mapped[list[NormalizedValue]] = relationship(back_populates="vehicle_fitment")
    parameter_assessments: Mapped[list[ParameterAssessment]] = relationship(back_populates="vehicle_fitment")
    geometry_assets: Mapped[list[GeometryAsset]] = relationship(back_populates="vehicle_fitment")
    readiness_results: Mapped[list[ReadinessResult]] = relationship(back_populates="vehicle_fitment")
    avt_mapping_results: Mapped[list[AVTMappingResult]] = relationship(back_populates="vehicle_fitment")


class Axle(Base):
    __tablename__ = "axle"
    __table_args__ = (
        UniqueConstraint("vehicle_configuration_id", "axle_index", name="uq_axle_configuration_index"),
        CheckConstraint("axle_index >= 0", name="nonnegative_axle_index"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    vehicle_configuration_id: Mapped[str] = mapped_column(ForeignKey("vehicle_configuration.id"), nullable=False)
    axle_role: Mapped[str] = mapped_column(String(32), nullable=False)
    axle_index: Mapped[int] = mapped_column(Integer, nullable=False)
    longitudinal_position_mm: Mapped[float | None] = mapped_column(Numeric(18, 6, asdecimal=False))
    axle_group: Mapped[str | None] = mapped_column(String(80))
    driven: Mapped[bool | None] = mapped_column(Boolean)
    steered: Mapped[bool | None] = mapped_column(Boolean)
    retractable: Mapped[bool | None] = mapped_column(Boolean)
    self_steering: Mapped[bool | None] = mapped_column(Boolean)
    notes: Mapped[str | None] = mapped_column(Text)

    vehicle_configuration: Mapped[VehicleConfiguration] = relationship(back_populates="axles")
    steering_relations: Mapped[list[SteeringRelation]] = relationship(back_populates="axle", cascade="all, delete-orphan")


class SteeringRelation(Base):
    __tablename__ = "steering_relation"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    vehicle_configuration_id: Mapped[str] = mapped_column(ForeignKey("vehicle_configuration.id"), nullable=False)
    axle_id: Mapped[str] = mapped_column(ForeignKey("axle.id"), nullable=False)
    steering_role: Mapped[str] = mapped_column(String(32), nullable=False)
    linkage_type: Mapped[str] = mapped_column(String(32), nullable=False)
    max_steering_angle_deg: Mapped[float | None] = mapped_column(Numeric(12, 6, asdecimal=False))
    phase_behavior: Mapped[str] = mapped_column(String(40), nullable=False)
    angle_ratio: Mapped[float | None] = mapped_column(Numeric(12, 6, asdecimal=False))
    relation_function: Mapped[str | None] = mapped_column(Text)
    speed_min_kph: Mapped[float | None] = mapped_column(Numeric(12, 6, asdecimal=False))
    speed_max_kph: Mapped[float | None] = mapped_column(Numeric(12, 6, asdecimal=False))
    mode_applicability: Mapped[str | None] = mapped_column(String(160))
    source_observation_id: Mapped[str | None] = mapped_column(ForeignKey("source_observation.id"))
    notes: Mapped[str | None] = mapped_column(Text)

    vehicle_configuration: Mapped[VehicleConfiguration] = relationship(back_populates="steering_relations")
    axle: Mapped[Axle] = relationship(back_populates="steering_relations")
    source_observation: Mapped[SourceObservation | None] = relationship()


class LoadCondition(Base):
    __tablename__ = "load_condition"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    vehicle_configuration_id: Mapped[str | None] = mapped_column(ForeignKey("vehicle_configuration.id"))
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    mass_basis: Mapped[str] = mapped_column(String(32), nullable=False)
    total_mass_kg: Mapped[float | None] = mapped_column(Numeric(14, 6, asdecimal=False))
    occupant_count: Mapped[int | None] = mapped_column(Integer)
    payload_kg: Mapped[float | None] = mapped_column(Numeric(14, 6, asdecimal=False))
    front_axle_load_kg: Mapped[float | None] = mapped_column(Numeric(14, 6, asdecimal=False))
    rear_axle_load_kg: Mapped[float | None] = mapped_column(Numeric(14, 6, asdecimal=False))
    front_tyre_pressure: Mapped[float | None] = mapped_column(Numeric(12, 6, asdecimal=False))
    rear_tyre_pressure: Mapped[float | None] = mapped_column(Numeric(12, 6, asdecimal=False))
    tyre_pressure_unit: Mapped[str | None] = mapped_column(String(24))
    suspension_mode: Mapped[str | None] = mapped_column(String(100))
    ride_height_mode: Mapped[str | None] = mapped_column(String(100))
    raw_oem_wording: Mapped[str | None] = mapped_column(Text)
    source_document_id: Mapped[str | None] = mapped_column(ForeignKey("source_document.id"))
    notes: Mapped[str | None] = mapped_column(Text)

    vehicle_configuration: Mapped[VehicleConfiguration | None] = relationship(back_populates="load_conditions")
    source_document: Mapped[SourceDocument | None] = relationship()
    normalized_values: Mapped[list[NormalizedValue]] = relationship(back_populates="load_condition")
    geometry_assets: Mapped[list[GeometryAsset]] = relationship(back_populates="load_condition")


class SourceDocument(Base):
    __tablename__ = "source_document"
    __table_args__ = (
        Index("ix_source_document_publisher", "publisher"),
        Index("ix_source_document_market_year", "market_code", "publication_year"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    source_code: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    publisher: Mapped[str] = mapped_column(String(200), nullable=False)
    authority_class: Mapped[str] = mapped_column(String(64), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    market_code: Mapped[str | None] = mapped_column(String(8))
    publication_year: Mapped[int | None] = mapped_column(Integer)
    model_year_from: Mapped[int | None] = mapped_column(Integer)
    model_year_to: Mapped[int | None] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    local_snapshot_reference: Mapped[str | None] = mapped_column(String(512))
    content_hash: Mapped[str | None] = mapped_column(String(128))
    page_section_default: Mapped[str | None] = mapped_column(String(240))
    access_licensing_notes: Mapped[str | None] = mapped_column(Text)
    applicability_notes: Mapped[str | None] = mapped_column(Text)
    archival_status: Mapped[str | None] = mapped_column(String(80))
    notes: Mapped[str | None] = mapped_column(Text)

    observations: Mapped[list[SourceObservation]] = relationship(back_populates="source_document", cascade="all, delete-orphan")


class SourceObservation(Base):
    __tablename__ = "source_observation"
    __table_args__ = (
        Index("ix_source_observation_parameter_label", "raw_label"),
        Index("ix_source_observation_vehicle_source", "vehicle_configuration_id", "source_document_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    vehicle_configuration_id: Mapped[str | None] = mapped_column(ForeignKey("vehicle_configuration.id"))
    vehicle_identity_claim: Mapped[str] = mapped_column(Text, nullable=False)
    source_document_id: Mapped[str] = mapped_column(ForeignKey("source_document.id"), nullable=False)
    raw_label: Mapped[str] = mapped_column(String(240), nullable=False)
    raw_value: Mapped[str] = mapped_column(Text, nullable=False)
    raw_unit: Mapped[str | None] = mapped_column(String(48))
    raw_qualifier: Mapped[str | None] = mapped_column(Text)
    raw_excerpt: Mapped[str | None] = mapped_column(Text)
    page_section_locator: Mapped[str | None] = mapped_column(String(240))
    reported_precision: Mapped[str | None] = mapped_column(String(80))
    uncertainty_value: Mapped[float | None] = mapped_column(Numeric(14, 6, asdecimal=False))
    uncertainty_unit: Mapped[str | None] = mapped_column(String(48))
    extraction_method: Mapped[str] = mapped_column(String(48), nullable=False)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    extracted_by: Mapped[str | None] = mapped_column(String(160))
    reviewer: Mapped[str | None] = mapped_column(String(160))
    ambiguity_note: Mapped[str | None] = mapped_column(Text)

    vehicle_configuration: Mapped[VehicleConfiguration | None] = relationship(back_populates="source_observations")
    source_document: Mapped[SourceDocument] = relationship(back_populates="observations")
    evidence_links: Mapped[list[EvidenceLink]] = relationship(back_populates="source_observation", cascade="all, delete-orphan")


class ParameterDefinition(Base):
    __tablename__ = "parameter_definition"
    __table_args__ = (
        Index("ix_parameter_definition_family", "family"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    parameter_code: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(240), nullable=False)
    family: Mapped[str] = mapped_column(String(80), nullable=False)
    data_type: Mapped[str] = mapped_column(String(16), nullable=False)
    canonical_unit: Mapped[str | None] = mapped_column(String(32))
    semantic_definition: Mapped[str | None] = mapped_column(Text)
    applicability_notes: Mapped[str | None] = mapped_column(Text)
    requires_attributes: Mapped[list[str] | None] = mapped_column(JSON(none_as_null=True))
    deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    replacement_parameter_code: Mapped[str | None] = mapped_column(String(160))
    created_version: Mapped[str] = mapped_column(String(32), nullable=False)

    normalized_values: Mapped[list[NormalizedValue]] = relationship(back_populates="parameter_definition")
    assessments: Mapped[list[ParameterAssessment]] = relationship(back_populates="parameter_definition")
    derivation_rules: Mapped[list[DerivationRule]] = relationship(back_populates="output_parameter_definition")
    conflict_decisions: Mapped[list[ConflictDecision]] = relationship(back_populates="parameter_definition")


class NormalizedValue(Base):
    __tablename__ = "normalized_value"
    __table_args__ = (
        CheckConstraint(
            "(CASE WHEN numeric_value IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN text_value IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN boolean_value IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN enum_value IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN json_value IS NOT NULL THEN 1 ELSE 0 END) = "
            "CASE WHEN availability_state = 'AVAILABLE' THEN 1 ELSE 0 END",
            name="typed_value_matches_availability",
        ),
        CheckConstraint(
            "evidence_method != 'DERIVED' OR normalization_rule_version IS NOT NULL",
            name="derived_value_has_rule_version",
        ),
        CheckConstraint("uncertainty_value IS NULL OR uncertainty_value >= 0", name="nonnegative_uncertainty"),
        Index("ix_normalized_value_config_parameter", "vehicle_configuration_id", "parameter_definition_id"),
        Index("ix_normalized_value_states", "availability_state", "resolution_state", "verification_state"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    vehicle_configuration_id: Mapped[str] = mapped_column(ForeignKey("vehicle_configuration.id"), nullable=False)
    vehicle_fitment_id: Mapped[str | None] = mapped_column(ForeignKey("vehicle_fitment.id"))
    parameter_definition_id: Mapped[str] = mapped_column(ForeignKey("parameter_definition.id"), nullable=False)
    numeric_value: Mapped[float | None] = mapped_column(Numeric(20, 8, asdecimal=False))
    text_value: Mapped[str | None] = mapped_column(Text)
    boolean_value: Mapped[bool | None] = mapped_column(Boolean)
    enum_value: Mapped[str | None] = mapped_column(String(120))
    json_value: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSON(none_as_null=True))
    canonical_unit: Mapped[str | None] = mapped_column(String(32))
    load_condition_id: Mapped[str | None] = mapped_column(ForeignKey("load_condition.id"))
    applicability_from: Mapped[int | None] = mapped_column(Integer)
    applicability_to: Mapped[int | None] = mapped_column(Integer)
    evidence_method: Mapped[str] = mapped_column(String(16), nullable=False)
    resolution_state: Mapped[str] = mapped_column(String(32), nullable=False)
    verification_state: Mapped[str] = mapped_column(String(16), nullable=False)
    availability_state: Mapped[str] = mapped_column(String(32), nullable=False)
    authority_grade: Mapped[str | None] = mapped_column(String(16))
    applicability_grade: Mapped[str | None] = mapped_column(String(64))
    precision: Mapped[str | None] = mapped_column(String(80))
    uncertainty_value: Mapped[float | None] = mapped_column(Numeric(14, 6, asdecimal=False))
    uncertainty_unit: Mapped[str | None] = mapped_column(String(48))
    normalization_rule_version: Mapped[str | None] = mapped_column(String(80))
    semantic_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON(none_as_null=True))
    preferred: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewer: Mapped[str | None] = mapped_column(String(160))

    vehicle_configuration: Mapped[VehicleConfiguration] = relationship(back_populates="normalized_values")
    vehicle_fitment: Mapped[VehicleFitment | None] = relationship(back_populates="normalized_values")
    parameter_definition: Mapped[ParameterDefinition] = relationship(back_populates="normalized_values")
    load_condition: Mapped[LoadCondition | None] = relationship(back_populates="normalized_values")
    evidence_links: Mapped[list[EvidenceLink]] = relationship(back_populates="normalized_value", cascade="all, delete-orphan")
    derivation_run: Mapped[DerivationRun | None] = relationship(
        "DerivationRun",
        back_populates="output_value",
        foreign_keys="DerivationRun.output_normalized_value_id",
        uselist=False,
    )
    selected_by_conflict_decisions: Mapped[list[ConflictDecision]] = relationship(
        "ConflictDecision",
        foreign_keys="ConflictDecision.selected_normalized_value_id",
        viewonly=True,
    )


class EvidenceLink(Base):
    __tablename__ = "evidence_link"
    __table_args__ = (
        UniqueConstraint("normalized_value_id", "source_observation_id", name="uq_evidence_link_value_observation"),
    )

    normalized_value_id: Mapped[str] = mapped_column(ForeignKey("normalized_value.id"), primary_key=True)
    source_observation_id: Mapped[str] = mapped_column(ForeignKey("source_observation.id"), primary_key=True)
    evidence_role: Mapped[str] = mapped_column(String(16), nullable=False)

    normalized_value: Mapped[NormalizedValue] = relationship(back_populates="evidence_links")
    source_observation: Mapped[SourceObservation] = relationship(back_populates="evidence_links")


class ParameterAssessment(Base):
    __tablename__ = "parameter_assessment"
    __table_args__ = (
        CheckConstraint(
            "availability_state IN ('UNKNOWN', 'NOT_FOUND_AFTER_SEARCH', 'NOT_APPLICABLE')",
            name="assessment_requires_nonavailable_state",
        ),
        Index("ix_parameter_assessment_state", "availability_state"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    vehicle_configuration_id: Mapped[str] = mapped_column(ForeignKey("vehicle_configuration.id"), nullable=False)
    vehicle_fitment_id: Mapped[str | None] = mapped_column(ForeignKey("vehicle_fitment.id"))
    parameter_definition_id: Mapped[str] = mapped_column(ForeignKey("parameter_definition.id"), nullable=False)
    availability_state: Mapped[str] = mapped_column(String(32), nullable=False)
    unknown_reason: Mapped[str] = mapped_column(Text, nullable=False)
    source_families_searched: Mapped[list[str] | None] = mapped_column(JSON(none_as_null=True))
    search_notes: Mapped[str | None] = mapped_column(Text)
    assessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviewer: Mapped[str | None] = mapped_column(String(160))
    next_action: Mapped[str | None] = mapped_column(Text)

    vehicle_configuration: Mapped[VehicleConfiguration] = relationship(back_populates="parameter_assessments")
    vehicle_fitment: Mapped[VehicleFitment | None] = relationship(back_populates="parameter_assessments")
    parameter_definition: Mapped[ParameterDefinition] = relationship(back_populates="assessments")


class DerivationRule(Base):
    __tablename__ = "derivation_rule"
    __table_args__ = (
        UniqueConstraint("rule_code", "version", name="uq_derivation_rule_code_version"),
        Index("ix_derivation_rule_output", "output_parameter_definition_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    rule_code: Mapped[str] = mapped_column(String(160), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    output_parameter_definition_id: Mapped[str] = mapped_column(ForeignKey("parameter_definition.id"), nullable=False)
    formula_description: Mapped[str] = mapped_column(Text, nullable=False)
    validity_conditions: Mapped[str] = mapped_column(Text, nullable=False)
    uncertainty_method: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    reference_basis: Mapped[str | None] = mapped_column(Text)
    input_parameter_codes: Mapped[list[str] | None] = mapped_column(JSON(none_as_null=True))

    output_parameter_definition: Mapped[ParameterDefinition] = relationship(back_populates="derivation_rules")
    runs: Mapped[list[DerivationRun]] = relationship(back_populates="derivation_rule")


class DerivationRun(Base):
    __tablename__ = "derivation_run"
    __table_args__ = (UniqueConstraint("output_normalized_value_id", name="uq_derivation_run_output_value"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    derivation_rule_id: Mapped[str] = mapped_column(ForeignKey("derivation_rule.id"), nullable=False)
    vehicle_configuration_id: Mapped[str] = mapped_column(ForeignKey("vehicle_configuration.id"), nullable=False)
    output_normalized_value_id: Mapped[str | None] = mapped_column(ForeignKey("normalized_value.id"))
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    implementation_version: Mapped[str] = mapped_column(String(80), nullable=False)
    result_notes: Mapped[str | None] = mapped_column(Text)

    derivation_rule: Mapped[DerivationRule] = relationship(back_populates="runs")
    vehicle_configuration: Mapped[VehicleConfiguration] = relationship(back_populates="derivation_runs")
    output_value: Mapped[NormalizedValue | None] = relationship(
        "NormalizedValue",
        back_populates="derivation_run",
        foreign_keys=[output_normalized_value_id],
    )
    inputs: Mapped[list[DerivationInput]] = relationship(back_populates="derivation_run", cascade="all, delete-orphan")
    geometry_assets: Mapped[list[GeometryAsset]] = relationship(back_populates="derivation_run")


class DerivationInput(Base):
    __tablename__ = "derivation_input"
    __table_args__ = (UniqueConstraint("derivation_run_id", "input_normalized_value_id", name="uq_derivation_input_value"),)

    derivation_run_id: Mapped[str] = mapped_column(ForeignKey("derivation_run.id"), primary_key=True)
    input_normalized_value_id: Mapped[str] = mapped_column(ForeignKey("normalized_value.id"), primary_key=True)
    input_role: Mapped[str] = mapped_column(String(80), nullable=False)

    derivation_run: Mapped[DerivationRun] = relationship(back_populates="inputs")
    input_value: Mapped[NormalizedValue] = relationship()


class ConflictDecision(Base):
    __tablename__ = "conflict_decision"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    vehicle_configuration_id: Mapped[str] = mapped_column(ForeignKey("vehicle_configuration.id"), nullable=False)
    parameter_definition_id: Mapped[str] = mapped_column(ForeignKey("parameter_definition.id"), nullable=False)
    selected_normalized_value_id: Mapped[str | None] = mapped_column(ForeignKey("normalized_value.id"))
    decision_state: Mapped[str] = mapped_column(String(32), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviewer: Mapped[str | None] = mapped_column(String(160))
    superseded_by_decision_id: Mapped[str | None] = mapped_column(ForeignKey("conflict_decision.id"))

    vehicle_configuration: Mapped[VehicleConfiguration] = relationship(back_populates="conflict_decisions")
    parameter_definition: Mapped[ParameterDefinition] = relationship(back_populates="conflict_decisions")
    selected_value: Mapped[NormalizedValue | None] = relationship(foreign_keys=[selected_normalized_value_id])
    superseded_by: Mapped[ConflictDecision | None] = relationship(remote_side=[id])


class GeometryAsset(Base):
    __tablename__ = "geometry_asset"
    __table_args__ = (
        CheckConstraint("length(coordinate_system_version) > 0", name="geometry_datum_required"),
        Index("ix_geometry_asset_role", "geometry_role"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    vehicle_configuration_id: Mapped[str] = mapped_column(ForeignKey("vehicle_configuration.id"), nullable=False)
    vehicle_fitment_id: Mapped[str | None] = mapped_column(ForeignKey("vehicle_fitment.id"))
    geometry_role: Mapped[str] = mapped_column(String(64), nullable=False)
    representation_type: Mapped[str] = mapped_column(String(32), nullable=False)
    geometry_data: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSON(none_as_null=True))
    file_reference: Mapped[str | None] = mapped_column(String(512))
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    coordinate_system_version: Mapped[str] = mapped_column(String(80), nullable=False)
    source_coordinate_description: Mapped[str | None] = mapped_column(Text)
    normalization_transform: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSON(none_as_null=True))
    load_condition_id: Mapped[str | None] = mapped_column(ForeignKey("load_condition.id"))
    body_mirror_inclusion: Mapped[str | None] = mapped_column(String(80))
    geometry_method: Mapped[str] = mapped_column(String(64), nullable=False)
    geometry_fidelity: Mapped[str] = mapped_column(String(32), nullable=False)
    uncertainty_description: Mapped[str | None] = mapped_column(Text)
    uncertainty_value: Mapped[float | None] = mapped_column(Numeric(14, 6, asdecimal=False))
    uncertainty_unit: Mapped[str | None] = mapped_column(String(32))
    source_document_id: Mapped[str | None] = mapped_column(ForeignKey("source_document.id"))
    derivation_run_id: Mapped[str | None] = mapped_column(ForeignKey("derivation_run.id"))
    notes: Mapped[str | None] = mapped_column(Text)

    vehicle_configuration: Mapped[VehicleConfiguration] = relationship(back_populates="geometry_assets")
    vehicle_fitment: Mapped[VehicleFitment | None] = relationship(back_populates="geometry_assets")
    load_condition: Mapped[LoadCondition | None] = relationship(back_populates="geometry_assets")
    source_document: Mapped[SourceDocument | None] = relationship()
    derivation_run: Mapped[DerivationRun | None] = relationship(back_populates="geometry_assets")


class ReadinessResult(Base):
    __tablename__ = "readiness_result"
    __table_args__ = (
        UniqueConstraint("vehicle_configuration_id", "vehicle_fitment_id", "readiness_type", name="uq_readiness_scope_type"),
        Index("ix_readiness_status", "readiness_type", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    vehicle_configuration_id: Mapped[str] = mapped_column(ForeignKey("vehicle_configuration.id"), nullable=False)
    vehicle_fitment_id: Mapped[str | None] = mapped_column(ForeignKey("vehicle_fitment.id"))
    readiness_type: Mapped[str] = mapped_column(String(48), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(80), nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    blocking_reasons: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    supporting_value_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    vehicle_configuration: Mapped[VehicleConfiguration] = relationship(back_populates="readiness_results")
    vehicle_fitment: Mapped[VehicleFitment | None] = relationship(back_populates="readiness_results")


class QAFinding(Base):
    __tablename__ = "qa_finding"
    __table_args__ = (Index("ix_qa_finding_status_severity", "status", "severity"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    vehicle_configuration_id: Mapped[str | None] = mapped_column(ForeignKey("vehicle_configuration.id"))
    source_document_id: Mapped[str | None] = mapped_column(ForeignKey("source_document.id"))
    normalized_value_id: Mapped[str | None] = mapped_column(ForeignKey("normalized_value.id"))
    finding_code: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution_note: Mapped[str | None] = mapped_column(Text)

    vehicle_configuration: Mapped[VehicleConfiguration | None] = relationship(back_populates="qa_findings")
    source_document: Mapped[SourceDocument | None] = relationship()
    normalized_value: Mapped[NormalizedValue | None] = relationship()


class AVTMappingResult(Base):
    __tablename__ = "avt_mapping_result"
    __table_args__ = (Index("ix_avt_mapping_status", "mapping_status"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    vehicle_configuration_id: Mapped[str] = mapped_column(ForeignKey("vehicle_configuration.id"), nullable=False)
    vehicle_fitment_id: Mapped[str | None] = mapped_column(ForeignKey("vehicle_fitment.id"))
    adapter_version: Mapped[str] = mapped_column(String(80), nullable=False)
    target_avt_version: Mapped[str | None] = mapped_column(String(80))
    mapping_status: Mapped[str] = mapped_column(String(24), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mapping_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    blocker_list: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    source_value_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    vehicle_configuration: Mapped[VehicleConfiguration] = relationship(back_populates="avt_mapping_results")
    vehicle_fitment: Mapped[VehicleFitment | None] = relationship(back_populates="avt_mapping_results")


QA_FINDING_STATUSES = ("OPEN", "ACCEPTED", "RESOLVED")
