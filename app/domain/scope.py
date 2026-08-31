from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import (
    Axle,
    DerivationRun,
    LoadCondition,
    SourceDocument,
    SourceObservation,
    VehicleConfiguration,
    VehicleFitment,
)
from app.domain.validation import ContractViolation


def validate_fitment_scope(
    session: Session,
    config: VehicleConfiguration,
    fitment: VehicleFitment | None,
) -> VehicleFitment | None:
    """Require an optional fitment to be persisted under the target configuration."""

    if fitment is None:
        return None
    persisted = session.get(VehicleFitment, fitment.id)
    if persisted is None:
        raise ContractViolation("fitment scope does not reference a known fitment")
    if persisted.vehicle_configuration_id != config.id:
        raise ContractViolation("fitment scope does not belong to the target configuration")
    return persisted


def validate_load_condition_scope(
    session: Session,
    config: VehicleConfiguration,
    load_condition_id: str | None,
) -> LoadCondition | None:
    """Resolve a load condition and allow only generic or target-configuration scope."""

    if load_condition_id is None or not str(load_condition_id).strip():
        return None
    condition = session.get(LoadCondition, load_condition_id)
    if condition is None:
        raise ContractViolation("load condition does not reference a known load condition")
    if condition.vehicle_configuration_id not in {None, config.id}:
        raise ContractViolation("load condition does not belong to the target configuration")
    return condition


def validate_source_observation_scope(
    session: Session,
    config: VehicleConfiguration,
    source_observation_id: str,
    *,
    context: str = "source observation",
) -> SourceObservation:
    """Require an observation to have resolved identity for the target configuration."""

    observation = session.get(SourceObservation, source_observation_id)
    if observation is None:
        raise ContractViolation(f"{context} does not reference a known source observation")
    if observation.vehicle_configuration_id is None:
        raise ContractViolation(f"{context} is unresolved and cannot qualify the target configuration")
    if observation.vehicle_configuration_id != config.id:
        raise ContractViolation(f"{context} does not belong to the target configuration")
    return observation


def validate_axle_scope(
    session: Session,
    config: VehicleConfiguration,
    axle_id: str,
) -> Axle:
    """Require an axle to be persisted under the target configuration."""

    axle = session.get(Axle, axle_id)
    if axle is None:
        raise ContractViolation("steering relation axle does not reference a known axle")
    if axle.vehicle_configuration_id != config.id:
        raise ContractViolation("steering relation axle does not belong to the target configuration")
    return axle


def validate_geometry_references(
    session: Session,
    config: VehicleConfiguration,
    *,
    fitment: VehicleFitment | None,
    load_condition_id: str | None,
    source_document_id: str | None,
    derivation_run_id: str | None,
) -> None:
    """Validate every cross-table reference used by a geometry asset."""

    validate_fitment_scope(session, config, fitment)
    validate_load_condition_scope(session, config, load_condition_id)

    if source_document_id is not None and not str(source_document_id).strip():
        raise ContractViolation("geometry source_document_id must reference a known source document")
    if source_document_id is not None and session.get(SourceDocument, source_document_id) is None:
        raise ContractViolation("geometry source_document_id does not reference a known source document")

    if derivation_run_id is None:
        return
    if not str(derivation_run_id).strip():
        raise ContractViolation("geometry derivation_run_id must reference a known derivation run")
    run = session.get(DerivationRun, derivation_run_id)
    if run is None:
        raise ContractViolation("geometry derivation_run_id does not reference a known derivation run")
    if run.vehicle_configuration_id != config.id:
        raise ContractViolation("geometry derivation run does not belong to the target configuration")

    # A run may produce geometry directly, so output_normalized_value_id can be
    # null. When it exists, do not let a fitment-specific normalized output lose
    # its scope while being attached to a geometry asset.
    output_value = run.output_value
    if output_value is None:
        return
    if output_value.vehicle_configuration_id != config.id:
        raise ContractViolation("geometry derivation output does not belong to the target configuration")
    if fitment is None and output_value.vehicle_fitment_id is not None:
        raise ContractViolation("fitment-specific derivation output requires matching geometry fitment scope")
    if fitment is not None and output_value.vehicle_fitment_id not in {None, fitment.id}:
        raise ContractViolation("geometry derivation output does not match the geometry fitment scope")
