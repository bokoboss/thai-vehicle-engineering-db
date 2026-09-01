from __future__ import annotations

import pytest

from app.domain.design_check import (
    DesignCheckInputs,
    DesignCheckState,
    DesignVehicle,
    ParameterAssessmentRecord,
    ParameterCandidate,
    evaluate_design_check,
    evaluate_height_constraint,
    evaluate_length_constraint,
    evaluate_turning_constraint,
    evaluate_vehicle,
    evaluate_width_constraint,
)


def vehicle(*values: ParameterCandidate, assessments=()) -> DesignVehicle:
    return DesignVehicle(
        stable_vehicle_code="UNIT-VEHICLE",
        manufacturer="Test maker",
        commercial_model="Test model",
        variant="Exact variant",
        values=tuple(values),
        assessments=tuple(assessments),
        detail_url="/vehicles/UNIT-VEHICLE",
    )


def numeric_value(code: str, value: float, unit: str, *, metadata=None, **kwargs) -> ParameterCandidate:
    return ParameterCandidate(
        parameter_code=code,
        value=value,
        unit=unit,
        semantic_metadata=metadata or {},
        **kwargs,
    )


def turning_value(
    value: float = 5.3,
    *,
    reference: str = "CURB_TO_CURB",
    axle_scope: str = "ALL_AXLES",
    wall_scope: str = "NOT_APPLICABLE",
    shape: str = "RADIUS",
    **kwargs,
) -> ParameterCandidate:
    return numeric_value(
        "turning_radius_normalized_m",
        value,
        "m",
        metadata={
            "turning_radius_or_diameter": shape,
            "turning_reference": reference,
            "turning_axle_scope": axle_scope,
            "turning_wall_envelope_scope": wall_scope,
        },
        **kwargs,
    )


def test_height_exact_boundary_and_allowance_margin():
    candidate = numeric_value("overall_height_mm", 2000, "mm")
    request = DesignCheckInputs(available_clear_height_mm=2100, vertical_allowance_mm=100)

    result = evaluate_height_constraint(vehicle(candidate), request)

    assert result.state == DesignCheckState.PASS
    assert result.effective_limit == 2000
    assert result.margin == 0


def test_height_positive_and_negative_margins_are_signed():
    request = DesignCheckInputs(available_clear_height_mm=2100, vertical_allowance_mm=100)
    passing = evaluate_height_constraint(vehicle(numeric_value("overall_height_mm", 1835, "mm")), request)
    failing = evaluate_height_constraint(vehicle(numeric_value("overall_height_mm", 2285, "mm")), request)

    assert passing.state == DesignCheckState.PASS
    assert passing.margin == 165
    assert failing.state == DesignCheckState.FAIL
    assert failing.margin == -285


def test_width_allowance_arithmetic_and_exact_envelope_boundary():
    candidate = numeric_value(
        "overall_width_including_mirrors_mm",
        2000,
        "mm",
        metadata={"width_envelope_definition": "INCLUDING_MIRRORS_OPEN"},
    )
    request = DesignCheckInputs(
        available_clear_width_mm=2100,
        lateral_allowance_each_side_mm=50,
        width_envelope="INCLUDING_MIRRORS_OPEN",
    )

    result = evaluate_width_constraint(vehicle(candidate), request)

    assert result.state == DesignCheckState.PASS
    assert result.effective_limit == 2000
    assert result.margin == 0


def test_width_envelope_mismatch_is_indeterminate_and_never_substituted():
    body = numeric_value(
        "overall_width_body_mm",
        1838,
        "mm",
        metadata={"width_envelope_definition": "BODY_EXCLUDING_MIRRORS"},
    )
    request = DesignCheckInputs(
        available_clear_width_mm=2100,
        lateral_allowance_each_side_mm=50,
        width_envelope="INCLUDING_MIRRORS_OPEN",
    )

    result = evaluate_width_constraint(vehicle(body), request)

    assert result.state == DesignCheckState.INDETERMINATE
    assert "mirrors open" in result.reason.lower()
    assert "substituted" in result.reason.lower()


def test_reported_width_is_not_promoted_to_body_width():
    reported = numeric_value(
        "overall_width_reported_mm",
        1875,
        "mm",
        metadata={"width_envelope_definition": "OEM_UNSPECIFIED"},
    )
    request = DesignCheckInputs(
        available_clear_width_mm=2000,
        lateral_allowance_each_side_mm=0,
        width_envelope="BODY_EXCLUDING_MIRRORS",
    )

    result = evaluate_width_constraint(vehicle(reported), request)

    assert result.state == DesignCheckState.INDETERMINATE
    assert "cannot be substituted" in result.reason.lower()


def test_turning_radius_and_diameter_inputs_use_deterministic_normalization():
    candidate = turning_value()
    radius_request = DesignCheckInputs(
        maximum_turning_value_m=5.3,
        turning_input_shape="RADIUS",
        turning_reference="CURB_TO_CURB",
    )
    diameter_request = DesignCheckInputs(
        maximum_turning_value_m=11.0,
        turning_input_shape="DIAMETER",
        turning_reference="CURB_TO_CURB",
    )

    radius_result = evaluate_turning_constraint(vehicle(candidate), radius_request)
    diameter_result = evaluate_turning_constraint(vehicle(candidate), diameter_request)

    assert radius_result.state == DesignCheckState.PASS
    assert radius_result.margin == pytest.approx(0)
    assert diameter_result.state == DesignCheckState.PASS
    assert diameter_result.vehicle_value == pytest.approx(10.6)
    assert diameter_result.margin == pytest.approx(0.4)


def test_turning_curb_wall_mismatch_and_unspecified_reference_fail_closed():
    curb = turning_value()
    wall_request = DesignCheckInputs(
        maximum_turning_value_m=11,
        turning_input_shape="DIAMETER",
        turning_reference="WALL_TO_WALL",
    )
    mismatch = evaluate_turning_constraint(vehicle(curb), wall_request)
    assert mismatch.state == DesignCheckState.INDETERMINATE
    assert "exact reference match" in mismatch.reason

    unspecified = evaluate_turning_constraint(
        vehicle(
            turning_value(
                reference="OEM_UNSPECIFIED",
                axle_scope="OEM_UNSPECIFIED",
                wall_scope="OEM_UNSPECIFIED",
            )
        ),
        DesignCheckInputs(
            maximum_turning_value_m=11,
            turning_input_shape="DIAMETER",
            turning_reference="CURB_TO_CURB",
        ),
    )
    assert unspecified.state == DesignCheckState.INDETERMINATE
    assert "reference" in unspecified.reason.lower()


def test_curb_to_curb_with_unresolved_axle_scope_is_indeterminate():
    result = evaluate_turning_constraint(
        vehicle(turning_value(axle_scope="OEM_UNSPECIFIED")),
        DesignCheckInputs(
            maximum_turning_value_m=11,
            turning_input_shape="DIAMETER",
            turning_reference="CURB_TO_CURB",
        ),
    )

    assert result.state == DesignCheckState.INDETERMINATE
    assert "axle scope" in result.reason.lower()


def test_raw_oem_turning_text_is_not_parsed_into_a_radius():
    raw = ParameterCandidate(
        parameter_code="oem_turning_value_text",
        value="11.7 m curb-to-curb turning circle",
        unit=None,
    )
    result = evaluate_turning_constraint(
        vehicle(raw),
        DesignCheckInputs(
            maximum_turning_value_m=12,
            turning_input_shape="DIAMETER",
            turning_reference="CURB_TO_CURB",
        ),
    )

    assert result.state == DesignCheckState.INDETERMINATE
    assert "not parsed" in result.reason


def test_conflict_and_unknown_values_are_indeterminate():
    conflict = numeric_value(
        "overall_length_mm",
        4500,
        "mm",
        resolution_state="CONFLICTING",
        preferred=True,
    )
    conflict_result = evaluate_length_constraint(
        vehicle(conflict), DesignCheckInputs(maximum_vehicle_length_mm=5000)
    )
    assert conflict_result.state == DesignCheckState.INDETERMINATE
    assert "conflicting" in conflict_result.reason.lower()

    unknown_result = evaluate_height_constraint(
        vehicle(
            assessments=[
                ParameterAssessmentRecord(
                    parameter_code="overall_height_mm",
                    availability_state="UNKNOWN",
                    unknown_reason="No exact height was located.",
                )
            ]
        ),
        DesignCheckInputs(available_clear_height_mm=2100),
    )
    assert unknown_result.state == DesignCheckState.INDETERMINATE
    assert "no exact height" in unknown_result.reason.lower()

    width_conflict = numeric_value(
        "overall_width_including_mirrors_mm",
        2000,
        "mm",
        metadata={"width_envelope_definition": "INCLUDING_MIRRORS_OPEN"},
        resolution_state="CONFLICTING",
    )
    width_conflict_result = evaluate_width_constraint(
        vehicle(width_conflict),
        DesignCheckInputs(
            available_clear_width_mm=2100,
            lateral_allowance_each_side_mm=0,
            width_envelope="INCLUDING_MIRRORS_OPEN",
        ),
    )
    assert width_conflict_result.state == DesignCheckState.INDETERMINATE
    assert "conflicting" in width_conflict_result.reason.lower()


def test_aggregation_is_fail_closed_and_retains_all_constraint_results():
    vehicle_data = vehicle(
        numeric_value("overall_height_mm", 1800, "mm"),
        numeric_value("overall_length_mm", 5200, "mm"),
    )
    request = DesignCheckInputs(
        available_clear_height_mm=2100,
        maximum_vehicle_length_mm=5000,
        maximum_turning_value_m=11,
        turning_input_shape="DIAMETER",
        turning_reference="CURB_TO_CURB",
    )
    result = evaluate_vehicle(vehicle_data, request)

    assert result.overall_state == DesignCheckState.FAIL
    assert {item.code for item in result.constraint_results} == {"height", "length", "turning"}
    assert {item.code for item in result.failed_constraints} == {"length"}
    assert {item.code for item in result.decision_blockers} == {"turning"}


def test_no_fail_with_unknown_is_indeterminate_and_all_pass_is_pass():
    unknown = evaluate_vehicle(
        vehicle(
            numeric_value("overall_height_mm", 1800, "mm"),
            assessments=[
                ParameterAssessmentRecord(
                    parameter_code="overall_length_mm",
                    availability_state="NOT_FOUND_AFTER_SEARCH",
                    unknown_reason="Length not found.",
                )
            ],
        ),
        DesignCheckInputs(available_clear_height_mm=2100, maximum_vehicle_length_mm=5000),
    )
    assert unknown.overall_state == DesignCheckState.INDETERMINATE

    all_pass = evaluate_vehicle(
        vehicle(
            numeric_value("overall_height_mm", 1800, "mm"),
            numeric_value("overall_length_mm", 4900, "mm"),
        ),
        DesignCheckInputs(available_clear_height_mm=2100, maximum_vehicle_length_mm=5000),
    )
    assert all_pass.overall_state == DesignCheckState.PASS
    assert all_pass.closest_active_limit is not None


def test_zero_constraints_have_no_suitability_verdict():
    report = evaluate_design_check(
        [vehicle(numeric_value("overall_height_mm", 1800, "mm"))],
        DesignCheckInputs(),
    )

    assert report.has_active_constraints is False
    assert report.result_counts == {"PASS": 0, "FAIL": 0, "INDETERMINATE": 0}
    assert len(report.vehicles) == 1
    assert report.vehicles[0].overall_state is None


def test_multiple_scoped_values_are_not_silently_reduced_to_a_favourable_value():
    result = evaluate_height_constraint(
        vehicle(
            numeric_value(
                "overall_height_mm",
                1800,
                "mm",
                scope_text="Unladen",
                preferred=True,
            ),
            numeric_value("overall_height_mm", 1880, "mm", scope_text="Laden"),
        ),
        DesignCheckInputs(available_clear_height_mm=2100),
    )
    assert result.state == DesignCheckState.INDETERMINATE
    assert "across scopes" in result.reason


def test_semantic_cue_keeps_same_named_unspecified_values_in_their_namespace():
    result = evaluate_turning_constraint(
        vehicle(
            turning_value(
                reference="OEM_UNSPECIFIED",
                axle_scope="OEM_UNSPECIFIED",
                wall_scope="OEM_UNSPECIFIED",
            )
        ),
        DesignCheckInputs(
            maximum_turning_value_m=11,
            turning_input_shape="DIAMETER",
            turning_reference="CURB_TO_CURB",
        ),
    )
    assert "OEM reference unspecified" in result.semantic_cue
    assert "OEM axle scope unspecified" in result.semantic_cue
    assert "OEM wall envelope unspecified" in result.semantic_cue


def test_unresolved_fitment_scope_and_invalid_numeric_value_cannot_pass():
    scoped = evaluate_height_constraint(
        vehicle(
            numeric_value(
                "overall_height_mm",
                1800,
                "mm",
                scope_text="Fitment scope unresolved",
            )
        ),
        DesignCheckInputs(available_clear_height_mm=2100),
    )
    invalid = evaluate_length_constraint(
        vehicle(numeric_value("overall_length_mm", -1, "mm")),
        DesignCheckInputs(maximum_vehicle_length_mm=5000),
    )
    assert scoped.state == DesignCheckState.INDETERMINATE
    assert "scope" in scoped.reason.lower()
    assert invalid.state == DesignCheckState.INDETERMINATE
    assert "greater than zero" in invalid.reason


def test_controlled_derived_value_requires_and_can_use_intact_lineage():
    derived = numeric_value(
        "overall_height_mm",
        1800,
        "mm",
        evidence_method="DERIVED",
        evidence_link_count=0,
        normalization_rule_version="controlled-height:1",
        lineage_intact=True,
    )
    incomplete = numeric_value(
        "overall_height_mm",
        1800,
        "mm",
        evidence_method="DERIVED",
        evidence_link_count=0,
        normalization_rule_version="controlled-height:1",
        lineage_intact=False,
    )
    request = DesignCheckInputs(available_clear_height_mm=2100)

    assert evaluate_height_constraint(vehicle(derived), request).state == DesignCheckState.PASS
    incomplete_result = evaluate_height_constraint(vehicle(incomplete), request)
    assert incomplete_result.state == DesignCheckState.INDETERMINATE
    assert "lineage" in incomplete_result.reason
