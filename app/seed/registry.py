from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import PROJECT_ROOT
from app.db.models import ParameterDefinition
from app.domain.enums import DataType
from app.domain.validation import ContractViolation


FORBIDDEN_AMBIGUOUS_CODES = {
    "track_mm",
    "width_mm",
    "turning_radius_m",
    "ground_clearance_mm",
    "steering_angle_deg",
    "breakover_angle_deg",
}


class RegistryEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: str = Field(min_length=1)
    family: str = Field(min_length=1)
    data_type: DataType
    unit: str | None = None
    requires_attributes: list[str] | None = None


class RegistryDocument(BaseModel):
    registry_version: str = Field(min_length=1)
    canonical_units: dict[str, str]
    parameters: list[RegistryEntry] = Field(min_length=1)
    forbidden_ambiguous_codes: list[str] = Field(default_factory=list)


DISPLAY_NAMES = {
    "oem_front_tread_or_track_mm": "OEM front tread/track",
    "oem_rear_tread_or_track_mm": "OEM rear tread/track",
    "avt_front_outer_face_track_mm": "AVT front outer-face tyre track",
    "avt_rear_outer_face_track_mm": "AVT rear outer-face tyre track",
    "turning_radius_normalized_m": "Normalized turning radius",
    "oem_turning_value_text": "OEM turning value (raw display)",
    "steering_wheel_lock_to_lock_turns": "Steering-wheel lock-to-lock turns",
    "maximum_inner_road_wheel_angle_deg": "Maximum inner road-wheel angle",
    "maximum_outer_road_wheel_angle_deg": "Maximum outer road-wheel angle",
    "virtual_center_steering_angle_deg": "Virtual-centre steering angle",
    "avt_maximum_steering_angle_deg": "AVT Maximum Steering Angle",
    "avt_lock_to_lock_time_forward_s": "AVT forward lock-to-lock time",
    "avt_lock_to_lock_time_reverse_s": "AVT reverse lock-to-lock time",
    "clearance_value_mm": "Clearance value",
    "screening_front_contact_angle_deg": "Screening front contact angle",
    "screening_rear_contact_angle_deg": "Screening rear contact angle",
    "screening_breakover_angle_deg": "Screening breakover angle",
    "screening_breakover_symmetric_angle_deg": "Screening symmetric breakover angle",
    "geometry_derived_approach_angle_deg": "Geometry-derived approach angle",
    "geometry_derived_departure_angle_deg": "Geometry-derived departure angle",
    "geometry_derived_breakover_angle_deg": "Geometry-derived breakover angle",
    "oem_published_approach_angle_deg": "OEM-published approach angle",
    "oem_published_departure_angle_deg": "OEM-published departure angle",
    "oem_published_breakover_angle_deg": "OEM-published breakover angle",
}


def _default_registry_path() -> Path:
    return PROJECT_ROOT / "data" / "reference" / "parameter_registry_v1.json"


def load_registry(path: Path | None = None) -> RegistryDocument:
    registry_path = path or _default_registry_path()
    document = RegistryDocument.model_validate_json(registry_path.read_text(encoding="utf-8"))
    codes = [entry.code for entry in document.parameters]
    if len(codes) != len(set(codes)):
        raise ContractViolation("parameter registry contains duplicate parameter codes")
    forbidden = FORBIDDEN_AMBIGUOUS_CODES | set(document.forbidden_ambiguous_codes)
    invalid = sorted(set(codes) & forbidden)
    if invalid:
        raise ContractViolation(f"parameter registry contains forbidden ambiguous codes: {', '.join(invalid)}")
    return document


def display_name_for(code: str) -> str:
    if code in DISPLAY_NAMES:
        return DISPLAY_NAMES[code]
    return code.replace("_", " ").capitalize()


def semantic_definition_for(entry: RegistryEntry) -> str:
    definitions = {
        "overall_width_reported_mm": "Width exactly as reported before mirror/envelope semantics are resolved.",
        "overall_width_body_mm": "Body envelope width excluding mirrors, only with explicit body-only semantics.",
        "overall_width_including_mirrors_mm": "Width including mirrors in the normal/open state.",
        "overall_width_mirrors_folded_mm": "Width including mirrors in the folded state.",
        "oem_front_tread_or_track_mm": "OEM-reported front tread/track; not AVT outer-face track unless semantics match.",
        "oem_rear_tread_or_track_mm": "OEM-reported rear tread/track; not AVT outer-face track unless semantics match.",
        "avt_front_outer_face_track_mm": "Distance between outer faces of the outermost front tyres under AVT semantics.",
        "avt_rear_outer_face_track_mm": "Distance between outer faces of the outermost rear tyres under AVT semantics.",
        "clearance_value_mm": "A clearance value that must carry clearance type and load-condition metadata.",
        "turning_radius_normalized_m": "Turning radius after explicit radius/diameter normalization; reference semantics remain metadata.",
    }
    return definitions.get(entry.code, f"Controlled {entry.family} parameter {entry.code}.")


def seed_registry(session: Session, path: Path | None = None) -> dict[str, ParameterDefinition]:
    document = load_registry(path)
    result: dict[str, ParameterDefinition] = {}
    existing = {row.parameter_code: row for row in session.scalars(select(ParameterDefinition)).all()}
    for entry in document.parameters:
        definition = existing.get(entry.code)
        if definition is None:
            definition = ParameterDefinition(
                parameter_code=entry.code,
                display_name=display_name_for(entry.code),
                family=entry.family,
                data_type=entry.data_type.value,
                canonical_unit=entry.unit,
                semantic_definition=semantic_definition_for(entry),
                applicability_notes="Registry v1.0.0; retain source/configuration applicability separately.",
                requires_attributes=entry.requires_attributes,
                created_version=document.registry_version,
            )
            session.add(definition)
        result[entry.code] = definition
    session.flush()
    return result
