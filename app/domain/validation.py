from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import atan, degrees
from typing import Any

from app.domain.enums import (
    ApplicabilityGrade,
    AvailabilityState,
    ClearanceType,
    DataType,
    EvidenceMethod,
    GeometryRole,
    LinkageType,
    PhaseBehavior,
    ResolutionState,
    TrackDefinition,
    TurningAxleScope,
    TurningRadiusOrDiameter,
    TurningReference,
    VerificationState,
    WallEnvelopeScope,
)


class ContractViolation(ValueError):
    """Raised when an accepted evidence/data contract would be violated."""


TYPED_FIELDS = ("numeric_value", "text_value", "boolean_value", "enum_value", "json_value")
SCREENING_PARAMETER_PREFIX = "screening_"
OEM_RAMP_PARAMETER_PREFIX = "oem_published_"
PHYSICAL_RAMP_PARAMETER_PREFIX = "geometry_derived_"
STATIC_LOADED_TYRE_RADIUS_CODES = {
    "static_loaded_tyre_radius_front_mm",
    "static_loaded_tyre_radius_rear_mm",
}


def typed_value_count(value: Any) -> int:
    return sum(getattr(value, field, None) is not None for field in TYPED_FIELDS)


def enum_text(value: Any) -> Any:
    return getattr(value, "value", value)


def _present(value: Any) -> bool:
    value = enum_text(value)
    return value is not None and (not isinstance(value, str) or bool(value.strip()))


def validate_typed_value_shape(parameter_definition: Any, value: Any) -> None:
    """Validate the typed value and orthogonal availability state together."""

    count = typed_value_count(value)
    availability = getattr(value, "availability_state", None)
    availability_text = getattr(availability, "value", availability)
    if availability_text == AvailabilityState.AVAILABLE.value:
        if count != 1:
            raise ContractViolation("AVAILABLE normalized values require exactly one typed value")
        if enum_text(getattr(value, "evidence_method", None)) == EvidenceMethod.NONE.value:
            raise ContractViolation("AVAILABLE normalized values require evidence or derivation provenance")
    elif count:
        raise ContractViolation("UNKNOWN/NOT_FOUND/NOT_APPLICABLE values cannot carry typed values")

    data_type = getattr(parameter_definition, "data_type", None)
    data_type_text = getattr(data_type, "value", data_type)
    expected_field = {
        DataType.NUMBER.value: "numeric_value",
        DataType.TEXT.value: "text_value",
        DataType.BOOLEAN.value: "boolean_value",
        DataType.ENUM.value: "enum_value",
        DataType.JSON.value: "json_value",
    }.get(data_type_text)
    if availability_text == AvailabilityState.AVAILABLE.value and expected_field and getattr(value, expected_field, None) is None:
        raise ContractViolation(f"parameter {parameter_definition.parameter_code} requires {expected_field}")
    if availability_text == AvailabilityState.AVAILABLE.value and expected_field:
        wrong_fields = [field for field in TYPED_FIELDS if field != expected_field and getattr(value, field, None) is not None]
        if wrong_fields:
            raise ContractViolation(f"parameter {parameter_definition.parameter_code} has a value in the wrong typed field")


def validate_registered_semantics(parameter_definition: Any, value: Any) -> None:
    """Apply the registry-declared semantic requirements at the write boundary."""

    metadata = getattr(value, "semantic_metadata", None) or {}
    missing: list[str] = []
    for attribute in getattr(parameter_definition, "requires_attributes", None) or []:
        if attribute == "load_condition":
            if not _present(getattr(value, "load_condition_id", None)):
                missing.append("load_condition_id")
        elif not _present(metadata.get(attribute)):
            missing.append(attribute)
    if missing:
        raise ContractViolation(
            f"{parameter_definition.parameter_code} requires registered semantic attributes: {', '.join(missing)}"
        )

    parameter_code = parameter_definition.parameter_code
    if parameter_code == "turning_radius_normalized_m":
        validate_turning_metadata(metadata)
    elif parameter_code == "clearance_value_mm":
        validate_clearance_metadata(metadata)
    elif parameter_code in STATIC_LOADED_TYRE_RADIUS_CODES:
        if enum_text(metadata.get("radius_kind")) not in {None, "STATIC_LOADED"}:
            raise ContractViolation(
                f"{parameter_code} cannot use nominal or unloaded tyre-radius semantics"
            )


def validate_clearance_metadata(metadata: Mapping[str, Any] | None) -> None:
    metadata = metadata or {}
    clearance_type = enum_text(metadata.get("clearance_type"))
    if clearance_type not in {item.value for item in ClearanceType}:
        raise ContractViolation("clearance values require a controlled clearance_type")


def validate_estimation_metadata(metadata: Mapping[str, Any] | None) -> None:
    metadata = metadata or {}
    missing = [key for key in ("estimation_method", "limitations") if not _present(metadata.get(key))]
    if missing:
        raise ContractViolation(f"ESTIMATED values require explicit metadata: {', '.join(missing)}")


def validate_provenance_payload(
    payload: Any,
    *,
    evidence_links: Sequence[Any] | None,
    derivation_rule: Any | None,
    derivation_inputs: Sequence[Any] | None,
) -> None:
    """Validate provenance before a normalized value is inserted."""

    method = enum_text(getattr(payload, "evidence_method", None))
    availability = enum_text(getattr(payload, "availability_state", None))
    links = list(evidence_links or [])
    inputs = list(derivation_inputs or [])
    if availability == AvailabilityState.AVAILABLE.value and method == EvidenceMethod.NONE.value:
        raise ContractViolation("AVAILABLE normalized values require evidence or derivation provenance")
    if method in {EvidenceMethod.PUBLISHED.value, EvidenceMethod.MEASURED.value} and not links:
        raise ContractViolation(f"{method} values require at least one source observation link")
    if method == EvidenceMethod.DERIVED.value:
        if derivation_rule is None:
            raise ContractViolation("DERIVED values must be created with a derivation rule and input lineage")
        if not inputs:
            raise ContractViolation("DERIVED values require at least one derivation input")
    if method == EvidenceMethod.ESTIMATED.value:
        if not links and not (derivation_rule is not None and inputs):
            raise ContractViolation("ESTIMATED values require source evidence or controlled derivation lineage")
        validate_estimation_metadata(getattr(payload, "semantic_metadata", None))
    if derivation_rule is not None and not inputs:
        raise ContractViolation("a derivation rule requires input lineage")
    if inputs and derivation_rule is None:
        raise ContractViolation("derivation inputs require a derivation rule")


def validate_persisted_value_contract(session: Any, value: Any) -> None:
    """Validate cross-table invariants after a normalized value has been assembled."""

    validate_typed_value_shape(value.parameter_definition, value)
    validate_registered_semantics(value.parameter_definition, value)
    derivation_rule_code = None
    if value.derivation_run is not None and value.derivation_run.derivation_rule is not None:
        derivation_rule_code = value.derivation_run.derivation_rule.rule_code
    validate_ramp_namespace(
        value.parameter_definition.parameter_code,
        requested_class=(value.semantic_metadata or {}).get("ramp_result_class"),
        evidence_method=value.evidence_method,
        derivation_rule_code=derivation_rule_code,
    )
    method = enum_text(value.evidence_method)
    if method == EvidenceMethod.DERIVED.value:
        if not value.normalization_rule_version:
            raise ContractViolation("DERIVED values require a rule version")
        if value.derivation_run is None:
            raise ContractViolation("DERIVED values require a derivation run with output lineage")
        if not value.derivation_run.inputs:
            raise ContractViolation("DERIVED values require derivation input lineage")
    if method in {EvidenceMethod.PUBLISHED.value, EvidenceMethod.MEASURED.value} and not value.evidence_links:
        raise ContractViolation(f"{method} values require at least one source observation link")
    if method == EvidenceMethod.ESTIMATED.value:
        validate_estimation_metadata(value.semantic_metadata)
        if not value.evidence_links and (value.derivation_run is None or not value.derivation_run.inputs):
            raise ContractViolation("ESTIMATED values require source evidence or controlled derivation lineage")


def validate_parameter_assessment(assessment: Any) -> None:
    state = getattr(assessment.availability_state, "value", assessment.availability_state)
    if state == AvailabilityState.AVAILABLE.value:
        raise ContractViolation("AVAILABLE is not a valid parameter assessment state")
    if not assessment.unknown_reason or not assessment.unknown_reason.strip():
        raise ContractViolation("unknown/not-found assessments require a reason")


def validate_width_promotion(parameter_code: str, metadata: Mapping[str, Any] | None) -> None:
    """Prevent generic OEM width from becoming a body/mirror envelope silently."""

    if parameter_code not in {
        "overall_width_body_mm",
        "overall_width_including_mirrors_mm",
        "overall_width_mirrors_folded_mm",
    }:
        return
    definition = enum_text((metadata or {}).get("width_envelope_definition"))
    if definition is None:
        raise ContractViolation(f"{parameter_code} requires explicit width_envelope_definition metadata")
    expected = {
        "overall_width_body_mm": "BODY_EXCLUDING_MIRRORS",
        "overall_width_including_mirrors_mm": "INCLUDING_MIRRORS_OPEN",
        "overall_width_mirrors_folded_mm": "INCLUDING_MIRRORS_FOLDED",
    }[parameter_code]
    if definition != expected:
        raise ContractViolation(f"{parameter_code} cannot be populated from width semantics {definition}")


def validate_avt_track_candidate(parameter_code: str, metadata: Mapping[str, Any] | None, evidence_method: Any) -> None:
    """Validate an AVT track candidate without treating every candidate as AVT-ready."""

    if parameter_code not in {"avt_front_outer_face_track_mm", "avt_rear_outer_face_track_mm"}:
        return
    metadata = metadata or {}
    track_definition = enum_text(metadata.get("track_definition"))
    if track_definition != TrackDefinition.OUTER_TYRE_FACES.value:
        raise ContractViolation("AVT outer-face track requires explicit OUTER_TYRE_FACES semantics")
    method = getattr(evidence_method, "value", evidence_method)
    source_basis = enum_text(metadata.get("source_basis"))
    if source_basis == "CENTERLINE_PLUS_NOMINAL_WIDTH":
        if method != EvidenceMethod.ESTIMATED.value or not metadata.get("screening_only"):
            raise ContractViolation("centerline plus nominal-width track must remain an estimated screening result")
        return
    if source_basis not in {"DIRECT_OUTER_FACE_EVIDENCE", "MOUNTED_GEOMETRY"}:
        raise ContractViolation("AVT outer-face track requires direct outer-face or explicit mounted-geometry evidence")
    if metadata.get("screening_only"):
        raise ContractViolation("screening-only track estimates cannot be represented as an AVT-ready candidate")
    if method == EvidenceMethod.ESTIMATED.value:
        raise ContractViolation("estimated nominal-width track cannot be AVT-ready")
    if source_basis == "MOUNTED_GEOMETRY" and not metadata.get("mounted_geometry_explicit"):
        raise ContractViolation("mounted-geometry AVT track requires mounted_geometry_explicit=true")


def is_avt_track_ready(value: Any, *, conflict_resolution_id: str | None = None) -> tuple[bool, str | None]:
    if value is None:
        return False, "missing AVT outer-face track"
    if enum_text(value.availability_state) != AvailabilityState.AVAILABLE.value:
        return False, f"AVT track availability is {value.availability_state}"
    if enum_text(value.verification_state) == VerificationState.REJECTED.value:
        return False, "AVT track verification is REJECTED"
    if enum_text(value.resolution_state) == ResolutionState.SUPERSEDED.value:
        return False, "AVT track value is SUPERSEDED"
    if enum_text(value.resolution_state) in {ResolutionState.CONFLICTING.value, ResolutionState.PREFERRED_WITH_CONFLICT.value} and not conflict_resolution_id:
        return False, "unresolved AVT track conflict"
    metadata = value.semantic_metadata or {}
    if enum_text(metadata.get("track_definition")) != TrackDefinition.OUTER_TYRE_FACES.value:
        return False, "AVT track is not explicitly outer-face-to-outer-face"
    if metadata.get("screening_only"):
        return False, "AVT track is screening-only"
    if enum_text(metadata.get("source_basis")) not in {"DIRECT_OUTER_FACE_EVIDENCE", "MOUNTED_GEOMETRY"}:
        return False, "AVT track source basis is not direct or mounted geometry"
    if enum_text(metadata.get("source_basis")) == "MOUNTED_GEOMETRY" and not metadata.get("mounted_geometry_explicit"):
        return False, "mounted AVT track geometry is not explicit"
    if value.evidence_method == EvidenceMethod.ESTIMATED.value:
        return False, "estimated AVT track cannot satisfy AVT_READY"
    return True, None


def validate_turning_metadata(metadata: Mapping[str, Any] | None) -> None:
    metadata = metadata or {}
    reference = enum_text(metadata.get("turning_reference"))
    radius_or_diameter = enum_text(metadata.get("turning_radius_or_diameter"))
    axle_scope = enum_text(metadata.get("turning_axle_scope"))
    if radius_or_diameter not in {TurningRadiusOrDiameter.RADIUS.value, TurningRadiusOrDiameter.DIAMETER.value}:
        raise ContractViolation("turning normalization requires explicit RADIUS or DIAMETER semantics")
    if reference not in {
        TurningReference.CURB_TO_CURB.value,
        TurningReference.WALL_TO_WALL.value,
        TurningReference.WHEEL_PATH_OTHER.value,
        TurningReference.BODY_PATH_OTHER.value,
        TurningReference.OEM_UNSPECIFIED.value,
    }:
        raise ContractViolation("turning normalization requires a controlled reference value")
    if axle_scope not in {item.value for item in TurningAxleScope}:
        raise ContractViolation("turning normalization requires a controlled axle scope")
    if reference == TurningReference.WALL_TO_WALL.value:
        scope = enum_text(metadata.get("turning_wall_envelope_scope"))
        if scope not in {item.value for item in WallEnvelopeScope}:
            raise ContractViolation("wall-to-wall turning values require wall envelope scope")


def is_turning_avt_ready(value: Any, *, conflict_resolution_id: str | None = None) -> tuple[bool, str | None]:
    if value is None:
        return False, "missing normalized turning value"
    if enum_text(value.availability_state) != AvailabilityState.AVAILABLE.value:
        return False, f"turning value availability is {value.availability_state}"
    if enum_text(value.verification_state) == VerificationState.REJECTED.value:
        return False, "turning value verification is REJECTED"
    if enum_text(value.resolution_state) == ResolutionState.SUPERSEDED.value:
        return False, "turning value is SUPERSEDED"
    metadata = value.semantic_metadata or {}
    if enum_text(metadata.get("turning_radius_or_diameter")) != TurningRadiusOrDiameter.RADIUS.value:
        return False, "AVT mapping requires normalized radius semantics"
    reference = enum_text(metadata.get("turning_reference"))
    if reference not in {TurningReference.CURB_TO_CURB.value, TurningReference.WALL_TO_WALL.value}:
        return False, "turning curb/wall reference is unresolved"
    if enum_text(metadata.get("turning_axle_scope")) not in {TurningAxleScope.ALL_AXLES.value, TurningAxleScope.ACTIVE_AXLES.value}:
        return False, "turning axle scope is unresolved"
    if reference == TurningReference.WALL_TO_WALL.value and enum_text(metadata.get("turning_wall_envelope_scope")) not in {
        "BODY_ONLY",
        "BODY_AND_LOADS",
    }:
        return False, "wall envelope scope is unresolved"
    if enum_text(value.resolution_state) in {ResolutionState.CONFLICTING.value, ResolutionState.PREFERRED_WITH_CONFLICT.value} and not conflict_resolution_id:
        return False, "unresolved turning conflict"
    return True, None


def normalize_turning_radius(value: float, radius_or_diameter: TurningRadiusOrDiameter | str) -> float:
    semantics = getattr(radius_or_diameter, "value", radius_or_diameter)
    if semantics == TurningRadiusOrDiameter.RADIUS.value:
        return value
    if semantics == TurningRadiusOrDiameter.DIAMETER.value:
        return value / 2
    raise ContractViolation("cannot convert turning value without explicit radius/diameter semantics")


def validate_secondary_steering(relation: Any) -> None:
    role = getattr(relation.steering_role, "value", relation.steering_role)
    if role not in {"SECONDARY", "LINKED"}:
        return
    linkage = getattr(relation.linkage_type, "value", relation.linkage_type)
    phase = getattr(relation.phase_behavior, "value", relation.phase_behavior)
    if not linkage or not phase:
        raise ContractViolation("secondary/rear steering requires explicit linkage and phase fields")


def rear_steering_mapping_ready(relations: Sequence[Any], rear_axles: Sequence[Any]) -> tuple[bool, str | None]:
    steered_rear_ids = {axle.id for axle in rear_axles if axle.steered is True}
    if not steered_rear_ids:
        return True, None
    rear_relations = [relation for relation in relations if relation.axle_id in steered_rear_ids]
    if not rear_relations:
        return False, "rear-steered axle has no steering relation"
    for relation in rear_relations:
        linkage = getattr(relation.linkage_type, "value", relation.linkage_type)
        phase = getattr(relation.phase_behavior, "value", relation.phase_behavior)
        if linkage == LinkageType.UNKNOWN.value or phase == PhaseBehavior.UNKNOWN.value:
            return False, "rear-steering linkage/phase behaviour is unknown"
        if relation.max_steering_angle_deg is None and relation.angle_ratio is None and not relation.relation_function:
            return False, "rear-steering angle/function is missing"
    return True, None


def validate_ramp_namespace(
    parameter_code: str,
    *,
    requested_class: str | None = None,
    evidence_method: Any | None = None,
    derivation_rule_code: str | None = None,
) -> None:
    """Keep screening, OEM-published, and geometry-derived ramp results disjoint."""

    screening_codes = {
        "screening_front_contact_angle_deg",
        "screening_rear_contact_angle_deg",
        "screening_breakover_angle_deg",
        "screening_breakover_symmetric_angle_deg",
    }
    method = getattr(evidence_method, "value", evidence_method)
    is_screening_derivation = bool(derivation_rule_code and derivation_rule_code.startswith("ramp_screening"))
    if parameter_code.startswith(PHYSICAL_RAMP_PARAMETER_PREFIX):
        raise ContractViolation(
            "Phase 0 rejects geometry-derived physical ramp angles until a dedicated physical-geometry validator exists"
        )
    if parameter_code in screening_codes:
        if requested_class != "SCREENING" or method != EvidenceMethod.DERIVED.value:
            raise ContractViolation("screening angle values require SCREENING metadata and DERIVED evidence")
        return
    if is_screening_derivation or requested_class == "SCREENING":
        if parameter_code.startswith(OEM_RAMP_PARAMETER_PREFIX):
            raise ContractViolation("screening result cannot populate OEM-published ramp namespace")
        if parameter_code.startswith(PHYSICAL_RAMP_PARAMETER_PREFIX):
            raise ContractViolation("screening result cannot populate geometry-derived physical ramp namespace")
    if parameter_code.startswith(OEM_RAMP_PARAMETER_PREFIX) and requested_class == "SCREENING":
        raise ContractViolation("screening result cannot populate OEM-published ramp namespace")
    if parameter_code.startswith(PHYSICAL_RAMP_PARAMETER_PREFIX) and requested_class == "SCREENING":
        raise ContractViolation("screening result cannot populate geometry-derived physical ramp namespace")


def validate_geometry_asset_role(role: Any, coordinate_system_version: str, geometry_fidelity: Any) -> None:
    role_text = getattr(role, "value", role)
    if not role_text:
        raise ContractViolation("geometry role is required")
    if not coordinate_system_version:
        raise ContractViolation("normalized geometry requires a coordinate-system/datum version")
    if not geometry_fidelity:
        raise ContractViolation("geometry fidelity is required")


def screening_breakover_symmetric_angle_deg(clearance_mm: float, wheelbase_mm: float) -> float:
    if clearance_mm <= 0 or wheelbase_mm <= 0:
        raise ContractViolation("screening breakover inputs must be positive")
    return degrees(2 * atan(2 * clearance_mm / wheelbase_mm))
