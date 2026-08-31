from __future__ import annotations

import csv
import io
import json
from collections.abc import Iterable
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.models import (
    DerivationRun,
    EvidenceLink,
    Manufacturer,
    NormalizedValue,
    ParameterAssessment,
    SourceObservation,
    VehicleConfiguration,
    VehicleModel,
)


EXPORT_COLUMNS = [
    "vehicle_id",
    "stable_vehicle_code",
    "manufacturer",
    "commercial_model",
    "generation",
    "variant",
    "market",
    "model_year_from",
    "model_year_to",
    "identity_time_basis",
    "identity_time_label_raw",
    "sale_period_from",
    "sale_period_to",
    "fitment_code",
    "parameter_code",
    "normalized_value",
    "normalized_unit",
    "value_kind",
    "evidence_method",
    "resolution_state",
    "verification_state",
    "availability_state",
    "preferred",
    "authority_grade",
    "applicability_grade",
    "precision",
    "uncertainty_value",
    "uncertainty_unit",
    "load_condition_id",
    "source_observation_ids",
    "source_document_codes",
    "derivation_run_id",
    "derivation_rule_code",
    "derivation_rule_version",
    "assessment_reason",
    "semantic_metadata_json",
]


def _typed_value(value: NormalizedValue) -> Any:
    if value.numeric_value is not None:
        return float(value.numeric_value)
    if value.text_value is not None:
        return value.text_value
    if value.boolean_value is not None:
        return value.boolean_value
    if value.enum_value is not None:
        return value.enum_value
    return value.json_value


def _base_identity(config: VehicleConfiguration) -> dict[str, Any]:
    return {
        "vehicle_id": config.id,
        "stable_vehicle_code": config.stable_vehicle_code,
        "manufacturer": config.vehicle_model.manufacturer.display_name,
        "commercial_model": config.vehicle_model.display_model_name,
        "generation": config.generation_name,
        "variant": config.variant_trim,
        "market": config.market_code,
        "model_year_from": config.model_year_from,
        "model_year_to": config.model_year_to,
        "identity_time_basis": config.identity_time_basis,
        "identity_time_label_raw": config.identity_time_label_raw or "",
        "sale_period_from": config.sale_period_from or "",
        "sale_period_to": config.sale_period_to or "",
    }


def export_rows(session: Session, stable_vehicle_codes: Iterable[str] | None = None) -> list[dict[str, Any]]:
    code_set = set(stable_vehicle_codes or [])
    configs = list(
        session.scalars(
            select(VehicleConfiguration)
            .options(joinedload(VehicleConfiguration.vehicle_model).joinedload(VehicleModel.manufacturer), selectinload(VehicleConfiguration.fitments))
            .order_by(VehicleConfiguration.stable_vehicle_code)
        ).all()
    )
    if code_set:
        configs = [config for config in configs if config.stable_vehicle_code in code_set]
    rows: list[dict[str, Any]] = []
    for config in configs:
        values = list(
            session.scalars(
                select(NormalizedValue)
                .where(NormalizedValue.vehicle_configuration_id == config.id)
                .options(
                    joinedload(NormalizedValue.parameter_definition),
                    joinedload(NormalizedValue.vehicle_fitment),
                    selectinload(NormalizedValue.evidence_links)
                    .joinedload(EvidenceLink.source_observation)
                    .joinedload(SourceObservation.source_document),
                    joinedload(NormalizedValue.derivation_run).joinedload(DerivationRun.derivation_rule),
                )
                .order_by(NormalizedValue.id)
            ).all()
        )
        assessments = list(
            session.scalars(
                select(ParameterAssessment)
                .where(ParameterAssessment.vehicle_configuration_id == config.id)
                .options(joinedload(ParameterAssessment.parameter_definition), joinedload(ParameterAssessment.vehicle_fitment))
                .order_by(ParameterAssessment.id)
            ).all()
        )
        for value in values:
            source_observation_ids = [link.source_observation_id for link in value.evidence_links]
            source_document_codes = sorted(
                {
                    link.source_observation.source_document.source_code
                    for link in value.evidence_links
                    if link.source_observation and link.source_observation.source_document
                }
            )
            run = value.derivation_run
            row = _base_identity(config)
            row.update(
                {
                    "fitment_code": value.vehicle_fitment.fitment_code if value.vehicle_fitment else "",
                    "parameter_code": value.parameter_definition.parameter_code,
                    "normalized_value": _typed_value(value),
                    "normalized_unit": value.canonical_unit or value.parameter_definition.canonical_unit or "",
                    "value_kind": "normalized",
                    "evidence_method": value.evidence_method,
                    "resolution_state": value.resolution_state,
                    "verification_state": value.verification_state,
                    "availability_state": value.availability_state,
                    "preferred": value.preferred,
                    "authority_grade": value.authority_grade or "",
                    "applicability_grade": value.applicability_grade or "",
                    "precision": value.precision or "",
                    "uncertainty_value": float(value.uncertainty_value) if value.uncertainty_value is not None else "",
                    "uncertainty_unit": value.uncertainty_unit or "",
                    "load_condition_id": value.load_condition_id or "",
                    "source_observation_ids": ";".join(source_observation_ids),
                    "source_document_codes": ";".join(source_document_codes),
                    "derivation_run_id": run.id if run else "",
                    "derivation_rule_code": run.derivation_rule.rule_code if run and run.derivation_rule else "",
                    "derivation_rule_version": run.derivation_rule.version if run and run.derivation_rule else "",
                    "assessment_reason": "",
                    "semantic_metadata_json": json.dumps(value.semantic_metadata or {}, sort_keys=True),
                }
            )
            rows.append(row)
        for assessment in assessments:
            row = _base_identity(config)
            row.update(
                {
                    "fitment_code": assessment.vehicle_fitment.fitment_code if assessment.vehicle_fitment else "",
                    "parameter_code": assessment.parameter_definition.parameter_code,
                    "normalized_value": "",
                    "normalized_unit": assessment.parameter_definition.canonical_unit or "",
                    "value_kind": "assessment",
                    "evidence_method": "NONE",
                    "resolution_state": "NOT_APPLICABLE",
                    "verification_state": "UNREVIEWED",
                    "availability_state": assessment.availability_state,
                    "preferred": False,
                    "authority_grade": "",
                    "applicability_grade": "",
                    "precision": "",
                    "uncertainty_value": "",
                    "uncertainty_unit": "",
                    "load_condition_id": "",
                    "source_observation_ids": "",
                    "source_document_codes": "",
                    "derivation_run_id": "",
                    "derivation_rule_code": "",
                    "derivation_rule_version": "",
                    "assessment_reason": assessment.unknown_reason,
                    "semantic_metadata_json": json.dumps({"source_families_searched": assessment.source_families_searched or []}, sort_keys=True),
                }
            )
            rows.append(row)
    return rows


def csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=EXPORT_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8-sig")


def xlsx_bytes(rows: list[dict[str, Any]]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Engineering Data"
    sheet.append(EXPORT_COLUMNS)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for row in rows:
        sheet.append([row.get(column, "") for column in EXPORT_COLUMNS])
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for column_cells in sheet.columns:
        column_letter = column_cells[0].column_letter
        max_length = max(len(str(cell.value or "")) for cell in column_cells[:50])
        sheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 42)
    stream = io.BytesIO()
    workbook.save(stream)
    return stream.getvalue()
