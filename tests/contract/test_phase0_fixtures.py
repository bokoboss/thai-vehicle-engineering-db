from __future__ import annotations

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from app.db.models import (
    Axle,
    ConflictDecision,
    DerivationInput,
    DerivationRun,
    GeometryAsset,
    LoadCondition,
    NormalizedValue,
    ParameterAssessment,
    ParameterDefinition,
    ReadinessResult,
    SourceObservation,
    SteeringRelation,
    VehicleConfiguration,
)
from app.domain.enums import AvailabilityState, EvidenceMethod, VerificationState
from app.domain.schemas import NormalizedValueCreate
from app.domain.validation import ContractViolation, normalize_turning_radius, validate_width_promotion
from app.seed.registry import FORBIDDEN_AMBIGUOUS_CODES, load_registry


def config(session, code: str) -> VehicleConfiguration:
    return session.scalar(select(VehicleConfiguration).where(VehicleConfiguration.stable_vehicle_code == code))


def values_for(session, code: str, parameter_code: str) -> list[NormalizedValue]:
    vehicle = config(session, code)
    return list(
        session.scalars(
            select(NormalizedValue)
            .join(ParameterDefinition)
            .where(
                NormalizedValue.vehicle_configuration_id == vehicle.id,
                ParameterDefinition.parameter_code == parameter_code,
            )
        ).all()
    )


def readiness(session, code: str, readiness_type: str) -> ReadinessResult:
    vehicle = config(session, code)
    return session.scalar(
        select(ReadinessResult).where(
            ReadinessResult.vehicle_configuration_id == vehicle.id,
            ReadinessResult.readiness_type == readiness_type,
            ReadinessResult.vehicle_fitment_id.is_(None),
        )
    )


def test_all_required_phase0_fixture_records_are_seeded(session):
    required_codes = {
        "FIXTURE-PRIMARY-PUBLISHED",
        "FIXTURE-TURNING-UNSPECIFIED",
        "FIXTURE-CONFLICTING-VALUE",
        "FIXTURE-AVT-TRACK-SCREENING",
        "FIXTURE-AVT-TRACK-DIRECT",
        "FIXTURE-UNKNOWN-ASSESSMENT",
        "FIXTURE-SCALED-ESTIMATE",
        "FIXTURE-STEERING-SEPARATION",
        "FIXTURE-CURB-UNKNOWN-AXLE",
        "FIXTURE-WALL-SCOPES",
        "FIXTURE-CLEARANCE-LOADS",
        "FIXTURE-STATIC-LOADED-RADIUS",
        "FIXTURE-REAR-STEERING",
        "FIXTURE-WIDTH-UNSPECIFIED",
        "FIXTURE-GEOMETRY-ROLES",
        "FIXTURE-RAMP-SCREENING",
    }
    actual_codes = {row.stable_vehicle_code for row in session.scalars(select(VehicleConfiguration)).all()}
    assert required_codes <= actual_codes


def test_registry_is_machine_seeded_and_forbidden_codes_are_rejected():
    registry = load_registry()
    codes = {entry.code for entry in registry.parameters}
    assert len(codes) == len(registry.parameters)
    assert not codes & FORBIDDEN_AMBIGUOUS_CODES
    assert "avt_front_outer_face_track_mm" in codes
    assert "screening_breakover_symmetric_angle_deg" in codes


def test_orthogonal_published_conflicting_reviewed_available_state_is_preserved(session):
    candidates = values_for(session, "FIXTURE-CONFLICTING-VALUE", "overall_length_mm")
    assert len(candidates) == 2
    reviewed = next(value for value in candidates if value.verification_state == VerificationState.REVIEWED.value)
    assert reviewed.evidence_method == EvidenceMethod.PUBLISHED.value
    assert reviewed.resolution_state == "CONFLICTING"
    assert reviewed.availability_state == AvailabilityState.AVAILABLE.value
    assert reviewed.preferred is True
    decision = session.scalar(select(ConflictDecision).where(ConflictDecision.vehicle_configuration_id == reviewed.vehicle_configuration_id))
    assert decision.selected_normalized_value_id == reviewed.id
    assert len({value.numeric_value for value in candidates}) == 2


def test_unknown_assessment_has_no_fake_numeric_value(session):
    vehicle = config(session, "FIXTURE-UNKNOWN-ASSESSMENT")
    assessment = session.scalar(
        select(ParameterAssessment)
        .join(ParameterDefinition)
        .where(
            ParameterAssessment.vehicle_configuration_id == vehicle.id,
            ParameterDefinition.parameter_code == "maximum_inner_road_wheel_angle_deg",
        )
    )
    assert assessment.availability_state == AvailabilityState.NOT_FOUND_AFTER_SEARCH.value
    assert session.scalars(
        select(NormalizedValue)
        .join(ParameterDefinition)
        .where(
            NormalizedValue.vehicle_configuration_id == vehicle.id,
            ParameterDefinition.parameter_code == "maximum_inner_road_wheel_angle_deg",
        )
    ).first() is None
    with pytest.raises(ValidationError):
        NormalizedValueCreate(
            parameter_code="maximum_inner_road_wheel_angle_deg",
            numeric_value=0,
            availability_state=AvailabilityState.UNKNOWN,
        )


def test_generic_width_stays_reported_and_body_promotion_fails_closed(session):
    reported = values_for(session, "FIXTURE-WIDTH-UNSPECIFIED", "overall_width_reported_mm")
    assert len(reported) == 1
    assert reported[0].semantic_metadata["width_envelope_definition"] == "OEM_UNSPECIFIED"
    assert not values_for(session, "FIXTURE-WIDTH-UNSPECIFIED", "overall_width_body_mm")
    with pytest.raises(ContractViolation):
        validate_width_promotion("overall_width_body_mm", {"width_envelope_definition": "OEM_UNSPECIFIED"})


def test_turning_radius_diameter_conversion_requires_explicit_semantics(session):
    turning = values_for(session, "FIXTURE-TURNING-UNSPECIFIED", "turning_radius_normalized_m")[0]
    assert turning.semantic_metadata["turning_reference"] == "OEM_UNSPECIFIED"
    assert readiness(session, "FIXTURE-TURNING-UNSPECIFIED", "AVT_READY").status == "NOT_READY"
    assert normalize_turning_radius(10.8, "DIAMETER") == pytest.approx(5.4)
    with pytest.raises(ContractViolation):
        normalize_turning_radius(5.4, "OEM_UNSPECIFIED")


def test_nominal_width_avt_track_estimate_is_retained_but_rejected_for_avt_ready(session):
    values = values_for(session, "FIXTURE-AVT-TRACK-SCREENING", "avt_front_outer_face_track_mm")
    assert len(values) == 1
    candidate = values[0]
    assert candidate.evidence_method == EvidenceMethod.ESTIMATED.value
    assert candidate.semantic_metadata["source_basis"] == "CENTERLINE_PLUS_NOMINAL_WIDTH"
    assert candidate.semantic_metadata["screening_only"] is True
    assert candidate.derivation_run is not None
    assert session.scalar(select(DerivationInput).where(DerivationInput.derivation_run_id == candidate.derivation_run.id)) is not None
    avt = readiness(session, "FIXTURE-AVT-TRACK-SCREENING", "AVT_READY")
    assert avt.status == "NOT_READY"
    assert any("screening-only" in reason for reason in avt.blocking_reasons)


def test_direct_outer_face_track_can_be_avt_ready_when_other_required_semantics_exist(session):
    front = values_for(session, "FIXTURE-AVT-TRACK-DIRECT", "avt_front_outer_face_track_mm")[0]
    assert front.semantic_metadata["track_definition"] == "OUTER_TYRE_FACES"
    assert front.semantic_metadata["source_basis"] == "DIRECT_OUTER_FACE_EVIDENCE"
    assert readiness(session, "FIXTURE-AVT-TRACK-DIRECT", "AVT_READY").status == "READY"


def test_scaled_estimate_keeps_uncertainty_and_raw_evidence(session):
    value = values_for(session, "FIXTURE-SCALED-ESTIMATE", "front_overhang_mm")[0]
    assert value.evidence_method == EvidenceMethod.ESTIMATED.value
    assert float(value.uncertainty_value) == 15
    assert len(value.evidence_links) == 1
    observation = value.evidence_links[0].source_observation
    assert observation.extraction_method == "IMAGE_SCALE"
    assert observation.raw_value == "760"


def test_steering_wheel_turns_do_not_become_wheel_angle_or_avt_time(session):
    turns = values_for(session, "FIXTURE-STEERING-SEPARATION", "steering_wheel_lock_to_lock_turns")[0]
    actual = values_for(session, "FIXTURE-STEERING-SEPARATION", "maximum_inner_road_wheel_angle_deg")[0]
    assert turns.numeric_value != actual.numeric_value
    assert not values_for(session, "FIXTURE-STEERING-SEPARATION", "avt_lock_to_lock_time_forward_s")
    assert len(session.scalars(select(ParameterAssessment).where(ParameterAssessment.vehicle_configuration_id == turns.vehicle_configuration_id)).all()) == 2


def test_curb_axle_scope_and_wall_envelope_scope_are_preserved(session):
    curb = values_for(session, "FIXTURE-CURB-UNKNOWN-AXLE", "turning_radius_normalized_m")[0]
    assert curb.semantic_metadata["turning_reference"] == "CURB_TO_CURB"
    assert curb.semantic_metadata["turning_axle_scope"] == "OEM_UNSPECIFIED"
    assert readiness(session, "FIXTURE-CURB-UNKNOWN-AXLE", "AVT_READY").status == "NOT_READY"
    wall = values_for(session, "FIXTURE-WALL-SCOPES", "turning_radius_normalized_m")
    assert {item.semantic_metadata["turning_wall_envelope_scope"] for item in wall} == {"BODY_ONLY", "BODY_AND_LOADS"}


def test_clearance_load_condition_and_static_loaded_radius_are_distinct(session):
    clearances = values_for(session, "FIXTURE-CLEARANCE-LOADS", "clearance_value_mm")
    assert {item.semantic_metadata["clearance_type"] for item in clearances} == {"BETWEEN_AXLES", "FRONT_AXLE"}
    assert len({item.load_condition_id for item in clearances}) == 2
    conditions = session.scalars(select(LoadCondition).where(LoadCondition.vehicle_configuration_id == config(session, "FIXTURE-CLEARANCE-LOADS").id)).all()
    laden = next(item for item in conditions if item.mass_basis == "OEM_LADEN")
    assert laden.front_tyre_pressure == 2.4
    assert laden.ride_height_mode == "laden static"
    loaded = values_for(session, "FIXTURE-STATIC-LOADED-RADIUS", "static_loaded_tyre_radius_front_mm")[0]
    assert loaded.load_condition_id is not None
    assert loaded.semantic_metadata["radius_kind"] == "STATIC_LOADED"
    assert loaded.evidence_method == EvidenceMethod.MEASURED.value


def test_four_wheel_steering_has_structural_rear_relation(session):
    vehicle = config(session, "FIXTURE-REAR-STEERING")
    rear = session.scalar(select(Axle).where(Axle.vehicle_configuration_id == vehicle.id, Axle.axle_role == "REAR"))
    relation = session.scalar(select(SteeringRelation).where(SteeringRelation.axle_id == rear.id))
    assert rear.steered is True
    assert relation.steering_role == "SECONDARY"
    assert relation.linkage_type == "MODE_DEPENDENT"
    assert relation.phase_behavior == "MODE_OR_SPEED_DEPENDENT"
    assert relation.relation_function


def test_geometry_roles_and_ramp_screening_namespace_remain_separate(session):
    vehicle = config(session, "FIXTURE-GEOMETRY-ROLES")
    roles = {item.geometry_role for item in session.scalars(select(GeometryAsset).where(GeometryAsset.vehicle_configuration_id == vehicle.id)).all()}
    assert roles == {"SIDE_SILHOUETTE", "LONGITUDINAL_LOWER_ENVELOPE"}
    ramp_values = values_for(session, "FIXTURE-RAMP-SCREENING", "screening_breakover_symmetric_angle_deg")
    assert len(ramp_values) == 1
    ramp = ramp_values[0]
    assert ramp.derivation_run is not None
    assert ramp.semantic_metadata["ramp_result_class"] == "SCREENING"
    assert not values_for(session, "FIXTURE-RAMP-SCREENING", "oem_published_breakover_angle_deg")
    assert not values_for(session, "FIXTURE-RAMP-SCREENING", "geometry_derived_breakover_angle_deg")
    assert readiness(session, "FIXTURE-RAMP-SCREENING", "RAMP_SCREENING_READY").status == "READY"


def test_raw_observations_and_normalized_values_are_separate_and_queryable(session):
    vehicle = config(session, "FIXTURE-PRIMARY-PUBLISHED")
    observation = session.scalar(select(SourceObservation).where(SourceObservation.vehicle_configuration_id == vehicle.id))
    value = values_for(session, "FIXTURE-PRIMARY-PUBLISHED", "wheelbase_actual_mm")[0]
    assert observation.raw_label == "Wheelbase"
    assert observation.raw_value == "2700"
    assert value.numeric_value == 2700
    assert observation.id != value.id
