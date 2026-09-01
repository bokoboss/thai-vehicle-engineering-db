from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.models import (
    Axle,
    EvidenceLink,
    Manufacturer,
    NormalizedValue,
    ParameterAssessment,
    QAFinding,
    ReadinessResult,
    SourceDocument,
    SourceObservation,
    VehicleConfiguration,
    VehicleModel,
)


def list_vehicles(
    session: Session,
    *,
    search: str | None = None,
    manufacturer: str | None = None,
    body_style: str | None = None,
    powertrain: str | None = None,
    identity_time: str | None = None,
    readiness: str | None = None,
    limit: int | None = None,
) -> list[VehicleConfiguration]:
    statement = (
        select(VehicleConfiguration)
        .join(VehicleConfiguration.vehicle_model)
        .options(joinedload(VehicleConfiguration.vehicle_model).joinedload(VehicleModel.manufacturer))
        .order_by(VehicleConfiguration.stable_vehicle_code)
    )
    if search:
        term = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                VehicleConfiguration.stable_vehicle_code.ilike(term),
                VehicleConfiguration.generation_name.ilike(term),
                VehicleConfiguration.variant_trim.ilike(term),
                VehicleConfiguration.identity_time_label_raw.ilike(term),
                VehicleModel.display_model_name.ilike(term),
            )
        )
    if manufacturer:
        statement = statement.join(Manufacturer).where(Manufacturer.canonical_name == manufacturer)
    if body_style:
        statement = statement.where(VehicleConfiguration.body_style == body_style)
    if powertrain:
        statement = statement.where(VehicleConfiguration.powertrain == powertrain)
    if identity_time:
        statement = statement.where(VehicleConfiguration.identity_time_basis == identity_time)
    if readiness:
        statement = statement.join(
            ReadinessResult,
            (ReadinessResult.vehicle_configuration_id == VehicleConfiguration.id)
            & (ReadinessResult.vehicle_fitment_id.is_(None))
            & (ReadinessResult.readiness_type == readiness),
        ).where(ReadinessResult.status == "READY")
    if limit is not None:
        statement = statement.limit(limit)
    return list(session.scalars(statement).unique().all())


def get_vehicle(session: Session, stable_vehicle_code: str) -> VehicleConfiguration | None:
    statement = (
        select(VehicleConfiguration)
        .where(VehicleConfiguration.stable_vehicle_code == stable_vehicle_code)
        .options(
            joinedload(VehicleConfiguration.vehicle_model).joinedload(VehicleModel.manufacturer),
            selectinload(VehicleConfiguration.fitments),
            selectinload(VehicleConfiguration.axles).selectinload(Axle.steering_relations),
            selectinload(VehicleConfiguration.steering_relations),
            selectinload(VehicleConfiguration.load_conditions),
            selectinload(VehicleConfiguration.source_observations).joinedload(SourceObservation.source_document),
            selectinload(VehicleConfiguration.normalized_values).joinedload(NormalizedValue.parameter_definition),
            selectinload(VehicleConfiguration.normalized_values).joinedload(NormalizedValue.vehicle_fitment),
            selectinload(VehicleConfiguration.normalized_values).joinedload(NormalizedValue.load_condition),
            selectinload(VehicleConfiguration.normalized_values)
            .selectinload(NormalizedValue.evidence_links)
            .joinedload(EvidenceLink.source_observation)
            .joinedload(SourceObservation.source_document),
            selectinload(VehicleConfiguration.parameter_assessments).joinedload(ParameterAssessment.parameter_definition),
            selectinload(VehicleConfiguration.geometry_assets),
            selectinload(VehicleConfiguration.readiness_results),
            selectinload(VehicleConfiguration.qa_findings),
            selectinload(VehicleConfiguration.avt_mapping_results),
        )
    )
    return session.scalar(statement)


def list_issue_rows(session: Session) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    readiness_rows = session.scalars(
        select(ReadinessResult)
        .where(ReadinessResult.status != "READY")
        .options(joinedload(ReadinessResult.vehicle_configuration).joinedload(VehicleConfiguration.vehicle_model).joinedload(VehicleModel.manufacturer))
        .order_by(ReadinessResult.vehicle_configuration_id, ReadinessResult.readiness_type)
    ).all()
    for result in readiness_rows:
        rows.append(
            {
                "kind": "READINESS",
                "code": result.readiness_type,
                "severity": "WARNING",
                "status": result.status,
                "vehicle": result.vehicle_configuration,
                "message": "; ".join(result.blocking_reasons) or "not ready",
            }
        )
    qa_rows = session.scalars(
        select(QAFinding)
        .where(QAFinding.status == "OPEN")
        .options(joinedload(QAFinding.vehicle_configuration).joinedload(VehicleConfiguration.vehicle_model).joinedload(VehicleModel.manufacturer))
        .order_by(QAFinding.severity.desc(), QAFinding.created_at)
    ).all()
    for finding in qa_rows:
        rows.append(
            {
                "kind": "QA",
                "code": finding.finding_code,
                "severity": finding.severity,
                "status": finding.status,
                "vehicle": finding.vehicle_configuration,
                "message": finding.message,
            }
        )
    return rows
