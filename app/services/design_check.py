from __future__ import annotations

from collections.abc import Iterable

from app.db.models import VehicleConfiguration
from app.domain.design_check import (
    DesignCheckInputs,
    DesignCheckReport,
    DesignVehicle,
    ParameterAssessmentRecord,
    ParameterCandidate,
    evaluate_design_check,
)
from app.domain.enums import DecisionState


DESIGN_CHECK_PARAMETER_CODES = frozenset(
    {
        "overall_height_mm",
        "overall_width_reported_mm",
        "overall_width_body_mm",
        "overall_width_including_mirrors_mm",
        "overall_width_mirrors_folded_mm",
        "overall_length_mm",
        "turning_radius_normalized_m",
        "oem_turning_value_text",
    }
)


def _scope_text(value, fitments, load_conditions) -> str:
    parts: list[str] = []
    fitment = fitments.get(value.vehicle_fitment_id) if value.vehicle_fitment_id else None
    load_condition = load_conditions.get(value.load_condition_id) if value.load_condition_id else None
    if fitment:
        parts.append(f"Fitment {fitment.fitment_code}")
    elif value.vehicle_fitment_id:
        parts.append("Fitment scope unresolved")
    if load_condition:
        parts.append(f"Load: {load_condition.name} · {load_condition.mass_basis}")
    elif value.load_condition_id:
        parts.append("Load condition unresolved")
    return " · ".join(parts) if parts else "Configuration-wide"


def _active_conflict_decision_id(config: VehicleConfiguration, value) -> str | None:
    matches = [
        decision
        for decision in config.conflict_decisions
        if decision.vehicle_configuration_id == config.id
        and decision.parameter_definition_id == value.parameter_definition_id
        and decision.selected_normalized_value_id == value.id
        and decision.decision_state == DecisionState.SELECTED.value
        and decision.superseded_by_decision_id is None
    ]
    return matches[0].id if len(matches) == 1 else None


def design_vehicle_from_configuration(config: VehicleConfiguration) -> DesignVehicle:
    """Map an eagerly loaded exact configuration to the pure evaluator input."""

    fitments = {fitment.id: fitment for fitment in config.fitments}
    load_conditions = {condition.id: condition for condition in config.load_conditions}
    values = []
    for value in config.normalized_values:
        code = value.parameter_definition.parameter_code
        if code not in DESIGN_CHECK_PARAMETER_CODES:
            continue
        derived_lineage_intact = True
        if value.evidence_method == "DERIVED":
            derivation_run = value.derivation_run
            derived_lineage_intact = bool(
                value.normalization_rule_version
                and derivation_run is not None
                and derivation_run.inputs
            )
        values.append(
            ParameterCandidate(
                parameter_code=code,
                value=(
                    value.numeric_value
                    if value.numeric_value is not None
                    else value.text_value
                    if value.text_value is not None
                    else value.boolean_value
                    if value.boolean_value is not None
                    else value.enum_value
                    if value.enum_value is not None
                    else value.json_value
                ),
                unit=value.canonical_unit,
                value_id=value.id,
                semantic_metadata=dict(value.semantic_metadata or {}),
                scope_text=_scope_text(value, fitments, load_conditions),
                evidence_method=value.evidence_method,
                resolution_state=value.resolution_state,
                verification_state=value.verification_state,
                availability_state=value.availability_state,
                applicability_grade=value.applicability_grade,
                evidence_link_count=len(value.evidence_links),
                normalization_rule_version=value.normalization_rule_version,
                lineage_intact=derived_lineage_intact,
                preferred=value.preferred,
                conflict_decision_id=_active_conflict_decision_id(config, value),
                detail_url=f"/vehicles/{config.stable_vehicle_code}#value-{value.id}",
            )
        )
    assessments = tuple(
        ParameterAssessmentRecord(
            parameter_code=assessment.parameter_definition.parameter_code,
            availability_state=assessment.availability_state,
            unknown_reason=assessment.unknown_reason,
            scope_text=(
                fitments[assessment.vehicle_fitment_id].fitment_code
                if assessment.vehicle_fitment_id in fitments
                else "Fitment scope unresolved"
                if assessment.vehicle_fitment_id
                else "Configuration-wide"
            ),
        )
        for assessment in config.parameter_assessments
        if assessment.parameter_definition.parameter_code in DESIGN_CHECK_PARAMETER_CODES
    )
    return DesignVehicle(
        stable_vehicle_code=config.stable_vehicle_code,
        manufacturer=config.vehicle_model.manufacturer.display_name,
        commercial_model=config.vehicle_model.display_model_name,
        variant=config.variant_trim,
        generation=config.generation_name,
        identity_time_label=(
            config.identity_time_label_raw
            or str(config.model_year_from)
            if config.identity_time_basis == "MODEL_YEAR" and config.model_year_from is not None
            else config.identity_time_label_raw
            or config.identity_time_basis
        ),
        body_style=config.body_style,
        powertrain=config.powertrain,
        detail_url=f"/vehicles/{config.stable_vehicle_code}",
        values=tuple(values),
        assessments=assessments,
    )


def evaluate_configurations(
    configurations: Iterable[VehicleConfiguration],
    inputs: DesignCheckInputs,
) -> DesignCheckReport:
    return evaluate_design_check(
        (design_vehicle_from_configuration(config) for config in configurations),
        inputs,
    )
