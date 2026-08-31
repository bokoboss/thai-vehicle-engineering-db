from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    ConflictDecision,
    GeometryAsset,
    LoadCondition,
    NormalizedValue,
    ParameterDefinition,
    QAFinding,
    ReadinessResult,
    SourceDocument,
    SourceObservation,
    VehicleConfiguration,
)
from app.domain.avt_mapping import persist_avt_mapping
from app.domain.derivations import derive_avt_track_estimate, derive_screening_breakover
from app.domain.enums import (
    ApplicabilityGrade,
    AvailabilityState,
    AxleRole,
    AuthorityClass,
    ClearanceType,
    DecisionState,
    EvidenceMethod,
    EvidenceRole,
    ExtractionMethod,
    GeometryFidelity,
    GeometryMethod,
    GeometryRole,
    LinkageType,
    MassBasis,
    PhaseBehavior,
    QAFindingStatus,
    ReadinessStatus,
    ResolutionState,
    Severity,
    SourceType,
    SteeringRole,
    TrackDefinition,
    TurningAxleScope,
    TurningRadiusOrDiameter,
    TurningReference,
    VerificationState,
    WallEnvelopeScope,
    WidthEnvelopeDefinition,
)
from app.domain.readiness import persist_readiness
from app.domain.schemas import (
    AxleCreate,
    EvidenceLinkCreate,
    GeometryAssetCreate,
    LoadConditionCreate,
    NormalizedValueCreate,
    ParameterAssessmentCreate,
    SourceDocumentCreate,
    SourceObservationCreate,
    SteeringRelationCreate,
    VehicleConfigurationCreate,
)
from app.services.foundation import (
    create_axle,
    create_geometry_asset,
    create_load_condition,
    create_normalized_value,
    create_parameter_assessment,
    create_source_document,
    create_source_observation,
    create_steering_relation,
    create_vehicle_configuration,
)


FIXTURE_NOTE = "Deterministic Phase 0 contract fixture; not a production vehicle curation record."
FIXTURE_TIME = datetime(2026, 8, 30, 0, 0, tzinfo=timezone.utc)


@dataclass
class FixtureContext:
    config: VehicleConfiguration
    source: SourceDocument


def _source(session: Session, code: str, title: str, *, authority: str = AuthorityClass.OEM_THAILAND.value) -> SourceDocument:
    existing = session.scalar(select(SourceDocument).where(SourceDocument.source_code == code))
    if existing:
        return existing
    return create_source_document(
        session,
        SourceDocumentCreate(
            source_code=code,
            title=title,
            publisher="Phase 0 deterministic fixture author",
            authority_class=authority,
            source_type=SourceType.DETERMINISTIC_FIXTURE.value,
            market_code="TEST",
            url=f"https://example.invalid/thai-vehicle-engineering-db/fixtures/{code}",
            retrieved_at=FIXTURE_TIME,
            archival_status="FIXTURE_ONLY",
            notes=FIXTURE_NOTE,
        ),
    )


def _config(session: Session, code: str, variant: str, *, body_style: str = "fixture") -> VehicleConfiguration:
    existing = session.scalar(select(VehicleConfiguration).where(VehicleConfiguration.stable_vehicle_code == code))
    if existing:
        return existing
    return create_vehicle_configuration(
        session,
        VehicleConfigurationCreate(
            stable_vehicle_code=code,
            market_code="TEST",
            generation_name="Phase 0 semantic fixture generation",
            body_style=body_style,
            model_year_from=2026,
            variant_trim=variant,
            chassis_platform_code="FIXTURE-V1",
            powertrain="semantic test configuration",
            drivetrain="not applicable",
            body_configuration="fixture-only",
            identity_notes=FIXTURE_NOTE,
        ),
        manufacturer_name="Phase 0 Contract Fixtures",
        canonical_model_name="Evidence-first semantic fixture set",
        display_model_name="Evidence-first semantic fixtures",
    )


def _observation(
    session: Session,
    config: VehicleConfiguration,
    source: SourceDocument,
    label: str,
    value: str,
    unit: str | None,
    *,
    qualifier: str | None = None,
    ambiguity: str | None = None,
    extraction_method: ExtractionMethod = ExtractionMethod.MANUAL,
    uncertainty_value: float | None = None,
    uncertainty_unit: str | None = None,
) -> SourceObservation:
    return create_source_observation(
        session,
        config,
        SourceObservationCreate(
            vehicle_identity_claim=config.stable_vehicle_code,
            source_document_id=source.id,
            raw_label=label,
            raw_value=value,
            raw_unit=unit,
            raw_qualifier=qualifier,
            page_section_locator="fixture-record",
            reported_precision="as supplied by fixture",
            uncertainty_value=uncertainty_value,
            uncertainty_unit=uncertainty_unit,
            extraction_method=extraction_method,
            extracted_at=FIXTURE_TIME,
            extracted_by="phase-0-fixture-builder",
            ambiguity_note=ambiguity,
        ),
    )


def _definition(session: Session, code: str) -> ParameterDefinition:
    definition = session.scalar(select(ParameterDefinition).where(ParameterDefinition.parameter_code == code))
    if definition is None:
        raise RuntimeError(f"parameter registry missing fixture parameter {code}")
    return definition


def _value(
    session: Session,
    config: VehicleConfiguration,
    code: str,
    raw_value: Any,
    source_observation: SourceObservation | None = None,
    *,
    method: EvidenceMethod = EvidenceMethod.PUBLISHED,
    resolution: ResolutionState = ResolutionState.UNCONTESTED,
    verification: VerificationState = VerificationState.VERIFIED,
    availability: AvailabilityState = AvailabilityState.AVAILABLE,
    metadata: dict[str, Any] | None = None,
    load_condition: LoadCondition | None = None,
    uncertainty_value: float | None = None,
    uncertainty_unit: str | None = None,
    preferred: bool = False,
    normalization_rule_version: str | None = None,
) -> NormalizedValue:
    definition = _definition(session, code)
    typed: dict[str, Any] = {}
    if availability == AvailabilityState.AVAILABLE:
        field = {
            "NUMBER": "numeric_value",
            "TEXT": "text_value",
            "BOOLEAN": "boolean_value",
            "ENUM": "enum_value",
            "JSON": "json_value",
        }[definition.data_type]
        typed[field] = raw_value
    payload = NormalizedValueCreate(
        parameter_code=code,
        **typed,
        canonical_unit=definition.canonical_unit,
        load_condition_id=load_condition.id if load_condition else None,
        evidence_method=method,
        resolution_state=resolution,
        verification_state=verification,
        availability_state=availability,
        authority_grade="A1" if method == EvidenceMethod.PUBLISHED else None,
        applicability_grade=ApplicabilityGrade.EXACT_CONFIGURATION,
        uncertainty_value=uncertainty_value,
        uncertainty_unit=uncertainty_unit,
        normalization_rule_version=normalization_rule_version,
        semantic_metadata=metadata,
        preferred=preferred,
        reviewed_at=FIXTURE_TIME if verification in {VerificationState.REVIEWED, VerificationState.VERIFIED} else None,
        reviewer="phase-0-fixture-reviewer",
    )
    links = []
    if source_observation is not None:
        links.append(EvidenceLinkCreate(source_observation_id=source_observation.id, evidence_role=EvidenceRole.PRIMARY))
    return create_normalized_value(session, config, payload, evidence_links=links)


def _assessment(session: Session, config: VehicleConfiguration, code: str, state: AvailabilityState, reason: str) -> None:
    create_parameter_assessment(
        session,
        config,
        ParameterAssessmentCreate(
            parameter_code=code,
            availability_state=state,
            unknown_reason=reason,
            source_families_searched=["Thai OEM specification", "OEM technical/service source", "controlled measurement"],
            search_notes="Deterministic fixture deliberately records the unresolved semantic/data state.",
            assessed_at=FIXTURE_TIME,
            reviewer="phase-0-fixture-reviewer",
            next_action="Obtain a source with explicit semantics before normalization.",
        ),
    )


def _basic_axles(session: Session, config: VehicleConfiguration, *, rear_steered: bool = False):
    front = create_axle(
        session,
        config,
        AxleCreate(
            axle_role=AxleRole.FRONT,
            axle_index=0,
            longitudinal_position_mm=0,
            steered=True,
            driven=False,
        ),
    )
    rear = create_axle(
        session,
        config,
        AxleCreate(
            axle_role=AxleRole.REAR,
            axle_index=1,
            longitudinal_position_mm=2700,
            steered=rear_steered,
            driven=True,
        ),
    )
    return front, rear


def _basic_dimensions(session: Session, config: VehicleConfiguration, source: SourceDocument) -> None:
    for code, label, value, unit in (
        ("overall_length_mm", "Overall length", 4500, "mm"),
        ("overall_height_mm", "Overall height", 1650, "mm"),
        ("overall_width_reported_mm", "Overall width", 1850, "mm"),
        ("wheelbase_actual_mm", "Wheelbase", 2700, "mm"),
    ):
        observation = _observation(session, config, source, label, str(value), unit)
        _value(session, config, code, value, observation)


def _add_qa_for_blockers(session: Session, config: VehicleConfiguration) -> None:
    existing = session.scalar(select(QAFinding).where(QAFinding.vehicle_configuration_id == config.id))
    if existing:
        return
    readiness = session.scalars(
        select(ReadinessResult).where(
            ReadinessResult.vehicle_configuration_id == config.id,
            ReadinessResult.status != ReadinessStatus.READY.value,
        )
    ).first()
    if readiness is None:
        return
    session.add(
        QAFinding(
            vehicle_configuration_id=config.id,
            finding_code=f"{readiness.readiness_type}_BLOCKED",
            severity=Severity.WARNING.value,
            status=QAFindingStatus.OPEN.value,
            message="; ".join(readiness.blocking_reasons),
            created_at=FIXTURE_TIME,
        )
    )
    session.flush()


def seed_phase0_fixtures(session: Session) -> dict[str, VehicleConfiguration]:
    """Insert idempotent semantic fixtures for local qualification and demo pages."""

    existing = {
        config.stable_vehicle_code: config
        for config in session.scalars(select(VehicleConfiguration)).all()
        if config.stable_vehicle_code.startswith("FIXTURE-")
    }
    if existing:
        return existing

    # 1. Exact primary published value.
    config = _config(session, "FIXTURE-PRIMARY-PUBLISHED", "Exact primary published value")
    source = _source(session, "fixture-primary", "Primary published value fixture")
    observation = _observation(session, config, source, "Wheelbase", "2700", "mm")
    _value(session, config, "wheelbase_actual_mm", 2700, observation)

    # 2. OEM turning value with unresolved curb/wall semantics.
    config = _config(session, "FIXTURE-TURNING-UNSPECIFIED", "OEM turning value with unknown envelope")
    source = _source(session, "fixture-turning-unspecified", "Turning semantic ambiguity fixture")
    observation = _observation(session, config, source, "Minimum turning radius", "5.35", "m", ambiguity="Curb/wall reference not stated")
    _value(session, config, "oem_turning_value_text", "5.35 m", observation)
    _value(
        session,
        config,
        "turning_radius_normalized_m",
        5.35,
        observation,
        metadata={
            "turning_radius_or_diameter": TurningRadiusOrDiameter.RADIUS.value,
            "turning_reference": TurningReference.OEM_UNSPECIFIED.value,
            "turning_axle_scope": TurningAxleScope.OEM_UNSPECIFIED.value,
            "turning_wall_envelope_scope": WallEnvelopeScope.OEM_UNSPECIFIED.value,
        },
    )

    # 3. Published + conflicting observations retained with an auditable preference.
    config = _config(session, "FIXTURE-CONFLICTING-VALUE", "Published value with conflicting evidence")
    source_a = _source(session, "fixture-conflict-a", "Conflicting source A")
    source_b = _source(session, "fixture-conflict-b", "Conflicting source B")
    observation_a = _observation(session, config, source_a, "Overall length", "4500", "mm")
    observation_b = _observation(session, config, source_b, "Overall length", "4520", "mm")
    value_a = _value(
        session,
        config,
        "overall_length_mm",
        4500,
        observation_a,
        resolution=ResolutionState.CONFLICTING,
        verification=VerificationState.REVIEWED,
        preferred=True,
    )
    value_b = _value(
        session,
        config,
        "overall_length_mm",
        4520,
        observation_b,
        resolution=ResolutionState.CONFLICTING,
    )
    session.add(
        ConflictDecision(
            vehicle_configuration_id=config.id,
            parameter_definition_id=_definition(session, "overall_length_mm").id,
            selected_normalized_value_id=value_a.id,
            decision_state=DecisionState.SELECTED.value,
            rationale="Fixture demonstrates that preference selects a candidate without deleting the conflicting observation/value.",
            decided_at=FIXTURE_TIME,
            reviewer="phase-0-fixture-reviewer",
        )
    )
    session.flush()

    # 4. Centerline tread + nominal tyre width estimate retained as screening only.
    config = _config(session, "FIXTURE-AVT-TRACK-SCREENING", "Rejected nominal-width AVT track estimate")
    source = _source(session, "fixture-avt-track-screening", "AVT track screening estimate fixture")
    front_track_obs = _observation(session, config, source, "Front OEM tread", "1575", "mm", ambiguity="Centerline/outer-face definition not established")
    rear_track_obs = _observation(session, config, source, "Rear OEM tread", "1580", "mm", ambiguity="Centerline/outer-face definition not established")
    front_width_obs = _observation(session, config, source, "Front nominal tyre section width", "235", "mm")
    rear_width_obs = _observation(session, config, source, "Rear nominal tyre section width", "235", "mm")
    front_track = _value(
        session,
        config,
        "oem_front_tread_or_track_mm",
        1575,
        front_track_obs,
        metadata={"track_definition": TrackDefinition.TYRE_CENTERLINE.value},
    )
    rear_track = _value(
        session,
        config,
        "oem_rear_tread_or_track_mm",
        1580,
        rear_track_obs,
        metadata={"track_definition": TrackDefinition.TYRE_CENTERLINE.value},
    )
    front_width = _value(session, config, "front_nominal_section_width_mm", 235, front_width_obs)
    rear_width = _value(session, config, "rear_nominal_section_width_mm", 235, rear_width_obs)
    derive_avt_track_estimate(
        session,
        config,
        centerline_value=front_track,
        nominal_section_width_value=front_width,
        output_parameter_code="avt_front_outer_face_track_mm",
    )
    derive_avt_track_estimate(
        session,
        config,
        centerline_value=rear_track,
        nominal_section_width_value=rear_width,
        output_parameter_code="avt_rear_outer_face_track_mm",
    )
    _basic_axles(session, config)

    # 5. Direct outer-face track with the other AVT fields needed for a positive fixture.
    config = _config(session, "FIXTURE-AVT-TRACK-DIRECT", "Direct AVT outer-face track")
    source = _source(session, "fixture-avt-track-direct", "Direct AVT outer-face track fixture")
    _basic_dimensions(session, config, source)
    front, rear = _basic_axles(session, config)
    for code, label, track in (
        ("avt_front_outer_face_track_mm", "Mounted front outer tyre-face track", 1810),
        ("avt_rear_outer_face_track_mm", "Mounted rear outer tyre-face track", 1820),
    ):
        observation = _observation(session, config, source, label, str(track), "mm")
        _value(
            session,
            config,
            code,
            track,
            observation,
            metadata={
                "track_definition": TrackDefinition.OUTER_TYRE_FACES.value,
                "source_basis": "DIRECT_OUTER_FACE_EVIDENCE",
                "screening_only": False,
            },
        )
    turning_obs = _observation(session, config, source, "Minimum turning radius (curb-to-curb)", "5.4", "m")
    _value(
        session,
        config,
        "turning_radius_normalized_m",
        5.4,
        turning_obs,
        metadata={
            "turning_radius_or_diameter": TurningRadiusOrDiameter.RADIUS.value,
            "turning_reference": TurningReference.CURB_TO_CURB.value,
            "turning_axle_scope": TurningAxleScope.ALL_AXLES.value,
            "turning_wall_envelope_scope": WallEnvelopeScope.NOT_APPLICABLE.value,
        },
    )
    for code, label, value in (
        ("avt_maximum_steering_angle_deg", "AVT Maximum Steering Angle", 34.0),
        ("avt_lock_to_lock_time_forward_s", "AVT forward lock-to-lock time", 4.0),
        ("avt_lock_to_lock_time_reverse_s", "AVT reverse lock-to-lock time", 4.5),
    ):
        observation = _observation(session, config, source, label, str(value), "deg" if code.endswith("deg") else "s")
        _value(session, config, code, value, observation, metadata={"explicit_avt_field": True})
    create_geometry_asset(
        session,
        config,
        GeometryAssetCreate(
            geometry_role=GeometryRole.AVT_PLAN_PROFILE,
            representation_type="POLYGON",
            geometry_data={"coordinates": [[0, -905], [0, 905], [4500, 910], [4500, -910]]},
            unit="mm",
            coordinate_system_version="vehicle-fixed-v1",
            source_coordinate_description="Fixture datum: front axle centreline at origin; +X rearward.",
            body_mirror_inclusion=WidthEnvelopeDefinition.BODY_EXCLUDING_MIRRORS,
            geometry_method=GeometryMethod.OEM_DIMENSION_DRAWING,
            geometry_fidelity=GeometryFidelity.MEDIUM,
            uncertainty_description="Deterministic geometry fixture; not a production body polygon.",
            uncertainty_value=10,
            uncertainty_unit="mm",
            source_document_id=source.id,
        ),
    )

    # 6. Unknown/not-found assessment with no numeric placeholder.
    config = _config(session, "FIXTURE-UNKNOWN-ASSESSMENT", "Unknown parameter assessment")
    _assessment(
        session,
        config,
        "maximum_inner_road_wheel_angle_deg",
        AvailabilityState.NOT_FOUND_AFTER_SEARCH,
        "No defensible actual road-wheel lock angle in the searched source families.",
    )

    # 7. Image-scaled estimate with explicit uncertainty and raw evidence.
    config = _config(session, "FIXTURE-SCALED-ESTIMATE", "Measured or scaled estimate with uncertainty")
    source = _source(session, "fixture-scaled-estimate", "Scaled drawing estimate fixture")
    observation = _observation(
        session,
        config,
        source,
        "Front overhang (scaled drawing)",
        "760",
        "mm",
        extraction_method=ExtractionMethod.IMAGE_SCALE,
        uncertainty_value=15,
        uncertainty_unit="mm",
    )
    _value(
        session,
        config,
        "front_overhang_mm",
        760,
        observation,
        method=EvidenceMethod.ESTIMATED,
        verification=VerificationState.REVIEWED,
        uncertainty_value=15,
        uncertainty_unit="mm",
        metadata={"estimation_method": "IMAGE_SCALE", "limitations": "Scaled drawing, not a direct measurement."},
    )

    # 8. Steering-wheel turns, actual wheel angle and AVT transition time remain separate.
    config = _config(session, "FIXTURE-STEERING-SEPARATION", "Steering semantic separation")
    source = _source(session, "fixture-steering-separation", "Steering field separation fixture")
    turns_obs = _observation(session, config, source, "Steering wheel turns lock-to-lock", "2.4", "turns")
    angle_obs = _observation(session, config, source, "Maximum inner road-wheel angle", "34", "deg")
    _value(session, config, "steering_wheel_lock_to_lock_turns", 2.4, turns_obs)
    _value(session, config, "maximum_inner_road_wheel_angle_deg", 34, angle_obs, method=EvidenceMethod.MEASURED, verification=VerificationState.REVIEWED)
    _assessment(session, config, "avt_lock_to_lock_time_forward_s", AvailabilityState.UNKNOWN, "Steering-wheel turns do not establish elapsed AVT steering-transition time.")
    _assessment(session, config, "avt_lock_to_lock_time_reverse_s", AvailabilityState.UNKNOWN, "Steering-wheel turns do not establish elapsed AVT steering-transition time.")

    # 9. Curb-to-curb turning with unresolved axle scope.
    config = _config(session, "FIXTURE-CURB-UNKNOWN-AXLE", "Curb-to-curb with unresolved axle scope")
    source = _source(session, "fixture-curb-unknown-axle", "Curb turning axle-scope fixture")
    observation = _observation(session, config, source, "Turning circle (curb-to-curb)", "10.8", "m")
    _value(
        session,
        config,
        "turning_radius_normalized_m",
        5.4,
        observation,
        metadata={
            "turning_radius_or_diameter": TurningRadiusOrDiameter.RADIUS.value,
            "turning_reference": TurningReference.CURB_TO_CURB.value,
            "turning_axle_scope": TurningAxleScope.OEM_UNSPECIFIED.value,
            "turning_wall_envelope_scope": WallEnvelopeScope.NOT_APPLICABLE.value,
            "source_value_was": "DIAMETER 10.8 m",
        },
        normalization_rule_version="turning-circle-to-radius:1",
    )

    # 10. Wall-to-wall scope is represented independently for body-only and body+loads.
    config = _config(session, "FIXTURE-WALL-SCOPES", "Wall-to-wall envelope scopes")
    source = _source(session, "fixture-wall-scopes", "Wall envelope scope fixture")
    body_obs = _observation(session, config, source, "Wall-to-wall radius body only", "6.2", "m")
    loads_obs = _observation(session, config, source, "Wall-to-wall radius body and loads", "6.5", "m")
    common_turning = {
        "turning_radius_or_diameter": TurningRadiusOrDiameter.RADIUS.value,
        "turning_reference": TurningReference.WALL_TO_WALL.value,
        "turning_axle_scope": TurningAxleScope.ALL_AXLES.value,
    }
    _value(session, config, "turning_radius_normalized_m", 6.2, body_obs, metadata={**common_turning, "turning_wall_envelope_scope": WallEnvelopeScope.BODY_ONLY.value})
    _value(session, config, "turning_radius_normalized_m", 6.5, loads_obs, metadata={**common_turning, "turning_wall_envelope_scope": WallEnvelopeScope.BODY_AND_LOADS.value})

    # 11–12. Clearance types and structured load applicability remain explicit.
    config = _config(session, "FIXTURE-CLEARANCE-LOADS", "Clearance taxonomy and load conditions")
    source = _source(session, "fixture-clearance-loads", "Clearance/load-state fixture")
    laden = create_load_condition(
        session,
        config,
        LoadConditionCreate(
            name="OEM laden between-axles condition",
            mass_basis=MassBasis.OEM_LADEN,
            total_mass_kg=1980,
            occupant_count=5,
            payload_kg=350,
            front_axle_load_kg=980,
            rear_axle_load_kg=1000,
            front_tyre_pressure=2.4,
            rear_tyre_pressure=2.5,
            tyre_pressure_unit="bar",
            suspension_mode="normal",
            ride_height_mode="laden static",
            raw_oem_wording="Ground clearance between axles, laden",
            source_document_id=source.id,
        ),
    )
    unladen = create_load_condition(
        session,
        config,
        LoadConditionCreate(
            name="Unladen front axle condition",
            mass_basis=MassBasis.UNLADEN,
            total_mass_kg=1600,
            occupant_count=0,
            front_tyre_pressure=2.3,
            rear_tyre_pressure=2.3,
            tyre_pressure_unit="bar",
            suspension_mode="normal",
            ride_height_mode="unladen static",
            raw_oem_wording="Minimum clearance at front axle, unladen",
            source_document_id=source.id,
        ),
    )
    laden_obs = _observation(session, config, source, "Ground clearance between axles, laden", "135", "mm")
    front_obs = _observation(session, config, source, "Front axle clearance, unladen", "160", "mm")
    _value(
        session,
        config,
        "clearance_value_mm",
        135,
        laden_obs,
        load_condition=laden,
        metadata={"clearance_type": ClearanceType.BETWEEN_AXLES.value, "load_state": "OEM_LADEN"},
    )
    _value(
        session,
        config,
        "clearance_value_mm",
        160,
        front_obs,
        load_condition=unladen,
        metadata={"clearance_type": ClearanceType.FRONT_AXLE.value, "load_state": "UNLADEN"},
    )

    # 13. Static-loaded tyre radius with load and pressure provenance.
    config = _config(session, "FIXTURE-STATIC-LOADED-RADIUS", "Static-loaded tyre radius")
    source = _source(session, "fixture-static-loaded-radius", "Static-loaded tyre radius fixture")
    load = create_load_condition(
        session,
        config,
        LoadConditionCreate(
            name="Measured static-loaded radius condition",
            mass_basis=MassBasis.KERB,
            total_mass_kg=1800,
            occupant_count=1,
            front_tyre_pressure=2.5,
            rear_tyre_pressure=2.6,
            tyre_pressure_unit="bar",
            suspension_mode="normal",
            ride_height_mode="kerb plus one person",
            source_document_id=source.id,
        ),
    )
    for code, label, radius in (
        ("static_loaded_tyre_radius_front_mm", "Measured static-loaded front tyre radius", 320),
        ("static_loaded_tyre_radius_rear_mm", "Measured static-loaded rear tyre radius", 322),
    ):
        observation = _observation(session, config, source, label, str(radius), "mm", extraction_method=ExtractionMethod.PHYSICAL_MEASUREMENT, uncertainty_value=3, uncertainty_unit="mm")
        _value(
            session,
            config,
            code,
            radius,
            observation,
            method=EvidenceMethod.MEASURED,
            verification=VerificationState.REVIEWED,
            load_condition=load,
            uncertainty_value=3,
            uncertainty_unit="mm",
            metadata={"radius_kind": "STATIC_LOADED", "load_condition_provenance": load.id},
        )

    # 14. Four-wheel/rear-steering structure with axle/linkage/mode semantics.
    config = _config(session, "FIXTURE-REAR-STEERING", "Four-wheel steering structural fixture")
    source = _source(session, "fixture-rear-steering", "Rear/four-wheel steering fixture")
    observation = _observation(session, config, source, "Intelligent four-wheel steering system", "present", None, ambiguity="Fixture describes the system but not a conventional fixed rear axle.")
    front, rear = _basic_axles(session, config, rear_steered=True)
    create_steering_relation(
        session,
        config,
        SteeringRelationCreate(
            axle_id=front.id,
            steering_role=SteeringRole.PRIMARY,
            linkage_type=LinkageType.FIXED_RATIO,
            max_steering_angle_deg=35,
            phase_behavior=PhaseBehavior.SAME_PHASE,
            relation_function="Primary front steering fixture relation",
            source_observation_id=observation.id,
        ),
    )
    create_steering_relation(
        session,
        config,
        SteeringRelationCreate(
            axle_id=rear.id,
            steering_role=SteeringRole.SECONDARY,
            linkage_type=LinkageType.MODE_DEPENDENT,
            max_steering_angle_deg=8,
            phase_behavior=PhaseBehavior.MODE_OR_SPEED_DEPENDENT,
            angle_ratio=-0.25,
            relation_function="Opposite phase at low speed; mode/speed-dependent behaviour retained as a function.",
            speed_min_kph=0,
            speed_max_kph=120,
            mode_applicability="Low-speed manoeuvre and high-speed stability modes",
            source_observation_id=observation.id,
        ),
    )

    # 15. Generic source width stays reported/unknown; no body-width promotion.
    config = _config(session, "FIXTURE-WIDTH-UNSPECIFIED", "Source width with unknown mirror semantics")
    source = _source(session, "fixture-width-unspecified", "Width mirror-semantics fixture")
    observation = _observation(session, config, source, "Overall Width", "1875", "mm", ambiguity="Mirror inclusion not stated")
    _value(
        session,
        config,
        "overall_width_reported_mm",
        1875,
        observation,
        metadata={"width_envelope_definition": WidthEnvelopeDefinition.OEM_UNSPECIFIED.value},
    )
    _assessment(session, config, "overall_width_body_mm", AvailabilityState.UNKNOWN, "Overall Width source wording does not establish body-only/mirror semantics.")

    # 16. Side silhouette and longitudinal lower envelope are separate assets.
    config = _config(session, "FIXTURE-GEOMETRY-ROLES", "Geometry role separation")
    source = _source(session, "fixture-geometry-roles", "Geometry role separation fixture")
    create_geometry_asset(
        session,
        config,
        GeometryAssetCreate(
            geometry_role=GeometryRole.SIDE_SILHOUETTE,
            representation_type="POLYLINE",
            geometry_data={"points": [[0, 0], [4500, 0], [4500, 1650], [0, 1650]]},
            unit="mm",
            coordinate_system_version="vehicle-fixed-v1",
            geometry_method=GeometryMethod.SCALED_DRAWING,
            geometry_fidelity=GeometryFidelity.LOW,
            uncertainty_description="Exterior silhouette scale uncertainty.",
            uncertainty_value=20,
            uncertainty_unit="mm",
            source_document_id=source.id,
        ),
    )
    create_geometry_asset(
        session,
        config,
        GeometryAssetCreate(
            geometry_role=GeometryRole.LONGITUDINAL_LOWER_ENVELOPE,
            representation_type="POLYLINE",
            geometry_data={"points": [[0, 320], [800, 220], [2700, 135], [3700, 200], [4500, 300]]},
            unit="mm",
            coordinate_system_version="vehicle-fixed-v1",
            geometry_method=GeometryMethod.PHYSICAL_SURVEY,
            geometry_fidelity=GeometryFidelity.MEDIUM,
            uncertainty_description="Lower-envelope survey uncertainty.",
            uncertainty_value=8,
            uncertainty_unit="mm",
            source_document_id=source.id,
        ),
    )

    # 17. Screening angle uses only its own namespace and controlled derivation lineage.
    config = _config(session, "FIXTURE-RAMP-SCREENING", "Ramp screening namespace")
    source = _source(session, "fixture-ramp-screening", "Ramp screening derivation fixture")
    load = create_load_condition(
        session,
        config,
        LoadConditionCreate(
            name="Screening laden condition",
            mass_basis=MassBasis.DESIGN_LOAD,
            total_mass_kg=1900,
            occupant_count=5,
            tyre_pressure_unit="bar",
            suspension_mode="normal",
            ride_height_mode="screening assumption",
            source_document_id=source.id,
        ),
    )
    clearance_obs = _observation(session, config, source, "Between-axles clearance used for screening", "135", "mm")
    wheelbase_obs = _observation(session, config, source, "Wheelbase used for screening", "2700", "mm")
    clearance = _value(
        session,
        config,
        "clearance_value_mm",
        135,
        clearance_obs,
        load_condition=load,
        metadata={"clearance_type": ClearanceType.BETWEEN_AXLES.value, "screening_assumption": True},
    )
    wheelbase = _value(session, config, "wheelbase_actual_mm", 2700, wheelbase_obs)
    derive_screening_breakover(session, config, clearance_value=clearance, wheelbase_value=wheelbase)

    # Persist rule-derived readiness and mapping records after all values/assets exist.
    configs = list(session.scalars(select(VehicleConfiguration).where(VehicleConfiguration.stable_vehicle_code.like("FIXTURE-%"))).all())
    for fixture_config in configs:
        persist_readiness(session, fixture_config)
        if fixture_config.stable_vehicle_code == "FIXTURE-AVT-TRACK-DIRECT":
            persist_avt_mapping(session, fixture_config)
        _add_qa_for_blockers(session, fixture_config)
    session.flush()
    return {config.stable_vehicle_code: config for config in configs}
