from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    model_validator,
)

from app.domain.enums import (
    ApplicabilityGrade,
    AvailabilityState,
    AuthorityClass,
    AxleRole,
    ClearanceType,
    DecisionState,
    EvidenceMethod,
    ExtractionMethod,
    GeometryFidelity,
    GeometryMethod,
    GeometryRole,
    IdentityTimeBasis,
    IdentityVerificationState,
    LinkageType,
    MassBasis,
    PhaseBehavior,
    RepresentationType,
    ResolutionState,
    SourceType,
    SteeringRole,
    VerificationState,
    WidthEnvelopeDefinition,
)
from app.domain.validation import validate_identity_time_basis


StrictNumber = StrictInt | StrictFloat


class ManifestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CurationVehicle(ManifestModel):
    stable_vehicle_code: StrictStr = Field(min_length=1, max_length=160)
    manufacturer_name: StrictStr = Field(min_length=1, max_length=160)
    manufacturer_display_name: StrictStr = Field(min_length=1, max_length=160)
    canonical_model_name: StrictStr = Field(min_length=1, max_length=160)
    display_model_name: StrictStr = Field(min_length=1, max_length=160)
    market_code: StrictStr = Field(min_length=1, max_length=8)
    generation_name: StrictStr = Field(min_length=1, max_length=160)
    body_style: StrictStr = Field(min_length=1, max_length=80)
    chassis_platform_code: StrictStr | None = None
    model_year_from: StrictInt | None = Field(default=None, ge=1886, le=2200)
    model_year_to: StrictInt | None = Field(default=None, ge=1886, le=2200)
    identity_time_basis: IdentityTimeBasis
    identity_time_label_raw: StrictStr | None = Field(default=None, max_length=240)
    sale_period_from: date | None = None
    sale_period_to: date | None = None
    variant_trim: StrictStr = Field(min_length=1, max_length=180)
    powertrain: StrictStr | None = None
    drivetrain: StrictStr | None = None
    body_configuration: StrictStr | None = None
    identity_verification_state: IdentityVerificationState
    identity_notes: StrictStr | None = None

    @model_validator(mode="after")
    def validate_identity(self) -> "CurationVehicle":
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


class CurationSource(ManifestModel):
    source_code: StrictStr = Field(min_length=1, max_length=160)
    publisher: StrictStr = Field(min_length=1, max_length=200)
    authority_class: AuthorityClass
    source_type: SourceType
    source_subtype_raw: StrictStr | None = None
    title: StrictStr = Field(min_length=1, max_length=240)
    url: StrictStr = Field(min_length=1, max_length=2048)
    retrieved_at: datetime
    market_code: StrictStr | None = None
    publication_year: StrictInt | None = Field(default=None, ge=1800, le=2200)
    model_year_from: StrictInt | None = Field(default=None, ge=1886, le=2200)
    model_year_to: StrictInt | None = Field(default=None, ge=1886, le=2200)
    page_section_default: StrictStr | None = None
    applicability_notes: StrictStr | None = None
    access_licensing_notes: StrictStr | None = None
    archival_status: StrictStr | None = None
    local_snapshot_reference: StrictStr | None = None
    content_hash: StrictStr | None = None
    notes: StrictStr | None = None

    @model_validator(mode="after")
    def validate_source(self) -> "CurationSource":
        if self.model_year_to is not None and self.model_year_from is None:
            raise ValueError("source model_year_to requires model_year_from")
        if self.model_year_from is not None and self.model_year_to is not None and self.model_year_to < self.model_year_from:
            raise ValueError("source model_year_to must not precede model_year_from")
        if self.source_type == SourceType.DETERMINISTIC_FIXTURE:
            raise ValueError("DETERMINISTIC_FIXTURE is reserved for Phase 0 fixtures")
        return self


class CurationLoadCondition(ManifestModel):
    load_condition_code: StrictStr = Field(min_length=1, max_length=120)
    name: StrictStr = Field(min_length=1, max_length=160)
    mass_basis: MassBasis
    total_mass_kg: StrictNumber | None = Field(default=None, ge=0)
    occupant_count: StrictInt | None = Field(default=None, ge=0)
    payload_kg: StrictNumber | None = Field(default=None, ge=0)
    front_axle_load_kg: StrictNumber | None = Field(default=None, ge=0)
    rear_axle_load_kg: StrictNumber | None = Field(default=None, ge=0)
    front_tyre_pressure: StrictNumber | None = Field(default=None, ge=0)
    rear_tyre_pressure: StrictNumber | None = Field(default=None, ge=0)
    tyre_pressure_unit: StrictStr | None = None
    suspension_mode: StrictStr | None = None
    ride_height_mode: StrictStr | None = None
    source_code: StrictStr | None = None
    raw_oem_wording: StrictStr | None = None
    notes: StrictStr | None = None


class CurationFitment(ManifestModel):
    fitment_code: StrictStr = Field(min_length=1, max_length=120)
    description: StrictStr | None = None
    wheel_package: StrictStr | None = None
    equipment_package: StrictStr | None = None
    model_year_from: StrictInt | None = Field(default=None, ge=1886, le=2200)
    model_year_to: StrictInt | None = Field(default=None, ge=1886, le=2200)
    default_for_configuration: StrictBool = False
    notes: StrictStr | None = None

    @model_validator(mode="after")
    def validate_years(self) -> "CurationFitment":
        if self.model_year_to is not None and self.model_year_from is None:
            raise ValueError("fitment model_year_to requires model_year_from")
        if self.model_year_from is not None and self.model_year_to is not None and self.model_year_to < self.model_year_from:
            raise ValueError("fitment model_year_to must not precede model_year_from")
        return self


class CurationAxle(ManifestModel):
    axle_code: StrictStr = Field(min_length=1, max_length=120)
    axle_role: AxleRole
    axle_index: StrictInt = Field(ge=0)
    longitudinal_position_mm: StrictNumber | None = None
    axle_group: StrictStr | None = None
    driven: StrictBool | None = None
    steered: StrictBool | None = None
    retractable: StrictBool | None = None
    self_steering: StrictBool | None = None
    notes: StrictStr | None = None


class CurationObservation(ManifestModel):
    observation_code: StrictStr = Field(min_length=1, max_length=160)
    source_code: StrictStr = Field(min_length=1, max_length=160)
    vehicle_identity_claim: StrictStr = Field(min_length=1)
    raw_label: StrictStr = Field(min_length=1, max_length=240)
    raw_value: StrictStr = Field(min_length=1)
    raw_unit: StrictStr | None = None
    raw_qualifier: StrictStr | None = None
    raw_excerpt: StrictStr | None = None
    page_section_locator: StrictStr | None = None
    reported_precision: StrictStr | None = None
    uncertainty_value: StrictNumber | None = Field(default=None, ge=0)
    uncertainty_unit: StrictStr | None = None
    extraction_method: ExtractionMethod
    extracted_at: datetime
    extracted_by: StrictStr | None = None
    reviewer: StrictStr | None = None
    ambiguity_note: StrictStr | None = None


class CurationValue(ManifestModel):
    value_code: StrictStr = Field(min_length=1, max_length=160)
    parameter_code: StrictStr = Field(min_length=1, max_length=160)
    value: Any
    canonical_unit: StrictStr | None = None
    applicability_from: StrictInt | None = None
    applicability_to: StrictInt | None = None
    evidence_method: EvidenceMethod
    resolution_state: ResolutionState
    verification_state: VerificationState
    availability_state: AvailabilityState
    authority_grade: StrictStr | None = None
    applicability_grade: ApplicabilityGrade | None = None
    precision: StrictStr | None = None
    uncertainty_value: StrictNumber | None = Field(default=None, ge=0)
    uncertainty_unit: StrictStr | None = None
    normalization_rule_version: StrictStr | None = None
    semantic_metadata: dict[str, Any] | None = None
    preferred: StrictBool = False
    reviewed_at: datetime | None = None
    reviewer: StrictStr | None = None
    load_condition_code: StrictStr | None = None
    fitment_code: StrictStr | None = None
    evidence_observation_codes: list[StrictStr] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_manifest_value(self) -> "CurationValue":
        if self.evidence_method in {EvidenceMethod.DERIVED, EvidenceMethod.ESTIMATED}:
            raise ValueError("manifest v1 does not allow direct DERIVED or ESTIMATED values")
        if self.evidence_method not in {EvidenceMethod.PUBLISHED, EvidenceMethod.MEASURED}:
            raise ValueError("manifest v1 values must use PUBLISHED or MEASURED evidence")
        if self.availability_state != AvailabilityState.AVAILABLE:
            raise ValueError("missing values must use parameter assessments, not normalized values")
        if not self.evidence_observation_codes:
            raise ValueError("available PUBLISHED/MEASURED values require evidence_observation_codes")
        if self.applicability_from is not None and self.applicability_to is not None and self.applicability_to < self.applicability_from:
            raise ValueError("applicability_to must not precede applicability_from")
        return self


class CurationAssessment(ManifestModel):
    parameter_code: StrictStr = Field(min_length=1, max_length=160)
    availability_state: AvailabilityState
    unknown_reason: StrictStr = Field(min_length=1)
    source_families_searched: list[StrictStr] | None = None
    search_notes: StrictStr | None = None
    assessed_at: datetime
    reviewer: StrictStr | None = None
    next_action: StrictStr | None = None
    fitment_code: StrictStr | None = None

    @model_validator(mode="after")
    def validate_assessment(self) -> "CurationAssessment":
        if self.availability_state == AvailabilityState.AVAILABLE:
            raise ValueError("parameter assessments are for unknown/not-found/not-applicable states")
        return self


class CurationSteeringRelation(ManifestModel):
    axle_code: StrictStr = Field(min_length=1, max_length=120)
    steering_role: SteeringRole
    linkage_type: LinkageType
    max_steering_angle_deg: StrictNumber | None = None
    phase_behavior: PhaseBehavior
    angle_ratio: StrictNumber | None = None
    relation_function: StrictStr | None = None
    speed_min_kph: StrictNumber | None = Field(default=None, ge=0)
    speed_max_kph: StrictNumber | None = Field(default=None, ge=0)
    mode_applicability: StrictStr | None = None
    source_observation_code: StrictStr | None = None
    notes: StrictStr | None = None


class CurationGeometryAsset(ManifestModel):
    geometry_code: StrictStr | None = None
    geometry_role: GeometryRole
    representation_type: RepresentationType
    geometry_data: dict[str, Any] | list[Any] | None = None
    file_reference: StrictStr | None = None
    unit: StrictStr = Field(min_length=1, max_length=32)
    coordinate_system_version: StrictStr = Field(min_length=1, max_length=80)
    source_coordinate_description: StrictStr | None = None
    normalization_transform: dict[str, Any] | list[Any] | None = None
    load_condition_code: StrictStr | None = None
    fitment_code: StrictStr | None = None
    body_mirror_inclusion: WidthEnvelopeDefinition | None = None
    geometry_method: GeometryMethod
    geometry_fidelity: GeometryFidelity
    uncertainty_description: StrictStr | None = None
    uncertainty_value: StrictNumber | None = Field(default=None, ge=0)
    uncertainty_unit: StrictStr | None = None
    source_code: StrictStr | None = None
    derivation_run_id: StrictStr | None = None
    notes: StrictStr | None = None

    @model_validator(mode="after")
    def validate_content(self) -> "CurationGeometryAsset":
        if self.geometry_data is None and not self.file_reference:
            raise ValueError("geometry assets require geometry_data or file_reference")
        if not self.source_code:
            raise ValueError("geometry assets require an exact source_code")
        return self


class CurationConflictDecision(ManifestModel):
    conflict_decision_code: StrictStr | None = None
    parameter_code: StrictStr = Field(min_length=1, max_length=160)
    selected_value_code: StrictStr | None = None
    decision_state: DecisionState
    rationale: StrictStr = Field(min_length=1)
    decided_at: datetime
    reviewer: StrictStr | None = None

    @model_validator(mode="after")
    def validate_selection(self) -> "CurationConflictDecision":
        if self.decision_state == DecisionState.SELECTED and not self.selected_value_code:
            raise ValueError("SELECTED conflict decisions require selected_value_code")
        if self.decision_state != DecisionState.SELECTED and self.selected_value_code is not None:
            raise ValueError("only SELECTED conflict decisions may select a value")
        return self


def _unique_codes(items: list[Any], field: str, section: str) -> set[str]:
    codes = [getattr(item, field) for item in items]
    if len(codes) != len(set(codes)):
        raise ValueError(f"{section} contains duplicate {field} values")
    return set(codes)


class CurationManifest(ManifestModel):
    manifest_version: Literal["1.0"]
    mode: Literal["CREATE_ONLY"]
    record_id: StrictStr = Field(min_length=1, max_length=200)
    vehicle: CurationVehicle
    sources: list[CurationSource] = Field(default_factory=list)
    load_conditions: list[CurationLoadCondition] = Field(default_factory=list)
    fitments: list[CurationFitment] = Field(default_factory=list)
    axles: list[CurationAxle] = Field(default_factory=list)
    observations: list[CurationObservation] = Field(default_factory=list)
    values: list[CurationValue] = Field(default_factory=list)
    assessments: list[CurationAssessment] = Field(default_factory=list)
    steering_relations: list[CurationSteeringRelation] = Field(default_factory=list)
    geometry_assets: list[CurationGeometryAsset] = Field(default_factory=list)
    conflict_decisions: list[CurationConflictDecision] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_references(self) -> "CurationManifest":
        source_codes = _unique_codes(self.sources, "source_code", "sources")
        load_codes = _unique_codes(self.load_conditions, "load_condition_code", "load_conditions")
        fitment_codes = _unique_codes(self.fitments, "fitment_code", "fitments")
        axle_codes = _unique_codes(self.axles, "axle_code", "axles")
        observation_codes = _unique_codes(self.observations, "observation_code", "observations")
        value_codes = _unique_codes(self.values, "value_code", "values")
        decision_codes = {
            code
            for code in [item.conflict_decision_code for item in self.conflict_decisions]
            if code is not None
        }
        if len(decision_codes) != sum(item.conflict_decision_code is not None for item in self.conflict_decisions):
            raise ValueError("conflict_decisions contains duplicate conflict_decision_code values")

        for observation in self.observations:
            if observation.source_code not in source_codes:
                raise ValueError(f"observation {observation.observation_code} references undeclared source {observation.source_code}")
        for load in self.load_conditions:
            if load.source_code is not None and load.source_code not in source_codes:
                raise ValueError(f"load condition {load.load_condition_code} references undeclared source {load.source_code}")
        for value in self.values:
            if value.load_condition_code is not None and value.load_condition_code not in load_codes:
                raise ValueError(f"value {value.value_code} references undeclared load condition {value.load_condition_code}")
            if value.fitment_code is not None and value.fitment_code not in fitment_codes:
                raise ValueError(f"value {value.value_code} references undeclared fitment {value.fitment_code}")
            for observation_code in value.evidence_observation_codes:
                if observation_code not in observation_codes:
                    raise ValueError(f"value {value.value_code} references undeclared observation {observation_code}")
            if len(value.evidence_observation_codes) != len(set(value.evidence_observation_codes)):
                raise ValueError(f"value {value.value_code} contains duplicate evidence observation codes")
        for assessment in self.assessments:
            if assessment.fitment_code is not None and assessment.fitment_code not in fitment_codes:
                raise ValueError(f"assessment {assessment.parameter_code} references undeclared fitment {assessment.fitment_code}")
        for relation in self.steering_relations:
            if relation.axle_code not in axle_codes:
                raise ValueError(f"steering relation references undeclared axle {relation.axle_code}")
            if relation.source_observation_code is not None and relation.source_observation_code not in observation_codes:
                raise ValueError(
                    f"steering relation references undeclared observation {relation.source_observation_code}"
                )
        for asset in self.geometry_assets:
            if asset.load_condition_code is not None and asset.load_condition_code not in load_codes:
                raise ValueError(f"geometry asset references undeclared load condition {asset.load_condition_code}")
            if asset.fitment_code is not None and asset.fitment_code not in fitment_codes:
                raise ValueError(f"geometry asset references undeclared fitment {asset.fitment_code}")
            if asset.source_code is not None and asset.source_code not in source_codes:
                raise ValueError(f"geometry asset references undeclared source {asset.source_code}")
        for decision in self.conflict_decisions:
            if decision.selected_value_code is not None and decision.selected_value_code not in value_codes:
                raise ValueError(
                    f"conflict decision references undeclared value {decision.selected_value_code}"
                )
        return self
