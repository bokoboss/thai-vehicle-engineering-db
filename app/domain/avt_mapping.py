from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AVTMappingResult, GeometryAsset, NormalizedValue, VehicleConfiguration, VehicleFitment
from app.domain.enums import AVTMappingStatus, AvailabilityState, ReadinessType
from app.domain.readiness import evaluate_readiness
from app.domain.validation import is_avt_track_ready, is_turning_avt_ready


ADAPTER_VERSION = "avt-preparation-v1"


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
    available = [
        item
        for item in values
        if item.parameter_definition.parameter_code == code and item.availability_state == AvailabilityState.AVAILABLE.value
    ]
    preferred = [item for item in available if item.preferred]
    return (preferred or available or [None])[0]


def build_avt_mapping(
    session: Session,
    config: VehicleConfiguration,
    *,
    fitment: VehicleFitment | None = None,
    adapter_version: str = ADAPTER_VERSION,
    target_avt_version: str | None = None,
) -> dict[str, Any]:
    values = _values(session, config, fitment)
    blockers: list[str] = []
    payload: dict[str, Any] = {}
    source_value_ids: list[str] = []

    for code, output_key in (
        ("avt_front_outer_face_track_mm", "front_outer_face_track_mm"),
        ("avt_rear_outer_face_track_mm", "rear_outer_face_track_mm"),
    ):
        candidate = _candidate(values, code)
        ready, reason = is_avt_track_ready(candidate)
        if not ready:
            blockers.append(f"{code}: {reason}")
        elif candidate is not None:
            payload[output_key] = float(candidate.numeric_value)
            source_value_ids.append(candidate.id)

    turning = _candidate(values, "turning_radius_normalized_m")
    turning_ready, turning_reason = is_turning_avt_ready(turning)
    if not turning_ready:
        blockers.append(f"turning: {turning_reason}")
    elif turning is not None:
        semantics = turning.semantic_metadata or {}
        payload["turning"] = {
            "radius_m": float(turning.numeric_value),
            "reference": semantics.get("turning_reference"),
            "axle_scope": semantics.get("turning_axle_scope"),
            "wall_envelope_scope": semantics.get("turning_wall_envelope_scope"),
        }
        source_value_ids.append(turning.id)

    steering = _candidate(values, "avt_maximum_steering_angle_deg")
    if steering is None:
        blockers.append("steering: missing explicit AVT Maximum Steering Angle")
    else:
        payload["maximum_steering_angle_deg"] = float(steering.numeric_value)
        source_value_ids.append(steering.id)

    for code, key in (
        ("avt_lock_to_lock_time_forward_s", "lock_to_lock_time_forward_s"),
        ("avt_lock_to_lock_time_reverse_s", "lock_to_lock_time_reverse_s"),
    ):
        candidate = _candidate(values, code)
        if candidate is None:
            blockers.append(f"steering: missing explicit {code}")
        else:
            payload[key] = float(candidate.numeric_value)
            source_value_ids.append(candidate.id)

    assets = list(session.scalars(select(GeometryAsset).where(GeometryAsset.vehicle_configuration_id == config.id)).all())
    assets = [asset for asset in assets if fitment is None or asset.vehicle_fitment_id in {None, fitment.id}]
    plan_asset = next(
        (asset for asset in assets if asset.geometry_role in {"AVT_PLAN_PROFILE", "PLAN_BODY_ENVELOPE"}),
        None,
    )
    if plan_asset is None:
        blockers.append("body: missing normalized AVT plan/body envelope geometry")
    else:
        payload["body_envelope_geometry_asset_id"] = plan_asset.id

    readiness = next(
        result for result in evaluate_readiness(session, config, fitment=fitment) if result.readiness_type == ReadinessType.AVT_READY
    )
    for reason in readiness.blocking_reasons:
        if reason not in blockers:
            blockers.append(reason)

    if not blockers:
        status = AVTMappingStatus.READY
    elif len(payload) == 0:
        status = AVTMappingStatus.BLOCKED
    else:
        status = AVTMappingStatus.PARTIAL
    return {
        "adapter_version": adapter_version,
        "target_avt_version": target_avt_version,
        "status": status.value,
        "payload": payload,
        "blockers": blockers,
        "source_value_ids": source_value_ids,
    }


def persist_avt_mapping(
    session: Session,
    config: VehicleConfiguration,
    *,
    fitment: VehicleFitment | None = None,
    adapter_version: str = ADAPTER_VERSION,
    target_avt_version: str | None = None,
) -> AVTMappingResult:
    result_data = build_avt_mapping(
        session,
        config,
        fitment=fitment,
        adapter_version=adapter_version,
        target_avt_version=target_avt_version,
    )
    result = AVTMappingResult(
        vehicle_configuration_id=config.id,
        vehicle_fitment_id=fitment.id if fitment else None,
        adapter_version=result_data["adapter_version"],
        target_avt_version=result_data["target_avt_version"],
        mapping_status=result_data["status"],
        generated_at=datetime.now(timezone.utc),
        mapping_payload=result_data["payload"],
        blocker_list=result_data["blockers"],
        source_value_ids=result_data["source_value_ids"],
    )
    session.add(result)
    session.flush()
    return result
