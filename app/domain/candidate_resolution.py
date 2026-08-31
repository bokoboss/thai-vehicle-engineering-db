from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ConflictDecision, NormalizedValue, VehicleConfiguration, VehicleFitment
from app.domain.enums import (
    AvailabilityState,
    DecisionState,
    ResolutionState,
    VerificationState,
)


CONFLICT_STATES = {
    ResolutionState.CONFLICTING.value,
    ResolutionState.PREFERRED_WITH_CONFLICT.value,
}


@dataclass(frozen=True)
class CandidateResolution:
    value: NormalizedValue | None
    conflict_decision_id: str | None = None
    reason: str | None = None


def _active_decision_for(
    session: Session,
    config: VehicleConfiguration,
    value: NormalizedValue,
    fitment: VehicleFitment | None,
) -> ConflictDecision | None:
    """Return an active auditable selection only when every scope matches."""

    if value.vehicle_configuration_id != config.id:
        return None
    if fitment is None:
        if value.vehicle_fitment_id is not None:
            return None
    elif value.vehicle_fitment_id not in {None, fitment.id}:
        return None

    statement = select(ConflictDecision).where(
        ConflictDecision.vehicle_configuration_id == config.id,
        ConflictDecision.parameter_definition_id == value.parameter_definition_id,
        ConflictDecision.selected_normalized_value_id == value.id,
        ConflictDecision.decision_state == DecisionState.SELECTED.value,
        ConflictDecision.superseded_by_decision_id.is_(None),
    )
    decisions = list(session.scalars(statement).all())
    if len(decisions) != 1:
        return None
    decision = decisions[0]
    if decision.selected_normalized_value_id != value.id:
        return None
    if decision.vehicle_configuration_id != value.vehicle_configuration_id:
        return None
    if decision.parameter_definition_id != value.parameter_definition_id:
        return None
    return decision


def resolve_engineering_candidate(
    session: Session,
    config: VehicleConfiguration,
    values: list[NormalizedValue],
    parameter_code: str,
    *,
    fitment: VehicleFitment | None = None,
) -> CandidateResolution:
    """Resolve one engineering candidate without trusting preference metadata.

    A conflicting candidate is usable only when one active, non-superseded
    conflict decision selects that exact value in the same configuration,
    parameter and applicable fitment scope.
    """

    matches = [
        value
        for value in values
        if value.parameter_definition.parameter_code == parameter_code
        and value.vehicle_configuration_id == config.id
        and (
            (fitment is None and value.vehicle_fitment_id is None)
            or (fitment is not None and value.vehicle_fitment_id in {None, fitment.id})
        )
        and value.availability_state == AvailabilityState.AVAILABLE.value
        and value.verification_state != VerificationState.REJECTED.value
        and value.resolution_state not in {
            ResolutionState.SUPERSEDED.value,
            ResolutionState.NOT_APPLICABLE.value,
        }
    ]
    if not matches:
        return CandidateResolution(None, reason=f"no eligible available value: {parameter_code}")

    eligible: list[tuple[NormalizedValue, ConflictDecision | None]] = []
    for value in matches:
        decision = None
        if value.resolution_state in CONFLICT_STATES:
            decision = _active_decision_for(session, config, value, fitment)
            if decision is None:
                continue
        eligible.append((value, decision))

    if not eligible:
        return CandidateResolution(None, reason=f"no auditable resolution for available value: {parameter_code}")

    selected_conflicts = [(value, decision) for value, decision in eligible if decision is not None]
    if len(selected_conflicts) > 1:
        return CandidateResolution(None, reason=f"multiple active conflict selections for: {parameter_code}")
    if selected_conflicts:
        value, decision = selected_conflicts[0]
        return CandidateResolution(value, conflict_decision_id=decision.id)

    preferred = [value for value, _ in eligible if value.preferred]
    if preferred:
        return CandidateResolution(preferred[0])
    return CandidateResolution(eligible[0][0])
