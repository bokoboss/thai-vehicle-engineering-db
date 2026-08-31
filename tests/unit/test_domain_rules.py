from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain.derivations import nominal_unloaded_tyre_radius_mm, parse_tyre_size
from app.domain.enums import AvailabilityState, EvidenceMethod
from app.domain.schemas import GeometryAssetCreate, NormalizedValueCreate
from app.domain.validation import ContractViolation, screening_breakover_symmetric_angle_deg, validate_ramp_namespace


def test_tyre_notation_and_nominal_radius_are_deterministic():
    section, aspect, rim = parse_tyre_size("235/50 R18")
    assert (section, aspect, rim) == (235, 50, 18)
    assert nominal_unloaded_tyre_radius_mm(section, aspect, rim) == pytest.approx(346.1)


def test_unknown_value_cannot_contain_zero_or_other_typed_value():
    with pytest.raises(ValidationError):
        NormalizedValueCreate(parameter_code="x", numeric_value=0, availability_state=AvailabilityState.UNKNOWN)


def test_available_value_requires_exactly_one_typed_field():
    with pytest.raises(ValidationError):
        NormalizedValueCreate(parameter_code="x", numeric_value=1, text_value="1")


def test_derived_value_requires_a_rule_version():
    with pytest.raises(ValidationError):
        NormalizedValueCreate(parameter_code="x", numeric_value=1, evidence_method=EvidenceMethod.DERIVED)


def test_geometry_requires_datum_and_content():
    with pytest.raises(ValidationError):
        GeometryAssetCreate(geometry_role="SIDE_SILHOUETTE", representation_type="POLYLINE", unit="mm", coordinate_system_version="")


def test_ramp_screening_formula_is_not_a_physical_solver():
    assert screening_breakover_symmetric_angle_deg(135, 2700) == pytest.approx(11.421, abs=0.001)
    with pytest.raises(ContractViolation):
        validate_ramp_namespace("oem_published_breakover_angle_deg", requested_class="SCREENING")
    with pytest.raises(ContractViolation):
        validate_ramp_namespace(
            "oem_published_breakover_angle_deg",
            requested_class="SCREENING",
            evidence_method=EvidenceMethod.DERIVED,
            derivation_rule_code="ramp_screening_breakover_symmetric",
        )
