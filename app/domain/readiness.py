from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    Axle,
    GeometryAsset,
    NormalizedValue,
    ReadinessResult,
    SteeringRelation,
    VehicleConfiguration,
    VehicleFitment,
)
from app.domain.enums import (
    AvailabilityState,
    EvidenceMethod,
    GeometryRole,
    ReadinessStatus,
    ReadinessType,
    ResolutionState,
    VerificationState,
)
from app.domain.validation import (
    is_avt_track_ready,
    is_turning_avt_ready,
    rear_steering_mapping_ready,
)


READINESS_RULE_VERSION = "phase-0-readiness-v1"


@dataclass(frozen=True)
class ReadinessEvaluation:
    readiness_type: ReadinessType
    status: ReadinessStatus
    blocking_reasons: list[str]
    supporting_value_ids: list[str]


def _values(session: Session, config: VehicleConfiguration, fitment: VehicleFitment | None) -> list[NormalizedValue]:
    statement = select(NormalizedValue).where(NormalizedValue.vehicle_configuration_id == config.id)
    if fitment is None:
        statement = statement.where(NormalizedValue.vehicle_fitment_id.is_(None))
    else:
        statement = statement.where(
            (NormalizedValue.vehicle_fitment_id == fitment.id) | NormalizedValue.vehicle_fitment_id.is_(None)
        )
    return list(session.scalars(statement).all())


def _candidate(values: list[NormalizedValue], code: str) -> NormalizedValue | None:
    matches = [value for value in values if value.parameter_definition.parameter_code == code]
    matches = [value for value in matches if value.availability_state == AvailabilityState.AVAILABLE.value]
    if not matches:
        return None
    preferred = [value for value in matches if value.preferred]
    if preferred:
        return preferred[0]
    uncontested = [value for value in matches if value.resolution_state not in {ResolutionState.CONFLICTING.value, ResolutionState.SUPERSEDED.value}]
    return uncontested[0] if uncontested else matches[0]


def _required_values(values: list[NormalizedValue], codes: list[str]) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    supporting: list[str] = []
    for code in codes:
        candidate = _candidate(values, code)
        if candidate is None:
            blockers.append(f"missing available value: {code}")
        else:
            supporting.append(candidate.id)
    return blockers, supporting


def evaluate_readiness(
    session: Session,
    config: VehicleConfiguration,
    *,
    fitment: VehicleFitment | None = None,
) -> list[ReadinessEvaluation]:
    values = _values(session, config, fitment)
    results: list[ReadinessEvaluation] = []

    identity_ready = config.identity_verification_state in {"RESOLVED_EXACT", "RESOLVED_SAME_GEOMETRY_GROUP"}
    results.append(
        ReadinessEvaluation(
            ReadinessType.IDENTITY_RESOLVED,
            ReadinessStatus.READY if identity_ready else ReadinessStatus.NOT_READY,
            [] if identity_ready else [f"identity state is {config.identity_verification_state}"],
            [],
        )
    )

    dimension_blockers, dimension_supporting = _required_values(
        values,
        ["overall_length_mm", "overall_height_mm", "overall_width_reported_mm", "wheelbase_actual_mm"],
    )
    results.append(
        ReadinessEvaluation(
            ReadinessType.DIMENSION_READY,
            ReadinessStatus.READY if not dimension_blockers else ReadinessStatus.NOT_READY,
            dimension_blockers,
            dimension_supporting,
        )
    )

    avt_blockers: list[str] = []
    avt_supporting: list[str] = []
    for code in ("avt_front_outer_face_track_mm", "avt_rear_outer_face_track_mm"):
        candidate = _candidate(values, code)
        ready, reason = is_avt_track_ready(candidate)
        if not ready:
            avt_blockers.append(f"{code}: {reason}")
        elif candidate is not None:
            avt_supporting.append(candidate.id)

    turning = _candidate(values, "turning_radius_normalized_m")
    turning_ready, turning_reason = is_turning_avt_ready(turning)
    if not turning_ready:
        avt_blockers.append(f"turning: {turning_reason}")
    elif turning is not None:
        avt_supporting.append(turning.id)

    steering = _candidate(values, "avt_maximum_steering_angle_deg")
    if steering is None:
        avt_blockers.append("steering: missing explicit AVT Maximum Steering Angle")
    else:
        avt_supporting.append(steering.id)

    for code in ("avt_lock_to_lock_time_forward_s", "avt_lock_to_lock_time_reverse_s"):
        candidate = _candidate(values, code)
        if candidate is None:
            avt_blockers.append(f"steering: missing explicit {code}")
        else:
            avt_supporting.append(candidate.id)

    plan_assets = [
        asset
        for asset in session.scalars(
            select(GeometryAsset).where(GeometryAsset.vehicle_configuration_id == config.id)
        ).all()
        if fitment is None or asset.vehicle_fitment_id in {None, fitment.id}
    ]
    if not any(asset.geometry_role in {GeometryRole.AVT_PLAN_PROFILE.value, GeometryRole.PLAN_BODY_ENVELOPE.value} for asset in plan_assets):
        avt_blockers.append("body: missing normalized AVT plan/body envelope geometry")

    rear_axles = list(session.scalars(select(Axle).where(Axle.vehicle_configuration_id == config.id)).all())
    relations = list(session.scalars(select(SteeringRelation).where(SteeringRelation.vehicle_configuration_id == config.id)).all())
    rear_ready, rear_reason = rear_steering_mapping_ready(relations, [axle for axle in rear_axles if axle.axle_role == "REAR"])
    if not rear_ready:
        avt_blockers.append(f"rear steering: {rear_reason}")

    results.append(
        ReadinessEvaluation(
            ReadinessType.AVT_READY,
            ReadinessStatus.READY if not avt_blockers else ReadinessStatus.NOT_READY,
            avt_blockers,
            avt_supporting,
        )
    )

    screening_candidates = [
        value
        for value in values
        if value.parameter_definition.parameter_code.startswith("screening_")
        and value.availability_state == AvailabilityState.AVAILABLE.value
    ]
    ramp_blockers: list[str] = []
    ramp_supporting: list[str] = []
    for value in screening_candidates:
        metadata = value.semantic_metadata or {}
        if value.evidence_method != EvidenceMethod.DERIVED.value or metadata.get("ramp_result_class") != "SCREENING":
            ramp_blockers.append(f"{value.parameter_definition.parameter_code}: invalid screening lineage/namespace")
        else:
            ramp_supporting.append(value.id)
    if not screening_candidates:
        ramp_blockers.append("no screening-specific ramp angle is available")
    results.append(
        ReadinessEvaluation(
            ReadinessType.RAMP_SCREENING_READY,
            ReadinessStatus.READY if not ramp_blockers else ReadinessStatus.NOT_READY,
            ramp_blockers,
            ramp_supporting,
        )
    )
    return results


def persist_readiness(
    session: Session,
    config: VehicleConfiguration,
    *,
    fitment: VehicleFitment | None = None,
) -> list[ReadinessResult]:
    evaluated = evaluate_readiness(session, config, fitment=fitment)
    persisted: list[ReadinessResult] = []
    for evaluation in evaluated:
        statement = select(ReadinessResult).where(
            ReadinessResult.vehicle_configuration_id == config.id,
            ReadinessResult.readiness_type == evaluation.readiness_type.value,
        )
        if fitment is None:
            statement = statement.where(ReadinessResult.vehicle_fitment_id.is_(None))
        else:
            statement = statement.where(ReadinessResult.vehicle_fitment_id == fitment.id)
        result = session.scalar(statement)
        if result is None:
            result = ReadinessResult(
                vehicle_configuration_id=config.id,
                vehicle_fitment_id=fitment.id if fitment else None,
                readiness_type=evaluation.readiness_type.value,
            )
            session.add(result)
        result.status = evaluation.status.value
        result.rule_version = READINESS_RULE_VERSION
        result.evaluated_at = datetime.now(timezone.utc)
        result.blocking_reasons = evaluation.blocking_reasons
        result.supporting_value_ids = evaluation.supporting_value_ids
        persisted.append(result)
    session.flush()
    return persisted
