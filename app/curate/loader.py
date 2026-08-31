from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.curate.report import ImportReport, ReadinessReport
from app.curate.schemas import CurationManifest
from app.curate.validation import (
    CurationError,
    ManifestValidation,
    load_manifest,
    parse_manifest,
    source_notes,
    validate_manifest,
)
from app.db.models import ParameterDefinition, SourceDocument, VehicleConfiguration
from app.domain.enums import EvidenceRole, ResolutionState
from app.domain.readiness import persist_readiness
from app.domain.schemas import (
    AxleCreate,
    ConflictDecisionCreate,
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
from app.seed.registry import seed_registry
from app.services.foundation import (
    create_axle,
    create_conflict_decision,
    create_fitment,
    create_geometry_asset,
    create_load_condition,
    create_normalized_value,
    create_parameter_assessment,
    create_source_document,
    create_source_observation,
    create_steering_relation,
    create_vehicle_configuration,
)


def _as_manifest(document: str | Path | Mapping[str, Any] | CurationManifest) -> CurationManifest:
    if isinstance(document, (str, Path)):
        return load_manifest(document)
    if isinstance(document, CurationManifest):
        return document
    return parse_manifest(document)


def initialize_registry(session: Session) -> int:
    """Seed parameter definitions only; never seed Phase 0 vehicle fixtures."""

    session.rollback()
    try:
        definitions = seed_registry(session)
        session.commit()
        return len(definitions)
    except Exception:
        session.rollback()
        raise


def _source_payload(source: Any) -> SourceDocumentCreate:
    return SourceDocumentCreate(
        source_code=source.source_code,
        title=source.title,
        publisher=source.publisher,
        authority_class=source.authority_class.value,
        source_type=source.source_type.value,
        market_code=source.market_code,
        publication_year=source.publication_year,
        model_year_from=source.model_year_from,
        model_year_to=source.model_year_to,
        url=source.url,
        retrieved_at=source.retrieved_at,
        local_snapshot_reference=source.local_snapshot_reference,
        content_hash=source.content_hash,
        page_section_default=source.page_section_default,
        access_licensing_notes=source.access_licensing_notes,
        applicability_notes=source.applicability_notes,
        archival_status=source.archival_status,
        notes=source_notes(source),
    )


def _vehicle_payload(manifest: CurationManifest) -> VehicleConfigurationCreate:
    vehicle = manifest.vehicle
    return VehicleConfigurationCreate(
        stable_vehicle_code=vehicle.stable_vehicle_code,
        market_code=vehicle.market_code,
        generation_name=vehicle.generation_name,
        body_style=vehicle.body_style,
        model_year_from=vehicle.model_year_from,
        model_year_to=vehicle.model_year_to,
        identity_time_basis=vehicle.identity_time_basis,
        identity_time_label_raw=vehicle.identity_time_label_raw,
        variant_trim=vehicle.variant_trim,
        chassis_platform_code=vehicle.chassis_platform_code,
        sale_period_from=vehicle.sale_period_from,
        sale_period_to=vehicle.sale_period_to,
        powertrain=vehicle.powertrain,
        drivetrain=vehicle.drivetrain,
        body_configuration=vehicle.body_configuration,
        identity_notes=vehicle.identity_notes,
        identity_verification_state=vehicle.identity_verification_state,
    )


def _require_mapping(mapping: Mapping[str, Any], code: str, kind: str) -> Any:
    try:
        return mapping[code]
    except KeyError as exc:
        raise CurationError(f"{kind} reference {code} could not be resolved during import") from exc


def _normalized_value_payload(
    value: Any,
    definition: ParameterDefinition,
    *,
    load_condition_id: str | None,
) -> NormalizedValueCreate:
    data = value.model_dump()
    raw_value = data.pop("value")
    data.pop("value_code")
    data.pop("load_condition_code")
    data.pop("fitment_code")
    data.pop("evidence_observation_codes")
    data["parameter_code"] = definition.parameter_code
    data["load_condition_id"] = load_condition_id
    data_type = getattr(definition.data_type, "value", definition.data_type)
    data[
        {
            "NUMBER": "numeric_value",
            "TEXT": "text_value",
            "BOOLEAN": "boolean_value",
            "ENUM": "enum_value",
            "JSON": "json_value",
        }[data_type]
    ] = raw_value
    return NormalizedValueCreate(**data)


def _readiness_report(
    session: Session,
    config: VehicleConfiguration,
    fitments: Mapping[str, Any],
) -> list[ReadinessReport]:
    rows: list[ReadinessReport] = []
    scopes: list[tuple[str, Any | None]] = [("", None)]
    scopes.extend((code, fitment) for code, fitment in sorted(fitments.items()))
    for fitment_code, fitment in scopes:
        for result in sorted(
            persist_readiness(session, config, fitment=fitment),
            key=lambda item: item.readiness_type,
        ):
            rows.append(
                ReadinessReport(
                    fitment_code=fitment_code,
                    readiness_type=result.readiness_type,
                    status=result.status,
                    blocking_reasons=list(result.blocking_reasons or []),
                )
            )
    return rows


def _make_report(
    *,
    status: str,
    config: VehicleConfiguration,
    database_identifier: str,
    source_created: int,
    source_reused: int,
    observations: int,
    values: list[Any],
    assessments: int,
    loads: int,
    fitments: int,
    axles: int,
    steering_relations: int,
    geometry_assets: int,
    conflict_decisions: int,
    readiness: list[ReadinessReport],
) -> ImportReport:
    conflict_values = sum(
        value.resolution_state
        in {ResolutionState.CONFLICTING.value, ResolutionState.PREFERRED_WITH_CONFLICT.value}
        for value in values
    )
    return ImportReport(
        status=status,
        stable_vehicle_code=config.stable_vehicle_code,
        database_identifier=database_identifier,
        sources_created=source_created,
        sources_reused=source_reused,
        observations=observations,
        normalized_values=len(values),
        assessments=assessments,
        loads=loads,
        fitments=fitments,
        axles=axles,
        steering_relations=steering_relations,
        geometry_assets=geometry_assets,
        conflicts=conflict_values,
        conflict_decisions=conflict_decisions,
        readiness=readiness,
    )


def import_manifest(
    session: Session,
    document: str | Path | Mapping[str, Any] | CurationManifest,
    *,
    dry_run: bool = False,
) -> ImportReport:
    """Import one manifest in one transaction, or roll it back for a dry run."""

    manifest = _as_manifest(document)
    plan: ManifestValidation = validate_manifest(session, manifest)
    session.rollback()

    try:
        sources: dict[str, SourceDocument] = {}
        source_created = 0
        source_reused = 0
        for source_spec in manifest.sources:
            existing = session.scalar(
                select(SourceDocument).where(SourceDocument.source_code == source_spec.source_code)
            )
            if existing is not None:
                sources[source_spec.source_code] = existing
                source_reused += 1
            else:
                sources[source_spec.source_code] = create_source_document(session, _source_payload(source_spec))
                source_created += 1

        config = create_vehicle_configuration(
            session,
            _vehicle_payload(manifest),
            manufacturer_name=manifest.vehicle.manufacturer_name,
            manufacturer_display_name=manifest.vehicle.manufacturer_display_name,
            canonical_model_name=manifest.vehicle.canonical_model_name,
            display_model_name=manifest.vehicle.display_model_name,
        )

        fitments: dict[str, Any] = {}
        for fitment_spec in manifest.fitments:
            data = fitment_spec.model_dump()
            fitment_code = data.pop("fitment_code")
            fitments[fitment_code] = create_fitment(session, config, fitment_code, **data)

        loads: dict[str, Any] = {}
        for load_spec in manifest.load_conditions:
            data = load_spec.model_dump()
            load_code = data.pop("load_condition_code")
            source_code = data.pop("source_code")
            data["source_document_id"] = sources[source_code].id if source_code else None
            loads[load_code] = create_load_condition(session, config, LoadConditionCreate(**data))

        axles: dict[str, Any] = {}
        for axle_spec in manifest.axles:
            data = axle_spec.model_dump()
            axle_code = data.pop("axle_code")
            axles[axle_code] = create_axle(session, config, AxleCreate(**data))

        observations: dict[str, Any] = {}
        for observation_spec in manifest.observations:
            data = observation_spec.model_dump()
            observation_code = data.pop("observation_code")
            source_code = data.pop("source_code")
            data["source_document_id"] = _require_mapping(sources, source_code, "source").id
            observations[observation_code] = create_source_observation(
                session,
                config,
                SourceObservationCreate(**data),
            )

        values: dict[str, Any] = {}
        for value_spec in manifest.values:
            definition = _require_mapping(plan.parameter_definitions, value_spec.parameter_code, "parameter")
            load_condition = (
                _require_mapping(loads, value_spec.load_condition_code, "load condition")
                if value_spec.load_condition_code
                else None
            )
            fitment = (
                _require_mapping(fitments, value_spec.fitment_code, "fitment")
                if value_spec.fitment_code
                else None
            )
            links = [
                EvidenceLinkCreate(
                    source_observation_id=_require_mapping(observations, code, "observation").id,
                    evidence_role=EvidenceRole.PRIMARY,
                )
                for code in value_spec.evidence_observation_codes
            ]
            value = create_normalized_value(
                session,
                config,
                _normalized_value_payload(
                    value_spec,
                    definition,
                    load_condition_id=load_condition.id if load_condition else None,
                ),
                evidence_links=links,
                fitment=fitment,
            )
            values[value_spec.value_code] = value

        assessment_count = 0
        for assessment_spec in manifest.assessments:
            fitment = (
                _require_mapping(fitments, assessment_spec.fitment_code, "fitment")
                if assessment_spec.fitment_code
                else None
            )
            data = assessment_spec.model_dump()
            data.pop("fitment_code")
            create_parameter_assessment(
                session,
                config,
                ParameterAssessmentCreate(**data),
                fitment=fitment,
            )
            assessment_count += 1

        steering_count = 0
        for relation_spec in manifest.steering_relations:
            data = relation_spec.model_dump()
            axle_code = data.pop("axle_code")
            source_observation_code = data.pop("source_observation_code")
            data["axle_id"] = _require_mapping(axles, axle_code, "axle").id
            data["source_observation_id"] = (
                _require_mapping(observations, source_observation_code, "observation").id
                if source_observation_code
                else None
            )
            create_steering_relation(session, config, SteeringRelationCreate(**data))
            steering_count += 1

        geometry_count = 0
        for asset_spec in manifest.geometry_assets:
            data = asset_spec.model_dump()
            data.pop("geometry_code")
            load_condition_code = data.pop("load_condition_code")
            fitment_code = data.pop("fitment_code")
            source_code = data.pop("source_code")
            data["load_condition_id"] = (
                _require_mapping(loads, load_condition_code, "load condition").id
                if load_condition_code
                else None
            )
            data["source_document_id"] = (
                _require_mapping(sources, source_code, "source").id if source_code else None
            )
            create_geometry_asset(
                session,
                config,
                GeometryAssetCreate(**data),
                fitment=(
                    _require_mapping(fitments, fitment_code, "fitment") if fitment_code else None
                ),
            )
            geometry_count += 1

        decision_count = 0
        for decision_spec in manifest.conflict_decisions:
            data = decision_spec.model_dump()
            data.pop("conflict_decision_code")
            selected_value_code = data.pop("selected_value_code")
            data["selected_normalized_value_id"] = (
                _require_mapping(values, selected_value_code, "value").id
                if selected_value_code
                else None
            )
            create_conflict_decision(
                session,
                config,
                ConflictDecisionCreate(**data),
            )
            decision_count += 1

        readiness = _readiness_report(session, config, fitments)
        session.flush()
        report = _make_report(
            status="DRY_RUN" if dry_run else "PASS",
            config=config,
            database_identifier=_database_identifier(session),
            source_created=source_created,
            source_reused=source_reused,
            observations=len(observations),
            values=list(values.values()),
            assessments=assessment_count,
            loads=len(loads),
            fitments=len(fitments),
            axles=len(axles),
            steering_relations=steering_count,
            geometry_assets=geometry_count,
            conflict_decisions=decision_count,
            readiness=readiness,
        )
        if dry_run:
            session.rollback()
        else:
            session.commit()
        return report
    except CurationError:
        session.rollback()
        raise
    except Exception as exc:
        session.rollback()
        raise CurationError(str(exc)) from exc


def _database_identifier(session: Session) -> str:
    """Return a connection identifier with credentials and query secrets removed."""

    url = session.get_bind().url
    return url.set(username=None, password=None, query={}).render_as_string(hide_password=True)
