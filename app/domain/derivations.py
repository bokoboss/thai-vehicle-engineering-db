from __future__ import annotations

import re
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DerivationRule, NormalizedValue, ParameterDefinition, VehicleConfiguration
from app.domain.enums import (
    ApplicabilityGrade,
    EvidenceMethod,
    ResolutionState,
    VerificationState,
)
from app.domain.schemas import NormalizedValueCreate
from app.domain.validation import ContractViolation, screening_breakover_symmetric_angle_deg
from app.services.foundation import create_normalized_value


TYRE_SIZE_RE = re.compile(r"^\s*(?P<section>\d+(?:\.\d+)?)\s*/\s*(?P<aspect>\d+(?:\.\d+)?)\s*(?:R|ZR)\s*(?P<rim>\d+(?:\.\d+)?)\s*$", re.IGNORECASE)


def parse_tyre_size(size_text: str) -> tuple[float, float, float]:
    match = TYRE_SIZE_RE.match(size_text)
    if not match:
        raise ContractViolation(f"unsupported tyre-size notation: {size_text}")
    return (
        float(match.group("section")),
        float(match.group("aspect")),
        float(match.group("rim")),
    )


def nominal_unloaded_tyre_radius_mm(section_width_mm: float, aspect_percent: float, rim_inches: float) -> float:
    if section_width_mm <= 0 or aspect_percent <= 0 or rim_inches <= 0:
        raise ContractViolation("tyre radius inputs must be positive")
    return (rim_inches * 25.4 / 2) + (section_width_mm * aspect_percent / 100)


def register_derivation_rule(
    session: Session,
    *,
    rule_code: str,
    version: str,
    name: str,
    output_parameter_code: str,
    formula_description: str,
    validity_conditions: str,
    uncertainty_method: str,
    reference_basis: str,
    input_parameter_codes: list[str],
) -> DerivationRule:
    existing = session.scalar(
        select(DerivationRule).where(DerivationRule.rule_code == rule_code, DerivationRule.version == version)
    )
    if existing:
        return existing
    output_definition = session.scalar(
        select(ParameterDefinition).where(ParameterDefinition.parameter_code == output_parameter_code)
    )
    if output_definition is None:
        raise ContractViolation(f"cannot register rule for unknown parameter {output_parameter_code}")
    rule = DerivationRule(
        rule_code=rule_code,
        version=version,
        name=name,
        output_parameter_definition_id=output_definition.id,
        formula_description=formula_description,
        validity_conditions=validity_conditions,
        uncertainty_method=uncertainty_method,
        reference_basis=reference_basis,
        input_parameter_codes=input_parameter_codes,
        active=True,
    )
    session.add(rule)
    session.flush()
    return rule


def derive_nominal_tyre_radius(
    session: Session,
    config: VehicleConfiguration,
    *,
    tyre_size_value: NormalizedValue,
    output_parameter_code: str,
    evidence_method: EvidenceMethod = EvidenceMethod.DERIVED,
) -> NormalizedValue:
    if tyre_size_value.text_value is None:
        raise ContractViolation("tyre radius derivation requires a tyre-size text value")
    section, aspect, rim = parse_tyre_size(tyre_size_value.text_value)
    result = nominal_unloaded_tyre_radius_mm(section, aspect, rim)
    rule = register_derivation_rule(
        session,
        rule_code=f"nominal_unloaded_tyre_radius_from_size_{output_parameter_code}",
        version="1",
        name="Nominal unloaded tyre radius from size notation",
        output_parameter_code=output_parameter_code,
        formula_description="rim_in * 25.4 / 2 + section_width_mm * aspect_percent / 100",
        validity_conditions="Standard passenger-tyre width/aspect/rim notation; nominal unloaded radius only.",
        uncertainty_method="Notation-derived nominal geometry; excludes tyre growth, load and deflection.",
        reference_basis="Controlled Phase 0 derivation; not static-loaded radius.",
        input_parameter_codes=[tyre_size_value.parameter_definition.parameter_code],
    )
    payload = NormalizedValueCreate(
        parameter_code=output_parameter_code,
        numeric_value=result,
        canonical_unit="mm",
        evidence_method=evidence_method,
        resolution_state=ResolutionState.UNCONTESTED,
        verification_state=VerificationState.REVIEWED,
        applicability_grade=ApplicabilityGrade.EXACT_CONFIGURATION,
        normalization_rule_version=f"{rule.rule_code}:{rule.version}",
        semantic_metadata={
            "radius_kind": "NOMINAL_UNLOADED",
            "formula": rule.formula_description,
        },
    )
    return create_normalized_value(
        session,
        config,
        payload,
        derivation_rule=rule,
        derivation_inputs=[(tyre_size_value, "tyre_size_notation")],
        result_notes="Nominal notation-derived radius; do not use as static-loaded radius.",
    )


def derive_avt_track_estimate(
    session: Session,
    config: VehicleConfiguration,
    *,
    centerline_value: NormalizedValue,
    nominal_section_width_value: NormalizedValue,
    output_parameter_code: str,
) -> NormalizedValue:
    if centerline_value.numeric_value is None or nominal_section_width_value.numeric_value is None:
        raise ContractViolation("AVT screening track estimate requires numeric centerline and nominal-width inputs")
    result = float(centerline_value.numeric_value) + float(nominal_section_width_value.numeric_value)
    rule = register_derivation_rule(
        session,
        rule_code=f"avt_track_centerline_plus_nominal_section_{output_parameter_code}",
        version="1",
        name="Screening AVT track estimate from centerline track plus nominal section width",
        output_parameter_code=output_parameter_code,
        formula_description="estimated outer-face track = OEM centreline track + nominal tyre section width",
        validity_conditions="Screening estimate only; mounted tyre/wheel geometry and offsets are not established.",
        uncertainty_method="At least nominal tyre section-width/mounting uncertainty; not AVT-ready.",
        reference_basis="AVT mapping specification v1; nominal width alone is insufficient.",
        input_parameter_codes=[
            centerline_value.parameter_definition.parameter_code,
            nominal_section_width_value.parameter_definition.parameter_code,
        ],
    )
    payload = NormalizedValueCreate(
        parameter_code=output_parameter_code,
        numeric_value=result,
        canonical_unit="mm",
        evidence_method=EvidenceMethod.ESTIMATED,
        resolution_state=ResolutionState.UNCONTESTED,
        verification_state=VerificationState.REVIEWED,
        applicability_grade=ApplicabilityGrade.EXACT_CONFIGURATION,
        normalization_rule_version=f"{rule.rule_code}:{rule.version}",
        semantic_metadata={
            "track_definition": "OUTER_TYRE_FACES",
            "source_basis": "CENTERLINE_PLUS_NOMINAL_WIDTH",
            "screening_only": True,
            "assumption": "nominal section width is treated as mounted outer-face addition for screening only",
        },
    )
    return create_normalized_value(
        session,
        config,
        payload,
        derivation_rule=rule,
        derivation_inputs=[
            (centerline_value, "oem_centerline_track"),
            (nominal_section_width_value, "nominal_section_width"),
        ],
        result_notes="Rejected as AVT-ready because this is a nominal-width screening approximation.",
    )


def derive_screening_breakover(
    session: Session,
    config: VehicleConfiguration,
    *,
    clearance_value: NormalizedValue,
    wheelbase_value: NormalizedValue,
) -> NormalizedValue:
    if clearance_value.numeric_value is None or wheelbase_value.numeric_value is None:
        raise ContractViolation("screening breakover requires numeric clearance and wheelbase values")
    clearance_metadata = clearance_value.semantic_metadata or {}
    if clearance_metadata.get("clearance_type") != "BETWEEN_AXLES":
        raise ContractViolation("screening breakover requires explicitly between-axles clearance")
    result = screening_breakover_symmetric_angle_deg(
        float(clearance_value.numeric_value),
        float(wheelbase_value.numeric_value),
    )
    output_code = "screening_breakover_symmetric_angle_deg"
    rule = register_derivation_rule(
        session,
        rule_code="ramp_screening_breakover_symmetric",
        version="1",
        name="Symmetric breakover screening angle",
        output_parameter_code=output_code,
        formula_description="beta_screen_symmetric = 2 * atan(2h/L), reported in degrees",
        validity_conditions="Symmetric midpoint screening assumption; h is an explicitly typed between-axles clearance, not a global clearance proxy.",
        uncertainty_method="Screening-only; excludes actual lower-envelope contact geometry, tyre deflection and pose effects.",
        reference_basis="RAMP_VERTICAL_CLEARANCE_METHOD.md, Level C screening.",
        input_parameter_codes=[
            clearance_value.parameter_definition.parameter_code,
            wheelbase_value.parameter_definition.parameter_code,
        ],
    )
    payload = NormalizedValueCreate(
        parameter_code=output_code,
        numeric_value=result,
        canonical_unit="deg",
        evidence_method=EvidenceMethod.DERIVED,
        resolution_state=ResolutionState.UNCONTESTED,
        verification_state=VerificationState.REVIEWED,
        applicability_grade=ApplicabilityGrade.EXACT_CONFIGURATION,
        normalization_rule_version=f"{rule.rule_code}:{rule.version}",
        semantic_metadata={
            "ramp_result_class": "SCREENING",
            "formula": rule.formula_description,
            "screening_assumptions": [
                "symmetric midpoint limiting point",
                "between-axles clearance represents the assumed limiting point",
            ],
        },
    )
    return create_normalized_value(
        session,
        config,
        payload,
        derivation_rule=rule,
        derivation_inputs=[
            (clearance_value, "between_axles_clearance"),
            (wheelbase_value, "wheelbase"),
        ],
        result_notes="Screening namespace only; no physical/OEM angle promotion.",
    )
