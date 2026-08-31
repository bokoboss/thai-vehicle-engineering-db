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
from app.domain.derivations import derive_avt_track_estimate, derive_nominal_tyre_radius
from app.domain.enums import (
    AvailabilityState,
    DecisionState,
    EvidenceMethod,
    ReadinessStatus,
    ReadinessType,
    ResolutionState,
    VerificationState,
)
from app.domain.readiness import evaluate_readiness
from app.domain.schemas import EvidenceLinkCreate, NormalizedValueCreate
from app.domain.validation import ContractViolation
from app.services.foundation import create_fitment, create_normalized_value


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
