from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.config import PROJECT_ROOT
from app.db.models import ReadinessResult, VehicleConfiguration
from app.db.repositories import get_vehicle, list_issue_rows, list_vehicles
from app.db.session import get_session
from app.domain.readiness import evaluate_readiness
from app.exports.exporter import csv_bytes, export_rows, xlsx_bytes


router = APIRouter()
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "app" / "web" / "templates"))


def _typed_value(value: Any) -> Any:
    if value.numeric_value is not None:
        return float(value.numeric_value)
    if value.text_value is not None:
        return value.text_value
    if value.boolean_value is not None:
        return value.boolean_value
    if value.enum_value is not None:
        return value.enum_value
    return value.json_value


def _readiness_dict(session: Session, config: VehicleConfiguration) -> dict[str, dict[str, Any]]:
    persisted = session.scalars(
        select(ReadinessResult).where(ReadinessResult.vehicle_configuration_id == config.id)
    ).all()
    if not persisted:
        return {
            evaluation.readiness_type.value: {
                "status": evaluation.status.value,
                "blocking_reasons": evaluation.blocking_reasons,
            }
            for evaluation in evaluate_readiness(session, config)
        }
    return {
        row.readiness_type: {
            "status": row.status,
            "blocking_reasons": row.blocking_reasons,
        }
        for row in persisted
        if row.vehicle_fitment_id is None
    }


def _summary(session: Session, config: VehicleConfiguration) -> dict[str, Any]:
    readiness = _readiness_dict(session, config)
    return {
        "id": config.id,
        "stable_vehicle_code": config.stable_vehicle_code,
        "manufacturer": config.vehicle_model.manufacturer.display_name,
        "commercial_model": config.vehicle_model.display_model_name,
        "generation": config.generation_name,
        "variant": config.variant_trim,
        "market": config.market_code,
        "body_style": config.body_style,
        "model_year_from": config.model_year_from,
        "model_year_to": config.model_year_to,
        "identity_verification_state": config.identity_verification_state,
        "readiness": readiness,
    }


def _detail(session: Session, config: VehicleConfiguration) -> dict[str, Any]:
    values = []
    for value in config.normalized_values:
        observations = [
            {
                "id": link.source_observation.id,
                "source_code": link.source_observation.source_document.source_code,
                "raw_label": link.source_observation.raw_label,
                "raw_value": link.source_observation.raw_value,
                "raw_unit": link.source_observation.raw_unit,
                "evidence_role": link.evidence_role,
            }
            for link in value.evidence_links
            if link.source_observation is not None
        ]
        values.append(
            {
                "id": value.id,
                "parameter_code": value.parameter_definition.parameter_code,
                "display_name": value.parameter_definition.display_name,
                "value": _typed_value(value),
                "unit": value.canonical_unit or value.parameter_definition.canonical_unit,
                "evidence_method": value.evidence_method,
                "resolution_state": value.resolution_state,
                "verification_state": value.verification_state,
                "availability_state": value.availability_state,
                "preferred": value.preferred,
                "uncertainty_value": float(value.uncertainty_value) if value.uncertainty_value is not None else None,
                "uncertainty_unit": value.uncertainty_unit,
                "semantic_metadata": value.semantic_metadata or {},
                "observations": observations,
                "derivation_rule": (
                    {"code": value.derivation_run.derivation_rule.rule_code, "version": value.derivation_run.derivation_rule.version}
                    if value.derivation_run and value.derivation_run.derivation_rule
                    else None
                ),
            }
        )
    assessments = [
        {
            "parameter_code": assessment.parameter_definition.parameter_code,
            "availability_state": assessment.availability_state,
            "unknown_reason": assessment.unknown_reason,
            "source_families_searched": assessment.source_families_searched or [],
        }
        for assessment in config.parameter_assessments
    ]
    return {
        **_summary(session, config),
        "powertrain": config.powertrain,
        "drivetrain": config.drivetrain,
        "body_configuration": config.body_configuration,
        "identity_notes": config.identity_notes,
        "fitments": [
            {
                "code": fitment.fitment_code,
                "description": fitment.description,
                "wheel_package": fitment.wheel_package,
                "equipment_package": fitment.equipment_package,
            }
            for fitment in config.fitments
        ],
        "values": values,
        "assessments": assessments,
        "geometry_assets": [
            {
                "id": asset.id,
                "role": asset.geometry_role,
                "representation_type": asset.representation_type,
                "fidelity": asset.geometry_fidelity,
                "datum": asset.coordinate_system_version,
                "uncertainty": asset.uncertainty_description,
            }
            for asset in config.geometry_assets
        ],
        "readiness_results": [
            {
                "type": evaluation.readiness_type.value,
                "status": evaluation.status.value,
                "blocking_reasons": evaluation.blocking_reasons,
            }
            for evaluation in evaluate_readiness(session, config)
        ],
    }


@router.get("/", include_in_schema=False)
def home() -> RedirectResponse:
    return RedirectResponse(url="/vehicles", status_code=307)


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/vehicles")
def api_vehicles(
    session: Session = Depends(get_session),
    q: str | None = Query(default=None),
    manufacturer: str | None = Query(default=None),
    body_style: str | None = Query(default=None),
    readiness: str | None = Query(default=None),
) -> dict[str, Any]:
    items = list_vehicles(session, search=q, manufacturer=manufacturer, body_style=body_style, readiness=readiness)
    return {"count": len(items), "items": [_summary(session, item) for item in items]}


@router.get("/api/vehicles/{stable_vehicle_code}")
def api_vehicle(stable_vehicle_code: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    config = get_vehicle(session, stable_vehicle_code)
    if config is None:
        raise HTTPException(status_code=404, detail="vehicle configuration not found")
    return _detail(session, config)


@router.get("/api/issues")
def api_issues(session: Session = Depends(get_session)) -> dict[str, Any]:
    rows = list_issue_rows(session)
    return {
        "count": len(rows),
        "items": [
            {
                "kind": row["kind"],
                "code": row["code"],
                "severity": row["severity"],
                "status": row["status"],
                "vehicle": row["vehicle"].stable_vehicle_code if row["vehicle"] else None,
                "message": row["message"],
            }
            for row in rows
        ],
    }


@router.get("/vehicles", response_class=HTMLResponse)
def vehicles_page(
    request: Request,
    session: Session = Depends(get_session),
    q: str | None = Query(default=None),
    manufacturer: str | None = Query(default=None),
    body_style: str | None = Query(default=None),
    readiness: str | None = Query(default=None),
) -> HTMLResponse:
    items = list_vehicles(session, search=q, manufacturer=manufacturer, body_style=body_style, readiness=readiness)
    return templates.TemplateResponse(
        request=request,
        name="vehicles.html",
        context={
            "vehicles": [_summary(session, item) for item in items],
            "q": q or "",
            "manufacturer": manufacturer or "",
            "body_style": body_style or "",
            "readiness": readiness or "",
        },
    )


@router.get("/vehicles/{stable_vehicle_code}", response_class=HTMLResponse)
def vehicle_page(stable_vehicle_code: str, request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    config = get_vehicle(session, stable_vehicle_code)
    if config is None:
        raise HTTPException(status_code=404, detail="vehicle configuration not found")
    return templates.TemplateResponse(request=request, name="vehicle_detail.html", context={"vehicle": _detail(session, config)})


@router.get("/issues", response_class=HTMLResponse)
def issues_page(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    rows = list_issue_rows(session)
    return templates.TemplateResponse(request=request, name="issues.html", context={"issues": rows})


@router.get("/compare", response_class=HTMLResponse)
def compare_page(
    request: Request,
    session: Session = Depends(get_session),
    codes: str | None = Query(default=None),
) -> HTMLResponse:
    selected_codes = [code.strip() for code in (codes or "").split(",") if code.strip()][:4]
    configs = [get_vehicle(session, code) for code in selected_codes]
    configs = [config for config in configs if config is not None]
    return templates.TemplateResponse(
        request=request,
        name="compare.html",
        context={"vehicles": [_detail(session, config) for config in configs], "selected_codes": ",".join(selected_codes)},
    )


def _export_response(session: Session, codes: str | None, xlsx: bool) -> Response:
    selected_codes = [code.strip() for code in (codes or "").split(",") if code.strip()]
    rows = export_rows(session, selected_codes or None)
    if xlsx:
        return Response(
            content=xlsx_bytes(rows),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=vehicle-engineering-export.xlsx"},
        )
    return Response(
        content=csv_bytes(rows),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=vehicle-engineering-export.csv"},
    )


@router.get("/exports/vehicles.csv")
def export_csv(codes: str | None = Query(default=None), session: Session = Depends(get_session)) -> Response:
    return _export_response(session, codes, xlsx=False)


@router.get("/exports/vehicles.xlsx")
def export_xlsx(codes: str | None = Query(default=None), session: Session = Depends(get_session)) -> Response:
    return _export_response(session, codes, xlsx=True)
