from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.enums import (
    ApplicabilityGrade,
    AvailabilityState,
    AxleRole,
    ClearanceType,
    DataType,
    DecisionState,
    EvidenceMethod,
    EvidenceRole,
    ExtractionMethod,
    GeometryFidelity,
    GeometryMethod,
    GeometryRole,
    IdentityTimeBasis,
    IdentityVerificationState,
    LinkageType,
    MassBasis,
    PhaseBehavior,
    ReadinessStatus,
    ReadinessType,
    RepresentationType,
    ResolutionState,
    SteeringRole,
    TrackDefinition,
    TurningAxleScope,
    TurningRadiusOrDiameter,
    TurningReference,
    VerificationState,
    WallEnvelopeScope,
    WidthEnvelopeDefinition,
)
from app.domain.validation import validate_identity_time_basis


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class VehicleConfigurationCreate(DomainModel):
    stable_vehicle_code: str = Field(min_length=1, max_length=160)
    market_code: str = Field(min_length=1, max_length=8)
    generation_name: str = Field(min_length=1, max_length=160)
    body_style: str = Field(min_length=1, max_length=80)
    model_year_from: int | None = Field(default=None, ge=1886, le=2200)
    model_year_to: int | None = Field(default=None, ge=1886, le=2200)
    identity_time_basis: IdentityTimeBasis = IdentityTimeBasis.MODEL_YEAR
    identity_time_label_raw: str | None = Field(default=None, max_length=240)
    variant_trim: str = Field(min_length=1, max_length=180)
    chassis_platform_code: str | None = None
    sale_period_from: date | None = None
    sale_period_to: date | None = None
    powertrain: str | None = None
    drivetrain: str | None = None
    body_configuration: str | None = None
    identity_notes: str | None = None
    identity_verification_state: IdentityVerificationState = IdentityVerificationState.RESOLVED_EXACT

    @model_validator(mode="after")
    def valid_years(self) -> "VehicleConfigurationCreate":
        validate_identity_time_basis(
            identity_verification_state=self.identity_verification_state,
            identity_time_basis=self.identity_time_basis,
            model_year_from=self.model_year_from,
            model_year_to=self.model_year_to,
            identity_time_label_raw=self.identity_time_label_raw,
            sale_period_from=self.sale_period_from,
            sale_period_to=self.sale_period_to,
        )
        return self


class SourceDocumentCreate(DomainModel):
    source_code: str = Field(min_length=1, max_length=160)
    title: str = Field(min_length=1, max_length=240)
    publisher: str = Field(min_length=1, max_length=200)
    authority_class: str = Field(min_length=1, max_length=64)
    source_type: str = Field(min_length=1, max_length=64)
    market_code: str | None = Field(default=None, max_length=8)
    publication_year: int | None = Field(default=None, ge=1800, le=2200)
    model_year_from: int | None = Field(default=None, ge=1886, le=2200)
    model_year_to: int | None = Field(default=None, ge=1886, le=2200)
    url: str = Field(min_length=1, max_length=2048)
    retrieved_at: datetime
    local_snapshot_reference: str | None = None
    content_hash: str | None = None
    page_section_default: str | None = None
    access_licensing_notes: str | None = None
    applicability_notes: str | None = None
    archival_status: str | None = None
    notes: str | None = None
    @model_validator(mode="after")
    def valid_years(self) -> "SourceDocumentCreate":
        if self.model_year_to is not None and self.model_year_from is not None and self.model_year_to < self.model_year_from:
            raise ValueError("source model_year_to must not precede model_year_from")
        return self


class SourceObservationCreate(DomainModel):
    vehicle_identity_claim: str = Field(min_length=1)
    source_document_id: str = Field(min_length=1)
    raw_label: str = Field(min_length=1, max_length=240)
    raw_value: str = Field(min_length=1)
    raw_unit: str | None = None
    raw_qualifier: str | None = None
    raw_excerpt: str | None = None
    page_section_locator: str | None = None
    reported_precision: str | None = None
    uncertainty_value: float | None = Field(default=None, ge=0)
    uncertainty_unit: str | None = None
    extraction_method: ExtractionMethod = ExtractionMethod.MANUAL
    extracted_at: datetime
    extracted_by: str | None = None
    reviewer: str | None = None
    ambiguity_note: str | None = None


class LoadConditionCreate(DomainModel):
    name: str = Field(min_length=1, max_length=160)
    mass_basis: MassBasis
    total_mass_kg: float | None = Field(default=None, ge=0)
    occupant_count: int | None = Field(default=None, ge=0)
    payload_kg: float | None = Field(default=None, ge=0)
    front_axle_load_kg: float | None = Field(default=None, ge=0)
    rear_axle_load_kg: float | None = Field(default=None, ge=0)
    front_tyre_pressure: float | None = Field(default=None, ge=0)
    rear_tyre_pressure: float | None = Field(default=None, ge=0)
    tyre_pressure_unit: str | None = None
    suspension_mode: str | None = None
    ride_height_mode: str | None = None
    raw_oem_wording: str | None = None
    source_document_id: str | None = None
    notes: str | None = None


class NormalizedValueCreate(DomainModel):
    parameter_code: str = Field(min_length=1, max_length=160)
    numeric_value: float | None = None
    text_value: str | None = None
    boolean_value: bool | None = None
    enum_value: str | None = None
    json_value: dict[str, Any] | list[Any] | None = None
    canonical_unit: str | None = None
    load_condition_id: str | None = None
    applicability_from: int | None = None
    applicability_to: int | None = None
    evidence_method: EvidenceMethod = EvidenceMethod.NONE
    resolution_state: ResolutionState = ResolutionState.UNCONTESTED
    verification_state: VerificationState = VerificationState.UNREVIEWED
    availability_state: AvailabilityState = AvailabilityState.AVAILABLE
    authority_grade: str | None = None
    applicability_grade: ApplicabilityGrade | None = None
    precision: str | None = None
    uncertainty_value: float | None = Field(default=None, ge=0)
    uncertainty_unit: str | None = None
    normalization_rule_version: str | None = None
    semantic_metadata: dict[str, Any] | None = None
    preferred: bool = False
    reviewed_at: datetime | None = None
    reviewer: str | None = None

    @model_validator(mode="after")
    def value_state_contract(self) -> "NormalizedValueCreate":
        values = [
            self.numeric_value,
            self.text_value,
            self.boolean_value,
            self.enum_value,
            self.json_value,
        ]
        typed_count = sum(value is not None for value in values)
        if self.availability_state == AvailabilityState.AVAILABLE:
            if typed_count != 1:
                raise ValueError("AVAILABLE normalized values require exactly one typed value")
            if self.evidence_method == EvidenceMethod.NONE:
                raise ValueError("AVAILABLE normalized values require evidence or derivation provenance")
        elif typed_count:
            raise ValueError("non-available normalized values must not contain a numeric or typed value")
        if self.evidence_method == EvidenceMethod.DERIVED and not self.normalization_rule_version:
            raise ValueError("DERIVED normalized values require normalization_rule_version")
        if self.applicability_from is not None and self.applicability_to is not None and self.applicability_to < self.applicability_from:
            raise ValueError("applicability_to must not precede applicability_from")
        return self


class EvidenceLinkCreate(DomainModel):
    source_observation_id: str = Field(min_length=1)
    evidence_role: EvidenceRole = EvidenceRole.PRIMARY


class ParameterAssessmentCreate(DomainModel):
    parameter_code: str = Field(min_length=1, max_length=160)
    availability_state: AvailabilityState
    unknown_reason: str = Field(min_length=1)
    source_families_searched: list[str] | None = None
    search_notes: str | None = None
    assessed_at: datetime
    reviewer: str | None = None
    next_action: str | None = None

    @model_validator(mode="after")
    def nonavailable_only(self) -> "ParameterAssessmentCreate":
        if self.availability_state == AvailabilityState.AVAILABLE:
            raise ValueError("parameter assessments are for unknown/not-found/not-applicable states")
        return self


class GeometryAssetCreate(DomainModel):
    geometry_role: GeometryRole
    representation_type: RepresentationType
    geometry_data: dict[str, Any] | list[Any] | None = None
    file_reference: str | None = None
    unit: str = Field(min_length=1, max_length=32)
    coordinate_system_version: str = Field(min_length=1, max_length=80)
    source_coordinate_description: str | None = None
    normalization_transform: dict[str, Any] | list[Any] | None = None
    load_condition_id: str | None = None
    body_mirror_inclusion: WidthEnvelopeDefinition | None = None
    geometry_method: GeometryMethod
    geometry_fidelity: GeometryFidelity
    uncertainty_description: str | None = None
    uncertainty_value: float | None = Field(default=None, ge=0)
    uncertainty_unit: str | None = None
    source_document_id: str | None = None
    derivation_run_id: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def representation_has_content(self) -> "GeometryAssetCreate":
        if self.geometry_data is None and not self.file_reference:
            raise ValueError("geometry assets require geometry_data or file_reference")
        return self


class SteeringRelationCreate(DomainModel):
    axle_id: str = Field(min_length=1)
    steering_role: SteeringRole
    linkage_type: LinkageType
    max_steering_angle_deg: float | None = None
    phase_behavior: PhaseBehavior
    angle_ratio: float | None = None
    relation_function: str | None = None
    speed_min_kph: float | None = Field(default=None, ge=0)
    speed_max_kph: float | None = Field(default=None, ge=0)
    mode_applicability: str | None = None
    source_observation_id: str | None = None
    notes: str | None = None


class ReadinessView(DomainModel):
    readiness_type: ReadinessType
    status: ReadinessStatus
    rule_version: str
    blocking_reasons: list[str]
    supporting_value_ids: list[str]


class AVTMappingView(DomainModel):
    adapter_version: str
    status: str
    payload: dict[str, Any]
    blockers: list[str]
    source_value_ids: list[str]


class TurningSemantics(DomainModel):
    radius_or_diameter: TurningRadiusOrDiameter
    reference: TurningReference
    axle_scope: TurningAxleScope
    wall_envelope_scope: WallEnvelopeScope = WallEnvelopeScope.NOT_APPLICABLE


class ClearanceSemantics(DomainModel):
    clearance_type: ClearanceType
    load_condition_id: str | None = None


class AxleCreate(DomainModel):
    axle_role: AxleRole
    axle_index: int = Field(ge=0)
    longitudinal_position_mm: float | None = None
    axle_group: str | None = None
    driven: bool | None = None
    steered: bool | None = None
    retractable: bool | None = None
    self_steering: bool | None = None
    notes: str | None = None
