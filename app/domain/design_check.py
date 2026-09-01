from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Any, Iterable, Mapping, Sequence

from app.domain.enums import (
    ApplicabilityGrade,
    AvailabilityState,
    EvidenceMethod,
    ResolutionState,
    TurningAxleScope,
    TurningRadiusOrDiameter,
    TurningReference,
    VerificationState,
    WallEnvelopeScope,
    WidthEnvelopeDefinition,
)


METHOD_ID = "DESIGN_CHECK_V1"

HEIGHT_CONSTRAINT = "height"
WIDTH_CONSTRAINT = "width"
LENGTH_CONSTRAINT = "length"
TURNING_CONSTRAINT = "turning"
WIDTH_PARAMETER_BY_ENVELOPE = {
    WidthEnvelopeDefinition.BODY_EXCLUDING_MIRRORS.value: "overall_width_body_mm",
    WidthEnvelopeDefinition.INCLUDING_MIRRORS_OPEN.value: "overall_width_including_mirrors_mm",
    WidthEnvelopeDefinition.INCLUDING_MIRRORS_FOLDED.value: "overall_width_mirrors_folded_mm",
    WidthEnvelopeDefinition.OEM_UNSPECIFIED.value: "overall_width_reported_mm",
}
WIDTH_LABELS = {
    WidthEnvelopeDefinition.BODY_EXCLUDING_MIRRORS.value: "Body excluding mirrors",
    WidthEnvelopeDefinition.INCLUDING_MIRRORS_OPEN.value: "Mirrors open",
    WidthEnvelopeDefinition.INCLUDING_MIRRORS_FOLDED.value: "Mirrors folded",
    WidthEnvelopeDefinition.OEM_UNSPECIFIED.value: "OEM-reported / unspecified (screening only)",
}
TURNING_SHAPE_LABELS = {
    TurningRadiusOrDiameter.RADIUS.value: "Radius",
    TurningRadiusOrDiameter.DIAMETER.value: "Diameter",
}
TURNING_REFERENCE_LABELS = {
    TurningReference.CURB_TO_CURB.value: "Curb-to-curb",
    TurningReference.WALL_TO_WALL.value: "Wall-to-wall",
}
SEMANTIC_LABELS_BY_KEY = {
    "width_envelope_definition": {
        WidthEnvelopeDefinition.BODY_EXCLUDING_MIRRORS.value: "Body excluding mirrors",
        WidthEnvelopeDefinition.INCLUDING_MIRRORS_OPEN.value: "Mirrors open",
        WidthEnvelopeDefinition.INCLUDING_MIRRORS_FOLDED.value: "Mirrors folded",
        WidthEnvelopeDefinition.BODY_AND_FIXED_APPENDAGES.value: "Body and fixed appendages",
        WidthEnvelopeDefinition.OEM_UNSPECIFIED.value: "OEM definition unspecified",
    },
    "turning_radius_or_diameter": {
        TurningRadiusOrDiameter.RADIUS.value: "Radius",
        TurningRadiusOrDiameter.DIAMETER.value: "Diameter",
        TurningRadiusOrDiameter.OEM_UNSPECIFIED.value: "OEM shape unspecified",
    },
    "turning_reference": {
        TurningReference.CURB_TO_CURB.value: "Curb-to-curb",
        TurningReference.WALL_TO_WALL.value: "Wall-to-wall",
        TurningReference.WHEEL_PATH_OTHER.value: "Other wheel path",
        TurningReference.BODY_PATH_OTHER.value: "Other body path",
        TurningReference.OEM_UNSPECIFIED.value: "OEM reference unspecified",
    },
    "turning_axle_scope": {
        TurningAxleScope.ALL_AXLES.value: "All axles",
        TurningAxleScope.ACTIVE_AXLES.value: "Active axles",
        TurningAxleScope.OEM_UNSPECIFIED.value: "OEM axle scope unspecified",
    },
    "turning_wall_envelope_scope": {
        WallEnvelopeScope.BODY_ONLY.value: "Body only",
        WallEnvelopeScope.BODY_AND_LOADS.value: "Body and loads",
        WallEnvelopeScope.OEM_UNSPECIFIED.value: "OEM wall envelope unspecified",
        WallEnvelopeScope.NOT_APPLICABLE.value: "Not applicable",
    },
}
SEMANTIC_KEY_LABELS = {
    "width_envelope_definition": "Recorded width envelope",
    "turning_radius_or_diameter": "Recorded turning shape",
    "turning_reference": "Recorded turning reference",
    "turning_axle_scope": "Recorded axle scope",
    "turning_wall_envelope_scope": "Recorded wall envelope",
    "source_qualifier": "Source qualifier",
}
CONFLICT_STATES = {
    ResolutionState.CONFLICTING.value,
    ResolutionState.PREFERRED_WITH_CONFLICT.value,
}
SKIPPABLE_RESOLUTION_STATES = {
    ResolutionState.SUPERSEDED.value,
    ResolutionState.NOT_APPLICABLE.value,
}
ALLOWED_APPLICABILITY = {
    ApplicabilityGrade.EXACT_CONFIGURATION.value,
    ApplicabilityGrade.SAME_GEOMETRY_CONFIRMED.value,
}
ALLOWED_EVIDENCE_METHODS = {
    EvidenceMethod.PUBLISHED.value,
    EvidenceMethod.MEASURED.value,
    EvidenceMethod.DERIVED.value,
}


class DesignCheckState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INDETERMINATE = "INDETERMINATE"


def _text(value: Any) -> str | None:
    if value is None:
        return None
    return value.value if isinstance(value, Enum) else str(value)


def _finite_number(name: str, value: float | int | None, *, positive: bool = False) -> None:
    if value is None:
        return
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not isfinite(numeric):
        raise ValueError(f"{name} must be finite")
    if numeric < 0 or (positive and numeric <= 0):
        qualifier = "greater than zero" if positive else "non-negative"
        raise ValueError(f"{name} must be {qualifier}")


@dataclass(frozen=True, slots=True)
class DesignCheckInputs:
    """Explicit user-entered limits. None means that constraint is inactive."""

    available_clear_height_mm: float | None = None
    vertical_allowance_mm: float = 0.0
    available_clear_width_mm: float | None = None
    lateral_allowance_each_side_mm: float | None = None
    width_envelope: str | None = None
    maximum_vehicle_length_mm: float | None = None
    maximum_turning_value_m: float | None = None
    turning_input_shape: str | None = None
    turning_reference: str | None = None

    def __post_init__(self) -> None:
        _finite_number("available_clear_height_mm", self.available_clear_height_mm, positive=True)
        _finite_number("vertical_allowance_mm", self.vertical_allowance_mm)
        _finite_number("available_clear_width_mm", self.available_clear_width_mm, positive=True)
        _finite_number("lateral_allowance_each_side_mm", self.lateral_allowance_each_side_mm)
        _finite_number("maximum_vehicle_length_mm", self.maximum_vehicle_length_mm, positive=True)
        _finite_number("maximum_turning_value_m", self.maximum_turning_value_m, positive=True)

        width_limit = self.available_clear_width_mm
        if width_limit is not None:
            envelope = _text(self.width_envelope)
            if envelope not in WIDTH_PARAMETER_BY_ENVELOPE:
                raise ValueError("width_envelope is required when a width limit is active")
            if self.lateral_allowance_each_side_mm is None:
                raise ValueError("lateral_allowance_each_side_mm is required when a width limit is active")

        turning_limit = self.maximum_turning_value_m
        if turning_limit is not None:
            if _text(self.turning_input_shape) not in {
                TurningRadiusOrDiameter.RADIUS.value,
                TurningRadiusOrDiameter.DIAMETER.value,
            }:
                raise ValueError("turning_input_shape must be RADIUS or DIAMETER when a turning limit is active")
            if _text(self.turning_reference) not in {
                TurningReference.CURB_TO_CURB.value,
                TurningReference.WALL_TO_WALL.value,
            }:
                raise ValueError("turning_reference must be CURB_TO_CURB or WALL_TO_WALL when a turning limit is active")

    @property
    def active_constraint_codes(self) -> tuple[str, ...]:
        active: list[str] = []
        if self.available_clear_height_mm is not None:
            active.append(HEIGHT_CONSTRAINT)
        if self.available_clear_width_mm is not None:
            active.append(WIDTH_CONSTRAINT)
        if self.maximum_vehicle_length_mm is not None:
            active.append(LENGTH_CONSTRAINT)
        if self.maximum_turning_value_m is not None:
            active.append(TURNING_CONSTRAINT)
        return tuple(active)


@dataclass(frozen=True, slots=True)
class ParameterCandidate:
    """Evidence-aware value snapshot consumed by the pure evaluator."""

    parameter_code: str
    value: float | int | str | None
    unit: str | None
    value_id: str | None = None
    semantic_metadata: Mapping[str, Any] = field(default_factory=dict)
    scope_text: str = "Configuration-wide"
    evidence_method: str | None = EvidenceMethod.PUBLISHED.value
    resolution_state: str = ResolutionState.UNCONTESTED.value
    verification_state: str = VerificationState.REVIEWED.value
    availability_state: str = AvailabilityState.AVAILABLE.value
    applicability_grade: str | None = ApplicabilityGrade.EXACT_CONFIGURATION.value
    evidence_link_count: int = 1
    normalization_rule_version: str | None = None
    lineage_intact: bool = True
    preferred: bool = False
    conflict_decision_id: str | None = None
    detail_url: str | None = None


@dataclass(frozen=True, slots=True)
class ParameterAssessmentRecord:
    parameter_code: str
    availability_state: str
    unknown_reason: str
    scope_text: str = "Configuration-wide"


@dataclass(frozen=True, slots=True)
class DesignVehicle:
    stable_vehicle_code: str
    manufacturer: str
    commercial_model: str
    variant: str
    generation: str = ""
    identity_time_label: str = ""
    body_style: str = ""
    powertrain: str | None = None
    detail_url: str | None = None
    values: tuple[ParameterCandidate, ...] = ()
    assessments: tuple[ParameterAssessmentRecord, ...] = ()

    @property
    def display_label(self) -> str:
        return f"{self.manufacturer} · {self.commercial_model}"


@dataclass(frozen=True, slots=True)
class CandidateResolution:
    candidate: ParameterCandidate | None
    reason: str


@dataclass(frozen=True, slots=True)
class ConstraintResult:
    code: str
    label: str
    state: DesignCheckState
    parameter_code: str
    requested_limit: float
    requested_unit: str
    allowance: float
    allowance_unit: str
    effective_limit: float
    effective_unit: str
    vehicle_value: float | None = None
    vehicle_unit: str | None = None
    margin: float | None = None
    margin_unit: str | None = None
    value_shape: str | None = None
    semantic_cue: str = ""
    scope_text: str = "Configuration-wide"
    reason: str = ""
    detail_url: str | None = None
    value_id: str | None = None
    evidence_state: str = ""
    utilization: float | None = None
    relative_exceedance: float | None = None


@dataclass(frozen=True, slots=True)
class VehicleDesignCheckResult:
    vehicle: DesignVehicle
    constraint_results: tuple[ConstraintResult, ...]
    overall_state: DesignCheckState | None
    closest_active_limit: ConstraintResult | None = None
    largest_exceedance: ConstraintResult | None = None
    decision_blockers: tuple[ConstraintResult, ...] = ()
    failed_constraints: tuple[ConstraintResult, ...] = ()

    @property
    def overall_reason(self) -> str:
        if self.overall_state is None:
            return "Enter at least one active constraint before calculating suitability."
        if self.overall_state == DesignCheckState.PASS:
            return "Every active constraint has passed."
        if self.overall_state == DesignCheckState.FAIL:
            return "At least one active constraint failed; all individual constraint results are retained."
        return "No active constraint failed, but one or more decision blockers prevent a suitability verdict."


@dataclass(frozen=True, slots=True)
class DesignCheckReport:
    method_id: str
    inputs: DesignCheckInputs
    vehicles: tuple[VehicleDesignCheckResult, ...]

    @property
    def result_counts(self) -> dict[str, int]:
        counts = {state.value: 0 for state in DesignCheckState}
        for result in self.vehicles:
            if result.overall_state is not None:
                counts[result.overall_state.value] += 1
        return counts

    @property
    def has_active_constraints(self) -> bool:
        return bool(self.inputs.active_constraint_codes)


def semantic_cue(metadata: Mapping[str, Any] | None) -> str:
    """Return a compact, deterministic display cue without changing semantics."""

    if not metadata:
        return ""
    parts: list[str] = []
    preferred_keys = (
        "width_envelope_definition",
        "turning_radius_or_diameter",
        "turning_reference",
        "turning_axle_scope",
        "turning_wall_envelope_scope",
        "source_qualifier",
    )
    for key in preferred_keys:
        if key not in metadata or metadata[key] is None:
            continue
        raw = str(metadata[key])
        value = SEMANTIC_LABELS_BY_KEY.get(key, {}).get(raw, raw.replace("_", " ").capitalize())
        label = SEMANTIC_KEY_LABELS.get(key)
        parts.append(f"{label}: {value}" if label else value)
    return " · ".join(parts)


def _format_number(value: float) -> str:
    if abs(value) < 1e-12:
        value = 0.0
    if value.is_integer():
        return str(int(value))
    return format(value, ".12g")


def _scope_suffix(candidate: ParameterCandidate) -> str:
    return f" ({candidate.scope_text})" if candidate.scope_text and candidate.scope_text != "Configuration-wide" else ""


def _assessment_reason(vehicle: DesignVehicle, parameter_code: str) -> str | None:
    assessments = [item for item in vehicle.assessments if item.parameter_code == parameter_code]
    if not assessments:
        return None
    assessment = assessments[0]
    scope = f" for {assessment.scope_text}" if assessment.scope_text != "Configuration-wide" else ""
    return f"{assessment.unknown_reason}{scope}"


def _scope_hint(vehicle: DesignVehicle, parameter_code: str) -> str:
    scopes = {
        item.scope_text
        for item in vehicle.values
        if item.parameter_code == parameter_code and item.scope_text
    }
    scopes.update(
        item.scope_text
        for item in vehicle.assessments
        if item.parameter_code == parameter_code and item.scope_text
    )
    if len(scopes) == 1:
        return next(iter(scopes))
    if len(scopes) > 1:
        return "Multiple scopes: " + ", ".join(sorted(scopes))
    return "Scope unresolved"


def _common_candidate_blockers(candidate: ParameterCandidate) -> list[str]:
    blockers: list[str] = []
    if candidate.availability_state != AvailabilityState.AVAILABLE.value:
        blockers.append(f"availability is {candidate.availability_state}")
    if candidate.verification_state == VerificationState.REJECTED.value:
        blockers.append("verification state is REJECTED")
    if candidate.applicability_grade not in ALLOWED_APPLICABILITY:
        blockers.append(f"applicability is {candidate.applicability_grade or 'not recorded'}")
    if candidate.evidence_method not in ALLOWED_EVIDENCE_METHODS:
        if candidate.evidence_method == EvidenceMethod.ESTIMATED.value:
            blockers.append("value is ESTIMATED and is not eligible for an automatic v1 verdict")
        else:
            blockers.append(f"evidence method is {candidate.evidence_method or 'not recorded'}")
    if candidate.evidence_method in {
        EvidenceMethod.PUBLISHED.value,
        EvidenceMethod.MEASURED.value,
    } and candidate.evidence_link_count < 1:
        blockers.append("no source evidence link is available")
    if candidate.evidence_method == EvidenceMethod.DERIVED.value and (
        not candidate.normalization_rule_version or not candidate.lineage_intact
    ):
        blockers.append("derived-value lineage is incomplete")
    if "scope unresolved" in candidate.scope_text.lower():
        blockers.append("fitment/load scope is unresolved")
    if candidate.value is None:
        blockers.append("typed numeric value is absent")
    return blockers


def resolve_parameter_candidate(vehicle: DesignVehicle, parameter_code: str) -> CandidateResolution:
    """Resolve one value without silently choosing a favourable scope or state."""

    matches = [item for item in vehicle.values if item.parameter_code == parameter_code]
    if not matches:
        assessed = _assessment_reason(vehicle, parameter_code)
        if assessed:
            return CandidateResolution(None, assessed)
        return CandidateResolution(None, f"{parameter_code} is unavailable for this exact configuration")

    ordinary: list[ParameterCandidate] = []
    selected_conflicts: list[ParameterCandidate] = []
    unresolved_conflicts: list[ParameterCandidate] = []
    blockers: list[str] = []

    for candidate in matches:
        if candidate.resolution_state in SKIPPABLE_RESOLUTION_STATES:
            continue
        candidate_blockers = _common_candidate_blockers(candidate)
        if candidate_blockers:
            blockers.extend(f"{parameter_code}{_scope_suffix(candidate)}: {item}" for item in candidate_blockers)
            continue
        if candidate.resolution_state in CONFLICT_STATES:
            if candidate.conflict_decision_id:
                selected_conflicts.append(candidate)
            else:
                unresolved_conflicts.append(candidate)
            continue
        ordinary.append(candidate)

    if blockers:
        return CandidateResolution(None, "; ".join(blockers))
    if len(selected_conflicts) > 1:
        return CandidateResolution(None, f"multiple active conflict selections exist for {parameter_code}")
    if unresolved_conflicts and not selected_conflicts:
        return CandidateResolution(None, f"conflicting {parameter_code} values have no active auditable selection")
    if selected_conflicts:
        return CandidateResolution(selected_conflicts[0], "active auditable conflict selection")
    if len(ordinary) == 1:
        return CandidateResolution(ordinary[0], "unique eligible value")
    if not ordinary:
        assessed = _assessment_reason(vehicle, parameter_code)
        return CandidateResolution(
            None,
            assessed or f"no eligible available value is recorded for {parameter_code}",
        )

    scopes = ", ".join(sorted({item.scope_text for item in ordinary}))
    if len({item.scope_text for item in ordinary}) > 1:
        return CandidateResolution(
            None,
            f"multiple applicable {parameter_code} values remain across scopes; scope/value is not uniquely selected ({scopes})",
        )

    return CandidateResolution(
        None,
        f"multiple applicable {parameter_code} values remain; no auditable selection is represented ({scopes})",
    )


def _numeric_candidate(
    vehicle: DesignVehicle,
    resolution: CandidateResolution,
    *,
    expected_unit: str,
    label: str,
    positive: bool = True,
) -> tuple[ParameterCandidate | None, float | None, str | None]:
    candidate = resolution.candidate
    if candidate is None:
        return None, None, resolution.reason
    if candidate.unit != expected_unit:
        return candidate, None, f"{label} unit is {candidate.unit or 'not recorded'}, not canonical {expected_unit}"
    if isinstance(candidate.value, bool):
        return candidate, None, f"{label} is not a numeric value"
    try:
        numeric = float(candidate.value)
    except (TypeError, ValueError):
        return candidate, None, f"{label} is not a numeric value"
    if not isfinite(numeric):
        return candidate, None, f"{label} is not finite"
    if positive and numeric <= 0:
        return candidate, None, f"{label} must be greater than zero"
    return candidate, numeric, None


def _relative_exceedance(value: float, limit: float) -> float | None:
    return (value - limit) / limit if limit > 0 else None


def _result(
    *,
    code: str,
    label: str,
    state: DesignCheckState,
    parameter_code: str,
    requested_limit: float,
    requested_unit: str,
    allowance: float,
    allowance_unit: str,
    effective_limit: float,
    effective_unit: str,
    candidate: ParameterCandidate | None = None,
    vehicle_value: float | None = None,
    vehicle_unit: str | None = None,
    margin: float | None = None,
    margin_unit: str | None = None,
    value_shape: str | None = None,
    semantic: str = "",
    reason: str = "",
    vehicle: DesignVehicle,
    utilization: float | None = None,
) -> ConstraintResult:
    return ConstraintResult(
        code=code,
        label=label,
        state=state,
        parameter_code=parameter_code,
        requested_limit=requested_limit,
        requested_unit=requested_unit,
        allowance=allowance,
        allowance_unit=allowance_unit,
        effective_limit=effective_limit,
        effective_unit=effective_unit,
        vehicle_value=vehicle_value,
        vehicle_unit=vehicle_unit,
        margin=margin,
        margin_unit=margin_unit,
        value_shape=value_shape,
        semantic_cue=semantic,
        scope_text=candidate.scope_text if candidate else _scope_hint(vehicle, parameter_code),
        reason=reason,
        detail_url=(candidate.detail_url if candidate and candidate.detail_url else vehicle.detail_url),
        value_id=candidate.value_id if candidate else None,
        evidence_state=(
            (
                "Selected conflict retained · "
                if candidate and candidate.conflict_decision_id
                else "Preferred candidate · "
                if candidate and candidate.preferred
                else ""
            )
            + (
                f"{candidate.evidence_method or 'Evidence method unknown'} · "
                f"{candidate.verification_state or 'Verification unknown'}"
                if candidate
                else ""
            )
        ),
        utilization=utilization,
        relative_exceedance=(
            _relative_exceedance(vehicle_value, effective_limit)
            if vehicle_value is not None
            else None
        ),
    )


def evaluate_height_constraint(vehicle: DesignVehicle, inputs: DesignCheckInputs) -> ConstraintResult:
    available = float(inputs.available_clear_height_mm)
    allowance = float(inputs.vertical_allowance_mm)
    effective = available - allowance
    resolution = resolve_parameter_candidate(vehicle, "overall_height_mm")
    candidate, value, blocker = _numeric_candidate(
        vehicle, resolution, expected_unit="mm", label="Overall height"
    )
    if blocker:
        reason = (
            blocker
            if resolution.candidate is not None
            else f"Overall height is unavailable: {blocker}"
        )
        return _result(
            code=HEIGHT_CONSTRAINT,
            label="Clear height",
            state=DesignCheckState.INDETERMINATE,
            parameter_code="overall_height_mm",
            requested_limit=available,
            requested_unit="mm",
            allowance=allowance,
            allowance_unit="mm",
            effective_limit=effective,
            effective_unit="mm",
            candidate=candidate,
            vehicle_value=value,
            vehicle_unit="mm" if value is not None else None,
            semantic=semantic_cue(candidate.semantic_metadata) if candidate else "",
            reason=reason,
            vehicle=vehicle,
        )
    assert candidate is not None and value is not None
    margin = effective - value
    state = DesignCheckState.PASS if margin >= 0 else DesignCheckState.FAIL
    if state == DesignCheckState.PASS:
        reason = (
            f"Overall height {_format_number(value)} mm is within the effective clear-height limit "
            f"{_format_number(effective)} mm ({_format_number(available)} mm minimum clear height "
            f"minus {_format_number(allowance)} mm vertical allowance)."
        )
    else:
        reason = (
            f"Overall height {_format_number(value)} mm exceeds the effective clear-height limit "
            f"{_format_number(effective)} mm by {_format_number(abs(margin))} mm."
        )
    return _result(
        code=HEIGHT_CONSTRAINT,
        label="Clear height",
        state=state,
        parameter_code="overall_height_mm",
        requested_limit=available,
        requested_unit="mm",
        allowance=allowance,
        allowance_unit="mm",
        effective_limit=effective,
        effective_unit="mm",
        candidate=candidate,
        vehicle_value=value,
        vehicle_unit="mm",
        margin=margin,
        margin_unit="mm",
        semantic=semantic_cue(candidate.semantic_metadata),
        reason=reason,
        vehicle=vehicle,
        utilization=value / effective if effective > 0 else None,
    )


def _width_missing_reason(vehicle: DesignVehicle, envelope: str, resolution: CandidateResolution) -> str:
    target_label = WIDTH_LABELS[envelope]
    target_parameter = WIDTH_PARAMETER_BY_ENVELOPE[envelope]
    if any(item.parameter_code == target_parameter for item in vehicle.values):
        return resolution.reason
    known: list[str] = []
    for candidate in vehicle.values:
        if not candidate.parameter_code.startswith("overall_width_"):
            continue
        if candidate.availability_state != AvailabilityState.AVAILABLE.value or candidate.value is None:
            continue
        recorded = candidate.semantic_metadata.get("width_envelope_definition")
        known.append(
            SEMANTIC_LABELS_BY_KEY["width_envelope_definition"].get(
                str(recorded), candidate.parameter_code
            )
        )
    if known:
        known_text = ", ".join(sorted(set(known)))
        return (
            f"{target_label} width is unavailable; recorded {known_text} definition(s) cannot be substituted."
        )
    assessed = _assessment_reason(vehicle, target_parameter)
    if assessed:
        return assessed
    return resolution.reason


def evaluate_width_constraint(vehicle: DesignVehicle, inputs: DesignCheckInputs) -> ConstraintResult:
    available = float(inputs.available_clear_width_mm)
    allowance = float(inputs.lateral_allowance_each_side_mm)
    effective = available - 2 * allowance
    envelope = _text(inputs.width_envelope)
    assert envelope is not None
    parameter_code = WIDTH_PARAMETER_BY_ENVELOPE[envelope]
    label = WIDTH_LABELS[envelope]
    resolution = resolve_parameter_candidate(vehicle, parameter_code)
    candidate, value, blocker = _numeric_candidate(
        vehicle, resolution, expected_unit="mm", label=f"{label} width"
    )
    if blocker:
        reason = _width_missing_reason(vehicle, envelope, resolution)
        if candidate is not None:
            reason = blocker
        return _result(
            code=WIDTH_CONSTRAINT,
            label="Width envelope",
            state=DesignCheckState.INDETERMINATE,
            parameter_code=parameter_code,
            requested_limit=available,
            requested_unit="mm",
            allowance=allowance,
            allowance_unit="mm each side",
            effective_limit=effective,
            effective_unit="mm",
            candidate=candidate,
            vehicle_value=value,
            vehicle_unit="mm" if value is not None else None,
            value_shape=envelope,
            semantic=semantic_cue(candidate.semantic_metadata) if candidate else "",
            reason=reason,
            vehicle=vehicle,
        )

    assert candidate is not None and value is not None
    recorded_definition = _text(candidate.semantic_metadata.get("width_envelope_definition"))
    if envelope != WidthEnvelopeDefinition.OEM_UNSPECIFIED.value and recorded_definition != envelope:
        reason = (
            f"Recorded width definition is {SEMANTIC_LABELS.get(recorded_definition or '', recorded_definition or 'not recorded')}; "
            f"requested {label} requires an exact envelope match."
        )
        return _result(
            code=WIDTH_CONSTRAINT,
            label="Width envelope",
            state=DesignCheckState.INDETERMINATE,
            parameter_code=parameter_code,
            requested_limit=available,
            requested_unit="mm",
            allowance=allowance,
            allowance_unit="mm each side",
            effective_limit=effective,
            effective_unit="mm",
            candidate=candidate,
            vehicle_value=value,
            vehicle_unit="mm",
            value_shape=envelope,
            semantic=semantic_cue(candidate.semantic_metadata),
            reason=reason,
            vehicle=vehicle,
        )
    if recorded_definition is None:
        reason = "Width envelope definition is not recorded; body, open-mirror and folded-mirror semantics are not interchangeable."
        return _result(
            code=WIDTH_CONSTRAINT,
            label="Width envelope",
            state=DesignCheckState.INDETERMINATE,
            parameter_code=parameter_code,
            requested_limit=available,
            requested_unit="mm",
            allowance=allowance,
            allowance_unit="mm each side",
            effective_limit=effective,
            effective_unit="mm",
            candidate=candidate,
            vehicle_value=value,
            vehicle_unit="mm",
            value_shape=envelope,
            semantic="",
            reason=reason,
            vehicle=vehicle,
        )

    margin = effective - value
    state = DesignCheckState.PASS if margin >= 0 else DesignCheckState.FAIL
    if state == DesignCheckState.PASS:
        reason = (
            f"{label} width {_format_number(value)} mm is within the effective width limit "
            f"{_format_number(effective)} mm after {_format_number(allowance)} mm lateral allowance per side."
        )
    else:
        reason = (
            f"{label} width {_format_number(value)} mm exceeds the effective width limit "
            f"{_format_number(effective)} mm by {_format_number(abs(margin))} mm."
        )
    if envelope == WidthEnvelopeDefinition.OEM_UNSPECIFIED.value:
        reason += " This is an explicitly labelled source-defined/unspecified width screening result."
    return _result(
        code=WIDTH_CONSTRAINT,
        label="Width envelope",
        state=state,
        parameter_code=parameter_code,
        requested_limit=available,
        requested_unit="mm",
        allowance=allowance,
        allowance_unit="mm each side",
        effective_limit=effective,
        effective_unit="mm",
        candidate=candidate,
        vehicle_value=value,
        vehicle_unit="mm",
        margin=margin,
        margin_unit="mm",
        value_shape=envelope,
        semantic=semantic_cue(candidate.semantic_metadata),
        reason=reason,
        vehicle=vehicle,
        utilization=value / effective if effective > 0 else None,
    )


def evaluate_length_constraint(vehicle: DesignVehicle, inputs: DesignCheckInputs) -> ConstraintResult:
    limit = float(inputs.maximum_vehicle_length_mm)
    resolution = resolve_parameter_candidate(vehicle, "overall_length_mm")
    candidate, value, blocker = _numeric_candidate(
        vehicle, resolution, expected_unit="mm", label="Overall length"
    )
    if blocker:
        reason = blocker if candidate is not None else f"Overall length is unavailable: {blocker}"
        return _result(
            code=LENGTH_CONSTRAINT,
            label="Overall length",
            state=DesignCheckState.INDETERMINATE,
            parameter_code="overall_length_mm",
            requested_limit=limit,
            requested_unit="mm",
            allowance=0,
            allowance_unit="mm",
            effective_limit=limit,
            effective_unit="mm",
            candidate=candidate,
            vehicle_value=value,
            vehicle_unit="mm" if value is not None else None,
            semantic=semantic_cue(candidate.semantic_metadata) if candidate else "",
            reason=reason,
            vehicle=vehicle,
        )
    assert candidate is not None and value is not None
    margin = limit - value
    state = DesignCheckState.PASS if margin >= 0 else DesignCheckState.FAIL
    if state == DesignCheckState.PASS:
        reason = f"Overall length {_format_number(value)} mm is within the maximum length limit {_format_number(limit)} mm."
    else:
        reason = f"Overall length {_format_number(value)} mm exceeds the maximum length limit {_format_number(limit)} mm by {_format_number(abs(margin))} mm."
    return _result(
        code=LENGTH_CONSTRAINT,
        label="Overall length",
        state=state,
        parameter_code="overall_length_mm",
        requested_limit=limit,
        requested_unit="mm",
        allowance=0,
        allowance_unit="mm",
        effective_limit=limit,
        effective_unit="mm",
        candidate=candidate,
        vehicle_value=value,
        vehicle_unit="mm",
        margin=margin,
        margin_unit="mm",
        semantic=semantic_cue(candidate.semantic_metadata),
        reason=reason,
        vehicle=vehicle,
        utilization=value / limit if limit > 0 else None,
    )


def _turning_missing_reason(vehicle: DesignVehicle, resolution: CandidateResolution) -> str:
    raw_turning_values = [
        item
        for item in vehicle.values
        if item.parameter_code == "oem_turning_value_text"
        and item.availability_state == AvailabilityState.AVAILABLE.value
        and item.value is not None
    ]
    if raw_turning_values and any(
        item.parameter_code == "oem_turning_value_text"
        and item.resolution_state in CONFLICT_STATES
        for item in vehicle.values
    ):
        return (
            "Conflicting raw OEM turning wording values are retained; normalized turning radius is unavailable and "
            "the wording is not parsed, halved, or otherwise converted by Design Check v1."
        )
    if raw_turning_values:
        return (
            "Normalized turning radius is unavailable; raw OEM turning wording is retained and is not parsed, halved, "
            "or otherwise converted by Design Check v1."
        )
    assessed = _assessment_reason(vehicle, "turning_radius_normalized_m")
    if assessed:
        return assessed
    return resolution.reason


def evaluate_turning_constraint(vehicle: DesignVehicle, inputs: DesignCheckInputs) -> ConstraintResult:
    limit_input = float(inputs.maximum_turning_value_m)
    input_shape = _text(inputs.turning_input_shape)
    reference = _text(inputs.turning_reference)
    site_radius = limit_input if input_shape == TurningRadiusOrDiameter.RADIUS.value else limit_input / 2
    resolution = resolve_parameter_candidate(vehicle, "turning_radius_normalized_m")
    candidate, vehicle_radius, blocker = _numeric_candidate(
        vehicle, resolution, expected_unit="m", label="Normalized turning radius"
    )
    display_value = vehicle_radius
    if input_shape == TurningRadiusOrDiameter.DIAMETER.value and vehicle_radius is not None:
        display_value = vehicle_radius * 2
    if blocker:
        reason = blocker if candidate is not None else _turning_missing_reason(vehicle, resolution)
        return _result(
            code=TURNING_CONSTRAINT,
            label="Turning-envelope screening",
            state=DesignCheckState.INDETERMINATE,
            parameter_code="turning_radius_normalized_m",
            requested_limit=limit_input,
            requested_unit="m",
            allowance=0,
            allowance_unit="m",
            effective_limit=limit_input,
            effective_unit="m",
            candidate=candidate,
            vehicle_value=display_value,
            vehicle_unit="m" if display_value is not None else None,
            value_shape=input_shape,
            semantic=semantic_cue(candidate.semantic_metadata) if candidate else "",
            reason=reason,
            vehicle=vehicle,
        )
    assert candidate is not None and vehicle_radius is not None
    metadata = candidate.semantic_metadata
    shape = _text(metadata.get("turning_radius_or_diameter"))
    recorded_reference = _text(metadata.get("turning_reference"))
    axle_scope = _text(metadata.get("turning_axle_scope"))
    wall_scope = _text(metadata.get("turning_wall_envelope_scope"))
    semantic = semantic_cue(metadata)
    if shape != TurningRadiusOrDiameter.RADIUS.value:
        reason = (
            "Vehicle turning candidate is not recorded as a normalized radius; radius/diameter semantics "
            "cannot be compared automatically."
        )
    elif recorded_reference != reference:
        reason = (
            f"Turning reference is {SEMANTIC_LABELS_BY_KEY['turning_reference'].get(recorded_reference or '', recorded_reference or 'not recorded')}; "
            f"requested {TURNING_REFERENCE_LABELS[reference]} requires an exact reference match."
        )
    elif reference == TurningReference.CURB_TO_CURB.value and axle_scope not in {
        TurningAxleScope.ALL_AXLES.value,
        TurningAxleScope.ACTIVE_AXLES.value,
    }:
        reason = "Curb-to-curb turning axle scope is unresolved; all-axles or active-axles semantics are required."
    elif reference == TurningReference.WALL_TO_WALL.value and wall_scope not in {
        WallEnvelopeScope.BODY_ONLY.value,
        WallEnvelopeScope.BODY_AND_LOADS.value,
    }:
        reason = "Wall-to-wall turning envelope scope is unresolved; body-only or body-and-loads semantics are required."
    else:
        reason = ""
    if reason:
        return _result(
            code=TURNING_CONSTRAINT,
            label="Turning-envelope screening",
            state=DesignCheckState.INDETERMINATE,
            parameter_code="turning_radius_normalized_m",
            requested_limit=limit_input,
            requested_unit="m",
            allowance=0,
            allowance_unit="m",
            effective_limit=limit_input,
            effective_unit="m",
            candidate=candidate,
            vehicle_value=display_value,
            vehicle_unit="m",
            value_shape=input_shape,
            semantic=semantic,
            reason=reason,
            vehicle=vehicle,
        )

    margin = site_radius - vehicle_radius
    display_margin = limit_input - display_value
    state = DesignCheckState.PASS if margin >= 0 else DesignCheckState.FAIL
    if input_shape == TurningRadiusOrDiameter.DIAMETER.value:
        vehicle_shape_text = f"equivalent diameter {_format_number(display_value)} m"
        margin_text = f"{_format_number(abs(display_margin))} m diameter"
    else:
        vehicle_shape_text = f"normalized radius {_format_number(vehicle_radius)} m"
        margin_text = f"{_format_number(abs(display_margin))} m radius"
    if state == DesignCheckState.PASS:
        reason = (
            f"{vehicle_shape_text} is within the maximum {TURNING_SHAPE_LABELS[input_shape].lower()} limit "
            f"{_format_number(limit_input)} m for {TURNING_REFERENCE_LABELS[reference]} ({margin_text} margin)."
        )
    else:
        reason = (
            f"{vehicle_shape_text} exceeds the maximum {TURNING_SHAPE_LABELS[input_shape].lower()} limit "
            f"{_format_number(limit_input)} m for {TURNING_REFERENCE_LABELS[reference]} by {margin_text}."
        )
    return _result(
        code=TURNING_CONSTRAINT,
        label="Turning-envelope screening",
        state=state,
        parameter_code="turning_radius_normalized_m",
        requested_limit=limit_input,
        requested_unit="m",
        allowance=0,
        allowance_unit="m",
        effective_limit=limit_input,
        effective_unit="m",
        candidate=candidate,
        vehicle_value=display_value,
        vehicle_unit="m",
        margin=display_margin,
        margin_unit="m",
        value_shape=input_shape,
        semantic=semantic,
        reason=reason,
        vehicle=vehicle,
        utilization=vehicle_radius / site_radius if site_radius > 0 else None,
    )


def aggregate_constraint_results(results: Sequence[ConstraintResult]) -> DesignCheckState | None:
    if not results:
        return None
    if any(item.state == DesignCheckState.FAIL for item in results):
        return DesignCheckState.FAIL
    if any(item.state == DesignCheckState.INDETERMINATE for item in results):
        return DesignCheckState.INDETERMINATE
    return DesignCheckState.PASS


def evaluate_vehicle(vehicle: DesignVehicle, inputs: DesignCheckInputs) -> VehicleDesignCheckResult:
    evaluators = {
        HEIGHT_CONSTRAINT: evaluate_height_constraint,
        WIDTH_CONSTRAINT: evaluate_width_constraint,
        LENGTH_CONSTRAINT: evaluate_length_constraint,
        TURNING_CONSTRAINT: evaluate_turning_constraint,
    }
    results = tuple(evaluators[code](vehicle, inputs) for code in inputs.active_constraint_codes)
    overall = aggregate_constraint_results(results)
    failed = tuple(item for item in results if item.state == DesignCheckState.FAIL)
    blockers = tuple(item for item in results if item.state == DesignCheckState.INDETERMINATE)
    closest = None
    largest = None
    if overall == DesignCheckState.PASS:
        comparable = [item for item in results if item.utilization is not None]
        closest = max(comparable, key=lambda item: item.utilization) if comparable else None
    elif overall == DesignCheckState.FAIL:
        comparable = [
            item
            for item in failed
            if item.relative_exceedance is not None and item.relative_exceedance > 0
        ]
        largest = max(comparable, key=lambda item: item.relative_exceedance) if comparable else None
    return VehicleDesignCheckResult(
        vehicle=vehicle,
        constraint_results=results,
        overall_state=overall,
        closest_active_limit=closest,
        largest_exceedance=largest,
        decision_blockers=blockers,
        failed_constraints=failed,
    )


def evaluate_design_check(
    vehicles: Iterable[DesignVehicle],
    inputs: DesignCheckInputs,
) -> DesignCheckReport:
    """Evaluate every candidate deterministically under DESIGN_CHECK_V1."""

    return DesignCheckReport(
        method_id=METHOD_ID,
        inputs=inputs,
        vehicles=tuple(evaluate_vehicle(vehicle, inputs) for vehicle in vehicles),
    )


# Short aliases keep the domain surface easy to discover for callers and tests.
evaluate_height = evaluate_height_constraint
evaluate_width = evaluate_width_constraint
evaluate_length = evaluate_length_constraint
evaluate_turning = evaluate_turning_constraint
