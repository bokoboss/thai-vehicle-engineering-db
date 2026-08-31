from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from app.db.models import (
    ConflictDecision,
    NormalizedValue,
    ParameterDefinition,
    SourceObservation,
    VehicleConfiguration,
)
from app.domain.avt_mapping import build_avt_mapping
from app.domain.derivations import derive_avt_track_estimate, derive_nominal_tyre_radius, register_derivation_rule
from app.domain.enums import (
    AvailabilityState,
    DecisionState,
    EvidenceMethod,
    GeometryFidelity,
    GeometryMethod,
    GeometryRole,
    LinkageType,
    MassBasis,
    PhaseBehavior,
    ReadinessStatus,
    ReadinessType,
    ResolutionState,
    SteeringRole,
    VerificationState,
)
from app.domain.readiness import evaluate_readiness
from app.domain.schemas import (
    EvidenceLinkCreate,
    GeometryAssetCreate,
    LoadConditionCreate,
    NormalizedValueCreate,
    ParameterAssessmentCreate,
    SourceObservationCreate,
    SteeringRelationCreate,
)
from app.domain.validation import ContractViolation
from app.services.foundation import (
    create_fitment,
    create_geometry_asset,
    create_load_condition,
    create_normalized_value,
    create_parameter_assessment,
    create_source_observation,
    create_steering_relation,
)


FIXTURE_TIME = datetime(2026, 8, 31, tzinfo=timezone.utc)


def config(session, code: str) -> VehicleConfiguration:
    return session.scalar(select(VehicleConfiguration).where(VehicleConfiguration.stable_vehicle_code == code))


def value_for(session, vehicle: VehicleConfiguration, parameter_code: str) -> NormalizedValue:
    return session.scalar(
        select(NormalizedValue)
        .join(ParameterDefinition)
        .where(
            NormalizedValue.vehicle_configuration_id == vehicle.id,
            ParameterDefinition.parameter_code == parameter_code,
        )
    )


def source_observation_for(session, vehicle: VehicleConfiguration) -> SourceObservation:
    return session.scalar(select(SourceObservation).where(SourceObservation.vehicle_configuration_id == vehicle.id))


def direct_track_payload(*, resolution: ResolutionState = ResolutionState.CONFLICTING, preferred: bool = False) -> NormalizedValueCreate:
    return NormalizedValueCreate(
        parameter_code="avt_front_outer_face_track_mm",
        numeric_value=1815,
        canonical_unit="mm",
        evidence_method=EvidenceMethod.PUBLISHED,
        resolution_state=resolution,
        verification_state=VerificationState.REVIEWED,
        availability_state=AvailabilityState.AVAILABLE,
        semantic_metadata={
            "track_definition": "OUTER_TYRE_FACES",
            "source_basis": "DIRECT_OUTER_FACE_EVIDENCE",
            "screening_only": False,
        },
        preferred=preferred,
    )


def make_conflicting_direct_tracks(session, *, preferred: bool) -> tuple[VehicleConfiguration, NormalizedValue, NormalizedValue]:
    vehicle = config(session, "FIXTURE-AVT-TRACK-DIRECT")
    original = value_for(session, vehicle, "avt_front_outer_face_track_mm")
    original.resolution_state = ResolutionState.CONFLICTING.value
    original.preferred = preferred
    observation = source_observation_for(session, vehicle)
    second = create_normalized_value(
        session,
        vehicle,
        direct_track_payload(preferred=not preferred),
        evidence_links=[EvidenceLinkCreate(source_observation_id=observation.id)],
    )
    return vehicle, original, second


def avt_evaluation(session, vehicle: VehicleConfiguration):
    return next(item for item in evaluate_readiness(session, vehicle) if item.readiness_type == ReadinessType.AVT_READY)


@pytest.mark.parametrize(
    "metadata",
    [
        {"turning_radius_or_diameter": "RADIUS", "turning_axle_scope": "ALL_AXLES"},
        {"turning_radius_or_diameter": "RADIUS", "turning_reference": "CURB_TO_CURB"},
        {
            "turning_radius_or_diameter": "RADIUS",
            "turning_reference": "WALL_TO_WALL",
            "turning_axle_scope": "ALL_AXLES",
        },
    ],
    ids=["missing-reference", "missing-axle-scope", "missing-wall-envelope-scope"],
)
def test_turning_semantic_requirements_are_enforced_at_persistence_boundary(session, metadata):
    vehicle = config(session, "FIXTURE-AVT-TRACK-DIRECT")
    observation = source_observation_for(session, vehicle)
    payload = NormalizedValueCreate(
        parameter_code="turning_radius_normalized_m",
        numeric_value=5.4,
        canonical_unit="m",
        evidence_method=EvidenceMethod.PUBLISHED,
        semantic_metadata=metadata,
    )
    with pytest.raises(ContractViolation):
        create_normalized_value(
            session,
            vehicle,
            payload,
            evidence_links=[EvidenceLinkCreate(source_observation_id=observation.id)],
        )


def test_clearance_type_and_load_condition_requirements_are_enforced(session):
    vehicle = config(session, "FIXTURE-CLEARANCE-LOADS")
    observation = source_observation_for(session, vehicle)
    load_condition = vehicle.load_conditions[0]
    missing_type = NormalizedValueCreate(
        parameter_code="clearance_value_mm",
        numeric_value=135,
        canonical_unit="mm",
        load_condition_id=load_condition.id,
        evidence_method=EvidenceMethod.PUBLISHED,
    )
    with pytest.raises(ContractViolation):
        create_normalized_value(
            session,
            vehicle,
            missing_type,
            evidence_links=[EvidenceLinkCreate(source_observation_id=observation.id)],
        )

    missing_load = NormalizedValueCreate(
        parameter_code="clearance_value_mm",
        numeric_value=135,
        canonical_unit="mm",
        evidence_method=EvidenceMethod.PUBLISHED,
        semantic_metadata={"clearance_type": "BETWEEN_AXLES"},
    )
    with pytest.raises(ContractViolation):
        create_normalized_value(
            session,
            vehicle,
            missing_load,
            evidence_links=[EvidenceLinkCreate(source_observation_id=observation.id)],
        )


def test_available_none_is_rejected_by_the_domain_contract():
    with pytest.raises(ValidationError):
        NormalizedValueCreate(
            parameter_code="overall_length_mm",
            numeric_value=4500,
            evidence_method=EvidenceMethod.NONE,
        )


@pytest.mark.parametrize("method", [EvidenceMethod.PUBLISHED, EvidenceMethod.MEASURED])
def test_published_and_measured_values_require_source_observation_links(session, method):
    vehicle = config(session, "FIXTURE-PRIMARY-PUBLISHED")
    payload = NormalizedValueCreate(
        parameter_code="overall_length_mm",
        numeric_value=4500,
        canonical_unit="mm",
        evidence_method=method,
    )
    with pytest.raises(ContractViolation):
        create_normalized_value(session, vehicle, payload)


def test_estimated_value_requires_source_or_controlled_derivation_lineage(session):
    vehicle = config(session, "FIXTURE-SCALED-ESTIMATE")
    payload = NormalizedValueCreate(
        parameter_code="front_overhang_mm",
        numeric_value=760,
        canonical_unit="mm",
        evidence_method=EvidenceMethod.ESTIMATED,
        semantic_metadata={"estimation_method": "UNSUPPORTED_ESTIMATE", "limitations": "No evidence."},
    )
    with pytest.raises(ContractViolation):
        create_normalized_value(session, vehicle, payload)


def test_existing_estimates_retain_defensible_provenance(session):
    scaled = value_for(session, config(session, "FIXTURE-SCALED-ESTIMATE"), "front_overhang_mm")
    assert scaled.evidence_method == EvidenceMethod.ESTIMATED.value
    assert scaled.evidence_links
    screening = value_for(session, config(session, "FIXTURE-AVT-TRACK-SCREENING"), "avt_front_outer_face_track_mm")
    assert screening.evidence_method == EvidenceMethod.ESTIMATED.value
    assert screening.derivation_run is not None
    assert screening.derivation_run.inputs
    assert screening.semantic_metadata["limitations"]


def test_two_conflicting_direct_avt_tracks_without_decision_are_not_ready(session):
    vehicle, _, _ = make_conflicting_direct_tracks(session, preferred=False)
    evaluation = avt_evaluation(session, vehicle)
    assert evaluation.status == ReadinessStatus.NOT_READY
    assert any("avt_front_outer_face_track_mm" in reason for reason in evaluation.blocking_reasons)


def test_preferred_conflicting_track_without_decision_is_still_not_ready(session):
    vehicle, _, _ = make_conflicting_direct_tracks(session, preferred=True)
    evaluation = avt_evaluation(session, vehicle)
    assert evaluation.status == ReadinessStatus.NOT_READY
    mapping = build_avt_mapping(session, vehicle)
    assert mapping["status"] != "READY"


def test_auditable_conflict_decision_selects_the_exact_candidate(session):
    vehicle, _, selected = make_conflicting_direct_tracks(session, preferred=False)
    parameter = session.scalar(
        select(ParameterDefinition).where(ParameterDefinition.parameter_code == "avt_front_outer_face_track_mm")
    )
    session.add(
        ConflictDecision(
            vehicle_configuration_id=vehicle.id,
            parameter_definition_id=parameter.id,
            selected_normalized_value_id=selected.id,
            decision_state=DecisionState.SELECTED.value,
            rationale="Deterministic test decision selects the exact direct track candidate.",
            decided_at=FIXTURE_TIME,
            reviewer="remediation-test",
        )
    )
    session.flush()
    evaluation = avt_evaluation(session, vehicle)
    assert evaluation.status == ReadinessStatus.READY
    assert selected.id in evaluation.supporting_value_ids
    mapping = build_avt_mapping(session, vehicle)
    assert mapping["status"] == "READY"
    assert selected.id in mapping["source_value_ids"]


def test_wrong_parameter_or_configuration_selection_fails_closed(session):
    vehicle, original, _ = make_conflicting_direct_tracks(session, preferred=True)
    wrong_parameter = session.scalar(
        select(ParameterDefinition).where(ParameterDefinition.parameter_code == "avt_rear_outer_face_track_mm")
    )
    wrong_configuration_value = value_for(
        session,
        config(session, "FIXTURE-AVT-TRACK-SCREENING"),
        "avt_front_outer_face_track_mm",
    )
    correct_parameter = session.scalar(
        select(ParameterDefinition).where(ParameterDefinition.parameter_code == "avt_front_outer_face_track_mm")
    )
    session.add_all(
        [
            ConflictDecision(
                vehicle_configuration_id=vehicle.id,
                parameter_definition_id=wrong_parameter.id,
                selected_normalized_value_id=original.id,
                decision_state=DecisionState.SELECTED.value,
                rationale="Wrong parameter scope test.",
                decided_at=FIXTURE_TIME,
            ),
            ConflictDecision(
                vehicle_configuration_id=vehicle.id,
                parameter_definition_id=correct_parameter.id,
                selected_normalized_value_id=wrong_configuration_value.id,
                decision_state=DecisionState.SELECTED.value,
                rationale="Wrong configuration scope test.",
                decided_at=FIXTURE_TIME,
            ),
        ]
    )
    session.flush()
    assert avt_evaluation(session, vehicle).status == ReadinessStatus.NOT_READY


def test_rejected_candidate_cannot_satisfy_avt_readiness(session):
    vehicle = config(session, "FIXTURE-AVT-TRACK-DIRECT")
    front = value_for(session, vehicle, "avt_front_outer_face_track_mm")
    front.verification_state = VerificationState.REJECTED.value
    assert avt_evaluation(session, vehicle).status == ReadinessStatus.NOT_READY


def test_fitment_specific_derivations_preserve_scope_and_reject_mixing(session):
    vehicle = config(session, "FIXTURE-PRIMARY-PUBLISHED")
    fitment_a = create_fitment(session, vehicle, "FITMENT-A", wheel_package="235/50 R18")
    fitment_b = create_fitment(session, vehicle, "FITMENT-B", wheel_package="245/45 R19")
    observation = source_observation_for(session, vehicle)

    tyre_size = create_normalized_value(
        session,
        vehicle,
        NormalizedValueCreate(
            parameter_code="front_tyre_size_text",
            text_value="235/50 R18",
            evidence_method=EvidenceMethod.PUBLISHED,
            availability_state=AvailabilityState.AVAILABLE,
        ),
        fitment=fitment_a,
        evidence_links=[EvidenceLinkCreate(source_observation_id=observation.id)],
    )
    derived_radius = derive_nominal_tyre_radius(
        session,
        vehicle,
        tyre_size_value=tyre_size,
        output_parameter_code="nominal_unloaded_tyre_radius_front_mm",
    )
    assert derived_radius.vehicle_fitment_id == fitment_a.id
    assert not session.scalar(
        select(NormalizedValue).where(
            NormalizedValue.vehicle_configuration_id == vehicle.id,
            NormalizedValue.parameter_definition_id
            == session.scalar(
                select(ParameterDefinition.id).where(
                    ParameterDefinition.parameter_code == "nominal_unloaded_tyre_radius_front_mm"
                )
            ),
            NormalizedValue.vehicle_fitment_id == fitment_b.id,
        )
    )

    centerline_a = create_normalized_value(
        session,
        vehicle,
        NormalizedValueCreate(
            parameter_code="oem_front_tread_or_track_mm",
            numeric_value=1575,
            canonical_unit="mm",
            evidence_method=EvidenceMethod.PUBLISHED,
            semantic_metadata={"track_definition": "TYRE_CENTERLINE"},
        ),
        fitment=fitment_a,
        evidence_links=[EvidenceLinkCreate(source_observation_id=observation.id)],
    )
    nominal_width_b = create_normalized_value(
        session,
        vehicle,
        NormalizedValueCreate(
            parameter_code="front_nominal_section_width_mm",
            numeric_value=245,
            canonical_unit="mm",
            evidence_method=EvidenceMethod.PUBLISHED,
        ),
        fitment=fitment_b,
        evidence_links=[EvidenceLinkCreate(source_observation_id=observation.id)],
    )
    with pytest.raises(ContractViolation):
        derive_avt_track_estimate(
            session,
            vehicle,
            centerline_value=centerline_a,
            nominal_section_width_value=nominal_width_b,
            output_parameter_code="avt_front_outer_face_track_mm",
        )


@pytest.mark.parametrize(
    "parameter_code",
    [
        "static_loaded_tyre_radius_front_mm",
        "static_loaded_tyre_radius_rear_mm",
    ],
)
def test_static_loaded_tyre_radius_requires_load_condition(session, parameter_code):
    vehicle = config(session, "FIXTURE-STATIC-LOADED-RADIUS")
    observation = source_observation_for(session, vehicle)
    payload = NormalizedValueCreate(
        parameter_code=parameter_code,
        numeric_value=321,
        canonical_unit="mm",
        evidence_method=EvidenceMethod.MEASURED,
        semantic_metadata={"radius_kind": "STATIC_LOADED"},
    )
    with pytest.raises(ContractViolation):
        create_normalized_value(
            session,
            vehicle,
            payload,
            evidence_links=[EvidenceLinkCreate(source_observation_id=observation.id)],
        )


def test_static_loaded_tyre_radius_rejects_foreign_load_condition(session):
    vehicle = config(session, "FIXTURE-STATIC-LOADED-RADIUS")
    foreign_vehicle = config(session, "FIXTURE-CLEARANCE-LOADS")
    observation = source_observation_for(session, vehicle)
    payload = NormalizedValueCreate(
        parameter_code="static_loaded_tyre_radius_front_mm",
        numeric_value=321,
        canonical_unit="mm",
        load_condition_id=foreign_vehicle.load_conditions[0].id,
        evidence_method=EvidenceMethod.MEASURED,
        semantic_metadata={"radius_kind": "STATIC_LOADED"},
    )
    with pytest.raises(ContractViolation):
        create_normalized_value(
            session,
            vehicle,
            payload,
            evidence_links=[EvidenceLinkCreate(source_observation_id=observation.id)],
        )


def test_static_loaded_tyre_radius_does_not_require_published_tyre_pressure(session):
    vehicle = config(session, "FIXTURE-STATIC-LOADED-RADIUS")
    observation = source_observation_for(session, vehicle)
    load = create_load_condition(
        session,
        vehicle,
        LoadConditionCreate(name="Unknown-pressure measured condition", mass_basis=MassBasis.KERB),
    )
    value = create_normalized_value(
        session,
        vehicle,
        NormalizedValueCreate(
            parameter_code="static_loaded_tyre_radius_front_mm",
            numeric_value=321,
            canonical_unit="mm",
            load_condition_id=load.id,
            evidence_method=EvidenceMethod.MEASURED,
            semantic_metadata={"radius_kind": "STATIC_LOADED"},
        ),
        evidence_links=[EvidenceLinkCreate(source_observation_id=observation.id)],
    )
    assert value.load_condition_id == load.id
    assert load.front_tyre_pressure is None
    assert load.rear_tyre_pressure is None


def test_cross_configuration_evidence_is_rejected(session):
    vehicle = config(session, "FIXTURE-PRIMARY-PUBLISHED")
    foreign_observation = source_observation_for(session, config(session, "FIXTURE-AVT-TRACK-SCREENING"))
    payload = NormalizedValueCreate(
        parameter_code="overall_length_mm",
        numeric_value=4500,
        canonical_unit="mm",
        evidence_method=EvidenceMethod.PUBLISHED,
    )
    with pytest.raises(ContractViolation):
        create_normalized_value(
            session,
            vehicle,
            payload,
            evidence_links=[EvidenceLinkCreate(source_observation_id=foreign_observation.id)],
        )


def test_unresolved_evidence_cannot_qualify_an_exact_configuration_value(session):
    vehicle = config(session, "FIXTURE-PRIMARY-PUBLISHED")
    existing_observation = source_observation_for(session, vehicle)

    unresolved = create_source_observation(
        session,
        None,
        SourceObservationCreate(
            vehicle_identity_claim="unresolved fixture identity",
            source_document_id=existing_observation.source_document_id,
            raw_label="Overall length",
            raw_value="4500",
            raw_unit="mm",
            extracted_at=FIXTURE_TIME,
        ),
    )
    with pytest.raises(ContractViolation):
        create_normalized_value(
            session,
            vehicle,
            NormalizedValueCreate(
                parameter_code="overall_length_mm",
                numeric_value=4500,
                canonical_unit="mm",
                evidence_method=EvidenceMethod.PUBLISHED,
            ),
            evidence_links=[EvidenceLinkCreate(source_observation_id=unresolved.id)],
        )


def test_steering_relation_rejects_axle_from_another_configuration(session):
    vehicle = config(session, "FIXTURE-REAR-STEERING")
    foreign_axle = config(session, "FIXTURE-AVT-TRACK-DIRECT").axles[0]
    with pytest.raises(ContractViolation):
        create_steering_relation(
            session,
            vehicle,
            SteeringRelationCreate(
                axle_id=foreign_axle.id,
                steering_role=SteeringRole.PRIMARY,
                linkage_type=LinkageType.FIXED_RATIO,
                phase_behavior=PhaseBehavior.SAME_PHASE,
            ),
        )


def test_steering_relation_rejects_foreign_source_observation(session):
    vehicle = config(session, "FIXTURE-REAR-STEERING")
    axle = vehicle.axles[0]
    foreign_observation = source_observation_for(session, config(session, "FIXTURE-AVT-TRACK-SCREENING"))
    with pytest.raises(ContractViolation):
        create_steering_relation(
            session,
            vehicle,
            SteeringRelationCreate(
                axle_id=axle.id,
                steering_role=SteeringRole.PRIMARY,
                linkage_type=LinkageType.FIXED_RATIO,
                phase_behavior=PhaseBehavior.SAME_PHASE,
                source_observation_id=foreign_observation.id,
            ),
        )


def _geometry_payload(**overrides) -> GeometryAssetCreate:
    data = {
        "geometry_role": GeometryRole.SIDE_SILHOUETTE,
        "representation_type": "POLYLINE",
        "geometry_data": {"points": [[0, 0], [1, 1]]},
        "unit": "mm",
        "coordinate_system_version": "vehicle-fixed-v1",
        "geometry_method": GeometryMethod.SCALED_DRAWING,
        "geometry_fidelity": GeometryFidelity.LOW,
    }
    data.update(overrides)
    return GeometryAssetCreate(**data)


def test_geometry_asset_rejects_foreign_fitment_and_load_condition(session):
    vehicle = config(session, "FIXTURE-PRIMARY-PUBLISHED")
    foreign_vehicle = config(session, "FIXTURE-CLEARANCE-LOADS")
    foreign_fitment = create_fitment(session, foreign_vehicle, "FOREIGN-FITMENT")
    with pytest.raises(ContractViolation):
        create_geometry_asset(session, vehicle, _geometry_payload(), fitment=foreign_fitment)

    with pytest.raises(ContractViolation):
        create_geometry_asset(
            session,
            vehicle,
            _geometry_payload(load_condition_id=foreign_vehicle.load_conditions[0].id),
        )


def test_geometry_asset_rejects_foreign_derivation_run(session):
    vehicle = config(session, "FIXTURE-PRIMARY-PUBLISHED")
    foreign_value = value_for(
        session,
        config(session, "FIXTURE-AVT-TRACK-SCREENING"),
        "avt_front_outer_face_track_mm",
    )
    assert foreign_value.derivation_run is not None
    with pytest.raises(ContractViolation):
        create_geometry_asset(
            session,
            vehicle,
            _geometry_payload(derivation_run_id=foreign_value.derivation_run.id),
        )


def test_parameter_assessment_rejects_foreign_fitment(session):
    vehicle = config(session, "FIXTURE-PRIMARY-PUBLISHED")
    foreign_fitment = create_fitment(session, config(session, "FIXTURE-AVT-TRACK-SCREENING"), "FOREIGN-FITMENT")
    payload = ParameterAssessmentCreate(
        parameter_code="overall_length_mm",
        availability_state=AvailabilityState.UNKNOWN,
        unknown_reason="Scope test",
        assessed_at=FIXTURE_TIME,
    )
    with pytest.raises(ContractViolation):
        create_parameter_assessment(session, vehicle, payload, fitment=foreign_fitment)


def test_readiness_and_avt_mapping_reject_foreign_fitment_scope(session):
    vehicle = config(session, "FIXTURE-AVT-TRACK-DIRECT")
    foreign_fitment = create_fitment(session, config(session, "FIXTURE-AVT-TRACK-SCREENING"), "FOREIGN-FITMENT")
    with pytest.raises(ContractViolation):
        evaluate_readiness(session, vehicle, fitment=foreign_fitment)
    with pytest.raises(ContractViolation):
        build_avt_mapping(session, vehicle, fitment=foreign_fitment)


@pytest.mark.parametrize(
    "parameter_code",
    [
        "geometry_derived_approach_angle_deg",
        "geometry_derived_departure_angle_deg",
        "geometry_derived_breakover_angle_deg",
    ],
)
def test_phase0_rejects_arbitrary_derived_physical_ramp_angles(session, parameter_code):
    vehicle = config(session, "FIXTURE-PRIMARY-PUBLISHED")
    input_value = value_for(session, vehicle, "wheelbase_actual_mm")
    rule = register_derivation_rule(
        session,
        rule_code=f"arbitrary-physical-ramp-{parameter_code}",
        version="1",
        name="Invalid arbitrary physical ramp derivation",
        output_parameter_code=parameter_code,
        formula_description="not a physical ramp solver",
        validity_conditions="invalid Phase 0 test rule",
        uncertainty_method="invalid Phase 0 test rule",
        reference_basis="test",
        input_parameter_codes=["wheelbase_actual_mm"],
    )
    with pytest.raises(ContractViolation):
        create_normalized_value(
            session,
            vehicle,
            NormalizedValueCreate(
                parameter_code=parameter_code,
                numeric_value=12,
                canonical_unit="deg",
                evidence_method=EvidenceMethod.DERIVED,
                normalization_rule_version=f"{rule.rule_code}:{rule.version}",
                semantic_metadata={"ramp_result_class": "PHYSICAL"},
            ),
            derivation_rule=rule,
            derivation_inputs=[(input_value, "test_input")],
        )


@pytest.mark.parametrize(
    "parameter_code",
    ["oem_published_approach_angle_deg", "geometry_derived_breakover_angle_deg"],
)
def test_screening_result_cannot_populate_oem_or_physical_ramp_namespace(session, parameter_code):
    vehicle = config(session, "FIXTURE-PRIMARY-PUBLISHED")
    input_value = value_for(session, vehicle, "wheelbase_actual_mm")
    rule = register_derivation_rule(
        session,
        rule_code=f"ramp_screening-invalid-{parameter_code}",
        version="1",
        name="Invalid screening namespace promotion",
        output_parameter_code=parameter_code,
        formula_description="screening test rule",
        validity_conditions="screening test only",
        uncertainty_method="screening test only",
        reference_basis="test",
        input_parameter_codes=["wheelbase_actual_mm"],
    )
    with pytest.raises(ContractViolation):
        create_normalized_value(
            session,
            vehicle,
            NormalizedValueCreate(
                parameter_code=parameter_code,
                numeric_value=12,
                canonical_unit="deg",
                evidence_method=EvidenceMethod.DERIVED,
                normalization_rule_version=f"{rule.rule_code}:{rule.version}",
                semantic_metadata={"ramp_result_class": "SCREENING"},
            ),
            derivation_rule=rule,
            derivation_inputs=[(input_value, "test_input")],
        )


def test_existing_screening_derivation_and_oem_published_ramp_value_remain_valid(session):
    screening = value_for(
        session,
        config(session, "FIXTURE-RAMP-SCREENING"),
        "screening_breakover_symmetric_angle_deg",
    )
    assert screening.derivation_run is not None
    assert screening.semantic_metadata["ramp_result_class"] == "SCREENING"

    vehicle = config(session, "FIXTURE-PRIMARY-PUBLISHED")
    observation = source_observation_for(session, vehicle)
    value = create_normalized_value(
        session,
        vehicle,
        NormalizedValueCreate(
            parameter_code="oem_published_breakover_angle_deg",
            numeric_value=12,
            canonical_unit="deg",
            evidence_method=EvidenceMethod.PUBLISHED,
            semantic_metadata={"ramp_result_class": "OEM_PUBLISHED"},
        ),
        evidence_links=[EvidenceLinkCreate(source_observation_id=observation.id)],
    )
    assert value.numeric_value == 12
