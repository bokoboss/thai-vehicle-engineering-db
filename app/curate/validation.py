from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Manufacturer, ParameterDefinition, SourceDocument, VehicleConfiguration, VehicleModel
from app.domain.enums import DataType
from app.curate.schemas import CurationManifest, CurationSource


class CurationError(ValueError):
    """Raised when a curation manifest cannot pass the importer contract."""


@dataclass(frozen=True)
class ManifestValidation:
    manifest: CurationManifest
    parameter_definitions: dict[str, ParameterDefinition]
    existing_sources: dict[str, SourceDocument]


def _duplicate_key_guard(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant is not allowed: {value}")


def _format_validation_error(error: ValidationError) -> str:
    messages: list[str] = []
    for item in error.errors(include_url=False):
        location = ".".join(str(part) for part in item.get("loc", ())) or "manifest"
        messages.append(f"{location}: {item.get('msg', 'invalid value')}")
    return "; ".join(messages)


def parse_manifest(document: Mapping[str, Any] | CurationManifest) -> CurationManifest:
    if isinstance(document, CurationManifest):
        return document
    try:
        return CurationManifest.model_validate(document)
    except ValidationError as exc:
        raise CurationError(_format_validation_error(exc)) from exc


def load_manifest(path: str | Path) -> CurationManifest:
    manifest_path = Path(path)
    try:
        raw = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CurationError(f"cannot read manifest {manifest_path}: {exc}") from exc
    try:
        document = json.loads(
            raw,
            object_pairs_hook=_duplicate_key_guard,
            parse_constant=_reject_json_constant,
        )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise CurationError(f"invalid JSON in {manifest_path}: {exc}") from exc
    if not isinstance(document, dict):
        raise CurationError("manifest root must be a JSON object")
    try:
        return parse_manifest(document)
    except CurationError as exc:
        raise CurationError(f"invalid manifest {manifest_path}: {exc}") from exc


def source_notes(source: CurationSource) -> str | None:
    """Preserve research subtype and curator notes in the existing notes field."""

    parts: list[str] = []
    if source.source_subtype_raw is not None:
        parts.append(f"source_subtype_raw: {source.source_subtype_raw}")
    if source.notes:
        parts.append(source.notes)
    return "\n".join(parts) or None


_SOURCE_SUBTYPE_NOTE_PREFIX = "source_subtype_raw: "


def _source_subtype_from_notes(notes: str | None) -> str | None:
    if not notes:
        return None
    for line in notes.splitlines():
        if line.startswith(_SOURCE_SUBTYPE_NOTE_PREFIX):
            return line[len(_SOURCE_SUBTYPE_NOTE_PREFIX) :]
    return None


def _datetime_key(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _datetimes_compatible(expected: datetime | None, actual: datetime | None) -> bool:
    if expected is None or actual is None:
        return expected is actual
    # SQLite's DateTime(timezone=True) adapter returns a naive value while
    # preserving the original wall-clock fields. PostgreSQL keeps the offset,
    # so compare instants when both sides carry timezone information and wall
    # time when the backend has stripped it.
    if expected.tzinfo is None or actual.tzinfo is None:
        return expected.replace(tzinfo=None) == actual.replace(tzinfo=None)
    return expected.astimezone(timezone.utc) == actual.astimezone(timezone.utc)


def _source_core_values(source: CurationSource) -> dict[str, Any]:
    return {
        "title": source.title,
        "publisher": source.publisher,
        "authority_class": source.authority_class.value,
        "source_type": source.source_type.value,
        "market_code": source.market_code,
        "publication_year": source.publication_year,
        "model_year_from": source.model_year_from,
        "model_year_to": source.model_year_to,
        "url": source.url,
        "retrieved_at": _datetime_key(source.retrieved_at),
        "local_snapshot_reference": source.local_snapshot_reference,
        "content_hash": source.content_hash,
        "page_section_default": source.page_section_default,
        "access_licensing_notes": source.access_licensing_notes,
        "applicability_notes": source.applicability_notes,
        "archival_status": source.archival_status,
    }


def _persisted_source_core_values(source: SourceDocument) -> dict[str, Any]:
    return {
        "title": source.title,
        "publisher": source.publisher,
        "authority_class": source.authority_class,
        "source_type": source.source_type,
        "market_code": source.market_code,
        "publication_year": source.publication_year,
        "model_year_from": source.model_year_from,
        "model_year_to": source.model_year_to,
        "url": source.url,
        "retrieved_at": _datetime_key(source.retrieved_at),
        "local_snapshot_reference": source.local_snapshot_reference,
        "content_hash": source.content_hash,
        "page_section_default": source.page_section_default,
        "access_licensing_notes": source.access_licensing_notes,
        "applicability_notes": source.applicability_notes,
        "archival_status": source.archival_status,
    }


def _validate_existing_source(source: CurationSource, existing: SourceDocument) -> None:
    expected = _source_core_values(source)
    actual = _persisted_source_core_values(existing)
    differences = sorted(
        key
        for key in expected
        if (
            not _datetimes_compatible(source.retrieved_at, existing.retrieved_at)
            if key == "retrieved_at"
            else expected[key] != actual[key]
        )
    )
    if differences:
        raise CurationError(
            f"source_code {source.source_code} conflicts with existing source metadata: {', '.join(differences)}"
        )

    existing_notes = existing.notes or ""
    if source.source_subtype_raw != _source_subtype_from_notes(existing.notes):
        raise CurationError(
            f"source_code {source.source_code} has incompatible source_subtype_raw; refusing to mutate source metadata"
        )
    if source.notes and source.notes not in existing_notes:
        raise CurationError(
            f"source_code {source.source_code} has incompatible existing notes; refusing to mutate source metadata"
        )


def _validate_existing_manufacturer_model(session: Session, manifest: CurationManifest) -> None:
    vehicle = manifest.vehicle
    manufacturer = session.scalar(
        select(Manufacturer).where(Manufacturer.canonical_name == vehicle.manufacturer_name)
    )
    if manufacturer is None:
        return
    if manufacturer.display_name != vehicle.manufacturer_display_name:
        raise CurationError(
            f"manufacturer {vehicle.manufacturer_name} has incompatible display metadata; refusing to mutate it"
        )

    model = session.scalar(
        select(VehicleModel).where(
            VehicleModel.manufacturer_id == manufacturer.id,
            VehicleModel.canonical_model_name == vehicle.canonical_model_name,
        )
    )
    if model is not None and model.display_model_name != vehicle.display_model_name:
        raise CurationError(
            f"model {vehicle.canonical_model_name} has incompatible display metadata; refusing to mutate it"
        )


def _validate_manifest_value_type(value: Any, definition: ParameterDefinition) -> None:
    data_type = definition.data_type.value if hasattr(definition.data_type, "value") else definition.data_type
    code = definition.parameter_code
    if data_type == DataType.NUMBER.value:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise CurationError(f"value for {code} must be a finite JSON number")
    elif data_type in {DataType.TEXT.value, DataType.ENUM.value}:
        if not isinstance(value, str):
            raise CurationError(f"value for {code} must be a JSON string")
    elif data_type == DataType.BOOLEAN.value:
        if type(value) is not bool:
            raise CurationError(f"value for {code} must be a JSON boolean")
    elif data_type == DataType.JSON.value:
        if not isinstance(value, (dict, list)):
            raise CurationError(f"value for {code} must be a JSON object or array")
    else:
        raise CurationError(f"parameter {code} uses unsupported registry data type {data_type}")


def validate_manifest(
    session: Session,
    document: Mapping[str, Any] | CurationManifest,
) -> ManifestValidation:
    manifest = parse_manifest(document)

    existing_vehicle = session.scalar(
        select(VehicleConfiguration).where(
            VehicleConfiguration.stable_vehicle_code == manifest.vehicle.stable_vehicle_code
        )
    )
    if existing_vehicle is not None:
        raise CurationError(
            f"stable_vehicle_code {manifest.vehicle.stable_vehicle_code} already exists; CREATE_ONLY refuses to update or merge it"
        )

    parameter_codes = {value.parameter_code for value in manifest.values}
    parameter_codes.update(assessment.parameter_code for assessment in manifest.assessments)
    parameter_codes.update(decision.parameter_code for decision in manifest.conflict_decisions)
    definitions = {
        definition.parameter_code: definition
        for definition in session.scalars(
            select(ParameterDefinition).where(ParameterDefinition.parameter_code.in_(parameter_codes))
        ).all()
    }
    missing = sorted(parameter_codes - definitions.keys())
    if missing:
        raise CurationError(f"parameter registry does not define: {', '.join(missing)}")

    _validate_existing_manufacturer_model(session, manifest)

    for value in manifest.values:
        definition = definitions[value.parameter_code]
        _validate_manifest_value_type(value.value, definition)
        if value.canonical_unit != definition.canonical_unit:
            raise CurationError(
                f"value {value.value_code} unit {value.canonical_unit!r} does not match registry unit {definition.canonical_unit!r} for {value.parameter_code}"
            )
        for attribute in definition.requires_attributes or []:
            if attribute == "load_condition" and value.load_condition_code is None:
                raise CurationError(f"value {value.value_code} requires a load_condition_code")
            if attribute != "load_condition" and not (value.semantic_metadata or {}).get(attribute):
                raise CurationError(f"value {value.value_code} requires semantic metadata {attribute}")

    existing_sources: dict[str, SourceDocument] = {}
    for source in manifest.sources:
        existing = session.scalar(select(SourceDocument).where(SourceDocument.source_code == source.source_code))
        if existing is not None:
            _validate_existing_source(source, existing)
            existing_sources[source.source_code] = existing

    return ManifestValidation(
        manifest=manifest,
        parameter_definitions=definitions,
        existing_sources=existing_sources,
    )
