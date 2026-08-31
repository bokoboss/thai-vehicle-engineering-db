from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    Axle,
    ConflictDecision,
    DerivationInput,
    DerivationRule,
    DerivationRun,
    EvidenceLink,
    GeometryAsset,
    LoadCondition,
    NormalizedValue,
    ParameterAssessment,
    ParameterDefinition,
    SourceDocument,
    SourceObservation,
    SteeringRelation,
    VehicleConfiguration,
    VehicleFitment,
)
from app.domain.enums import EvidenceMethod, ResolutionState
from app.domain.scope import (
    validate_axle_scope,
    validate_fitment_scope,
    validate_geometry_references,
    validate_load_condition_scope,
    validate_source_observation_scope,
)
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
from app.domain.validation import (
    ContractViolation,
    validate_avt_track_candidate,
    validate_geometry_asset_role,
    validate_identity_time_basis,
    validate_parameter_assessment,
    validate_persisted_value_contract,
    validate_provenance_payload,
    validate_registered_semantics,
    validate_ramp_namespace,
    validate_secondary_steering,
    validate_typed_value_shape,
    validate_width_promotion,
)


def enum_value(value: Any) -> Any:
    return getattr(value, "value", value)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_vehicle_configuration(
    session: Session,
    payload: VehicleConfigurationCreate,
    *,
    manufacturer_name: str,
    manufacturer_display_name: str | None = None,
    display_model_name: str | None = None,
    canonical_model_name: str | None = None,
    country_of_origin: str | None = None,
) -> VehicleConfiguration:
    from app.db.models import Manufacturer, VehicleModel

    validate_identity_time_basis(
        identity_verification_state=payload.identity_verification_state,
        identity_time_basis=payload.identity_time_basis,
        model_year_from=payload.model_year_from,
        model_year_to=payload.model_year_to,
        identity_time_label_raw=payload.identity_time_label_raw,
        sale_period_from=payload.sale_period_from,
        sale_period_to=payload.sale_period_to,
    )

    manufacturer = session.scalar(select(Manufacturer).where(Manufacturer.canonical_name == manufacturer_name))
    if manufacturer is None:
        manufacturer = Manufacturer(
            canonical_name=manufacturer_name,
            display_name=manufacturer_display_name or manufacturer_name,
            country_of_origin=country_of_origin,
        )
        session.add(manufacturer)
        session.flush()
    model_name = canonical_model_name or payload.stable_vehicle_code
    vehicle_model = session.scalar(
        select(VehicleModel).where(
            VehicleModel.manufacturer_id == manufacturer.id,
            VehicleModel.canonical_model_name == model_name,
        )
    )
    if vehicle_model is None:
        vehicle_model = VehicleModel(
            manufacturer_id=manufacturer.id,
            canonical_model_name=model_name,
            display_model_name=display_model_name or model_name,
        )
        session.add(vehicle_model)
        session.flush()
    config = VehicleConfiguration(
        stable_vehicle_code=payload.stable_vehicle_code,
        vehicle_model_id=vehicle_model.id,
        market_code=payload.market_code,
        generation_name=payload.generation_name,
        chassis_platform_code=payload.chassis_platform_code,
        body_style=payload.body_style,
        model_year_from=payload.model_year_from,
        model_year_to=payload.model_year_to,
        identity_time_basis=enum_value(payload.identity_time_basis),
        identity_time_label_raw=payload.identity_time_label_raw,
        sale_period_from=payload.sale_period_from,
        sale_period_to=payload.sale_period_to,
        variant_trim=payload.variant_trim,
        powertrain=payload.powertrain,
        drivetrain=payload.drivetrain,
        body_configuration=payload.body_configuration,
        identity_notes=payload.identity_notes,
        identity_verification_state=enum_value(payload.identity_verification_state),
    )
    session.add(config)
    session.flush()
    return config


def create_conflict_decision(
    session: Session,
    config: VehicleConfiguration,
    payload: ConflictDecisionCreate,
) -> ConflictDecision:
    """Create one explicit, auditable conflict selection for a configuration."""

    definition = _parameter_definition(session, payload.parameter_code)
    has_conflicting_value = session.scalar(
        select(NormalizedValue.id).where(
            NormalizedValue.vehicle_configuration_id == config.id,
            NormalizedValue.parameter_definition_id == definition.id,
            NormalizedValue.resolution_state.in_(
                {
                    ResolutionState.CONFLICTING.value,
                    ResolutionState.PREFERRED_WITH_CONFLICT.value,
                }
            ),
        )
    )
    if has_conflicting_value is None:
        raise ContractViolation("conflict decision requires a conflicting normalized value")
    selected_value = None
    if payload.selected_normalized_value_id is not None:
        selected_value = session.get(NormalizedValue, payload.selected_normalized_value_id)
        if selected_value is None:
            raise ContractViolation("conflict decision selected value does not reference a known normalized value")
        if selected_value.vehicle_configuration_id != config.id:
            raise ContractViolation("conflict decision selected value belongs to another configuration")
        if selected_value.parameter_definition_id != definition.id:
            raise ContractViolation("conflict decision selected value belongs to another parameter")
        if selected_value.resolution_state not in {
            "CONFLICTING",
            "PREFERRED_WITH_CONFLICT",
        }:
            raise ContractViolation("conflict decision must select a conflicting normalized value")
    if payload.decision_state.value == "SELECTED" and selected_value is None:
        raise ContractViolation("SELECTED conflict decisions require a selected normalized value")
    if payload.decision_state.value != "SELECTED" and selected_value is not None:
        raise ContractViolation("only SELECTED conflict decisions may select a normalized value")

    decision = ConflictDecision(
        vehicle_configuration_id=config.id,
        parameter_definition_id=definition.id,
        selected_normalized_value_id=selected_value.id if selected_value else None,
        decision_state=enum_value(payload.decision_state),
        rationale=payload.rationale,
        decided_at=payload.decided_at,
        reviewer=payload.reviewer,
    )
    session.add(decision)
    session.flush()
    return decision


def create_fitment(session: Session, config: VehicleConfiguration, fitment_code: str, **kwargs: Any) -> VehicleFitment:
    fitment = VehicleFitment(vehicle_configuration_id=config.id, fitment_code=fitment_code, **kwargs)
    session.add(fitment)
    session.flush()
    return fitment


def create_axle(session: Session, config: VehicleConfiguration, payload: AxleCreate) -> Axle:
    axle = Axle(
        vehicle_configuration_id=config.id,
        axle_role=enum_value(payload.axle_role),
        axle_index=payload.axle_index,
        longitudinal_position_mm=payload.longitudinal_position_mm,
        axle_group=payload.axle_group,
        driven=payload.driven,
        steered=payload.steered,
        retractable=payload.retractable,
        self_steering=payload.self_steering,
        notes=payload.notes,
    )
    session.add(axle)
    session.flush()
    return axle


def create_steering_relation(session: Session, config: VehicleConfiguration, payload: SteeringRelationCreate) -> SteeringRelation:
    validate_secondary_steering(payload)
    validate_axle_scope(session, config, payload.axle_id)
    if payload.source_observation_id is not None:
        validate_source_observation_scope(
            session,
            config,
            payload.source_observation_id,
            context="steering relation source observation",
        )
    relation = SteeringRelation(
        vehicle_configuration_id=config.id,
        axle_id=payload.axle_id,
        steering_role=enum_value(payload.steering_role),
        linkage_type=enum_value(payload.linkage_type),
        max_steering_angle_deg=payload.max_steering_angle_deg,
        phase_behavior=enum_value(payload.phase_behavior),
        angle_ratio=payload.angle_ratio,
        relation_function=payload.relation_function,
        speed_min_kph=payload.speed_min_kph,
        speed_max_kph=payload.speed_max_kph,
        mode_applicability=payload.mode_applicability,
        source_observation_id=payload.source_observation_id,
        notes=payload.notes,
    )
    session.add(relation)
    session.flush()
    return relation


def create_load_condition(session: Session, config: VehicleConfiguration | None, payload: LoadConditionCreate) -> LoadCondition:
    condition = LoadCondition(
        vehicle_configuration_id=config.id if config else None,
        name=payload.name,
        mass_basis=enum_value(payload.mass_basis),
        total_mass_kg=payload.total_mass_kg,
        occupant_count=payload.occupant_count,
        payload_kg=payload.payload_kg,
        front_axle_load_kg=payload.front_axle_load_kg,
        rear_axle_load_kg=payload.rear_axle_load_kg,
        front_tyre_pressure=payload.front_tyre_pressure,
        rear_tyre_pressure=payload.rear_tyre_pressure,
        tyre_pressure_unit=payload.tyre_pressure_unit,
        suspension_mode=payload.suspension_mode,
        ride_height_mode=payload.ride_height_mode,
        raw_oem_wording=payload.raw_oem_wording,
        source_document_id=payload.source_document_id,
        notes=payload.notes,
    )
    session.add(condition)
    session.flush()
    return condition


def create_source_document(session: Session, payload: SourceDocumentCreate) -> SourceDocument:
    document = SourceDocument(**payload.model_dump())
    session.add(document)
    session.flush()
    return document


def create_source_observation(
    session: Session,
    config: VehicleConfiguration | None,
    payload: SourceObservationCreate,
) -> SourceObservation:
    observation = SourceObservation(
        vehicle_configuration_id=config.id if config else None,
        vehicle_identity_claim=payload.vehicle_identity_claim,
        source_document_id=payload.source_document_id,
        raw_label=payload.raw_label,
        raw_value=payload.raw_value,
        raw_unit=payload.raw_unit,
        raw_qualifier=payload.raw_qualifier,
        raw_excerpt=payload.raw_excerpt,
        page_section_locator=payload.page_section_locator,
        reported_precision=payload.reported_precision,
        uncertainty_value=payload.uncertainty_value,
        uncertainty_unit=payload.uncertainty_unit,
        extraction_method=enum_value(payload.extraction_method),
        extracted_at=payload.extracted_at,
        extracted_by=payload.extracted_by,
        reviewer=payload.reviewer,
        ambiguity_note=payload.ambiguity_note,
    )
    session.add(observation)
    session.flush()
    return observation


def _parameter_definition(session: Session, parameter_code: str) -> ParameterDefinition:
    definition = session.scalar(select(ParameterDefinition).where(ParameterDefinition.parameter_code == parameter_code))
    if definition is None:
        raise ContractViolation(f"parameter registry does not define {parameter_code}")
    return definition


def _resolve_fitment_scope(
    session: Session,
    config: VehicleConfiguration,
    fitment: VehicleFitment | None,
    derivation_inputs: list[tuple[NormalizedValue, str]] | None,
) -> VehicleFitment | None:
    """Propagate one input fitment scope and reject mixed/incompatible scopes."""

    fitment = validate_fitment_scope(session, config, fitment)
    input_values = [input_value for input_value, _ in derivation_inputs or []]
    for input_value in input_values:
        if input_value.vehicle_configuration_id != config.id:
            raise ContractViolation("derivation input does not belong to the target configuration")
    input_fitment_ids = {input_value.vehicle_fitment_id for input_value in input_values if input_value.vehicle_fitment_id is not None}
    if len(input_fitment_ids) > 1:
        raise ContractViolation("derivation inputs belong to incompatible fitments")
    if input_fitment_ids:
        input_fitment_id = next(iter(input_fitment_ids))
        if fitment is not None and fitment.id != input_fitment_id:
            raise ContractViolation("derived output fitment does not match its input fitment scope")
        fitment = fitment or session.get(VehicleFitment, input_fitment_id)
        fitment = validate_fitment_scope(session, config, fitment)
        if fitment is None:
            raise ContractViolation("derivation input fitment cannot be resolved in the target configuration")
    return fitment


def create_normalized_value(
    session: Session,
    config: VehicleConfiguration,
    payload: NormalizedValueCreate,
    *,
    evidence_links: list[EvidenceLinkCreate] | None = None,
    fitment: VehicleFitment | None = None,
    derivation_rule: DerivationRule | None = None,
    derivation_inputs: list[tuple[NormalizedValue, str]] | None = None,
    result_notes: str | None = None,
    implementation_version: str = "phase-0",
) -> NormalizedValue:
    definition = _parameter_definition(session, payload.parameter_code)
    validate_typed_value_shape(definition, payload)
    validate_registered_semantics(definition, payload)
    validate_load_condition_scope(session, config, payload.load_condition_id)
    validate_width_promotion(payload.parameter_code, payload.semantic_metadata)
    validate_avt_track_candidate(payload.parameter_code, payload.semantic_metadata, payload.evidence_method)
    requested_class = (payload.semantic_metadata or {}).get("ramp_result_class")
    validate_ramp_namespace(
        payload.parameter_code,
        requested_class=requested_class,
        evidence_method=payload.evidence_method,
        derivation_rule_code=derivation_rule.rule_code if derivation_rule else None,
    )
    if payload.evidence_method == EvidenceMethod.DERIVED and derivation_rule is None:
        raise ContractViolation("DERIVED values must be created with a derivation rule and input lineage")
    validate_provenance_payload(
        payload,
        evidence_links=evidence_links,
        derivation_rule=derivation_rule,
        derivation_inputs=derivation_inputs,
    )
    for link_payload in evidence_links or []:
        validate_source_observation_scope(
            session,
            config,
            link_payload.source_observation_id,
            context="evidence link source observation",
        )
    if derivation_rule and derivation_rule.output_parameter_definition_id != definition.id:
        raise ContractViolation("derivation rule output parameter does not match normalized value")
    if derivation_rule and payload.normalization_rule_version != f"{derivation_rule.rule_code}:{derivation_rule.version}":
        raise ContractViolation("normalized value rule version must match the derivation rule identity")

    fitment = _resolve_fitment_scope(session, config, fitment, derivation_inputs)
    dumped = payload.model_dump()
    dumped.pop("parameter_code")
    dumped["evidence_method"] = enum_value(dumped["evidence_method"])
    dumped["resolution_state"] = enum_value(dumped["resolution_state"])
    dumped["verification_state"] = enum_value(dumped["verification_state"])
    dumped["availability_state"] = enum_value(dumped["availability_state"])
    dumped["applicability_grade"] = enum_value(dumped["applicability_grade"])
    dumped["vehicle_configuration_id"] = config.id
    dumped["vehicle_fitment_id"] = fitment.id if fitment else None
    dumped["parameter_definition_id"] = definition.id
    value = NormalizedValue(**dumped)
    session.add(value)
    session.flush()

    for link_payload in evidence_links or []:
        link = EvidenceLink(
            normalized_value_id=value.id,
            source_observation_id=link_payload.source_observation_id,
            evidence_role=enum_value(link_payload.evidence_role),
        )
        session.add(link)

    if derivation_rule is not None:
        assert derivation_rule is not None
        run = DerivationRun(
            derivation_rule_id=derivation_rule.id,
            vehicle_configuration_id=config.id,
            output_normalized_value_id=value.id,
            executed_at=utc_now(),
            implementation_version=implementation_version,
            result_notes=result_notes,
        )
        run.output_value = value
        session.add(run)
        for input_value, input_role in derivation_inputs or []:
            session.add(
                DerivationInput(
                    derivation_run=run,
                    input_normalized_value_id=input_value.id,
                    input_role=input_role,
                )
            )
        session.flush()
    else:
        session.flush()

    validate_persisted_value_contract(session, value)
    return value


def create_parameter_assessment(
    session: Session,
    config: VehicleConfiguration,
    payload: ParameterAssessmentCreate,
    *,
    fitment: VehicleFitment | None = None,
) -> ParameterAssessment:
    definition = _parameter_definition(session, payload.parameter_code)
    validate_parameter_assessment(payload)
    fitment = validate_fitment_scope(session, config, fitment)
    assessment = ParameterAssessment(
        vehicle_configuration_id=config.id,
        vehicle_fitment_id=fitment.id if fitment else None,
        parameter_definition_id=definition.id,
        availability_state=enum_value(payload.availability_state),
        unknown_reason=payload.unknown_reason,
        source_families_searched=payload.source_families_searched,
        search_notes=payload.search_notes,
        assessed_at=payload.assessed_at,
        reviewer=payload.reviewer,
        next_action=payload.next_action,
    )
    session.add(assessment)
    session.flush()
    return assessment


def create_geometry_asset(
    session: Session,
    config: VehicleConfiguration,
    payload: GeometryAssetCreate,
    *,
    fitment: VehicleFitment | None = None,
) -> GeometryAsset:
    validate_geometry_asset_role(payload.geometry_role, payload.coordinate_system_version, payload.geometry_fidelity)
    fitment = validate_fitment_scope(session, config, fitment)
    validate_geometry_references(
        session,
        config,
        fitment=fitment,
        load_condition_id=payload.load_condition_id,
        source_document_id=payload.source_document_id,
        derivation_run_id=payload.derivation_run_id,
    )
    data = payload.model_dump()
    data["geometry_role"] = enum_value(data["geometry_role"])
    data["representation_type"] = enum_value(data["representation_type"])
    data["body_mirror_inclusion"] = enum_value(data["body_mirror_inclusion"])
    data["geometry_method"] = enum_value(data["geometry_method"])
    data["geometry_fidelity"] = enum_value(data["geometry_fidelity"])
    data["vehicle_configuration_id"] = config.id
    data["vehicle_fitment_id"] = fitment.id if fitment else None
    asset = GeometryAsset(**data)
    session.add(asset)
    session.flush()
    return asset
