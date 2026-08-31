from __future__ import annotations

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from app.db.base import Base
from app.db.models import (
    AVTMappingResult,
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
    QAFinding,
    ReadinessResult,
    SourceDocument,
    SourceObservation,
    SteeringRelation,
    VehicleConfiguration,
    VehicleFitment,
)


def test_logical_schema_entities_exist_as_separate_tables():
    required_tables = {
        "manufacturer",
        "vehicle_model",
        "vehicle_configuration",
        "vehicle_fitment",
        "axle",
        "steering_relation",
        "load_condition",
        "source_document",
        "source_observation",
        "parameter_definition",
        "normalized_value",
        "evidence_link",
        "parameter_assessment",
        "derivation_rule",
        "derivation_run",
        "derivation_input",
        "conflict_decision",
        "geometry_asset",
        "readiness_result",
        "qa_finding",
        "avt_mapping_result",
    }
    assert required_tables <= set(Base.metadata.tables)


def test_high_risk_semantics_have_physical_storage_fields():
    assert {"raw_label", "raw_value", "raw_unit"} <= set(SourceObservation.__table__.c.keys())
    assert {"evidence_method", "resolution_state", "verification_state", "availability_state"} <= set(NormalizedValue.__table__.c.keys())
    # Turning reference/axle/wall-envelope scope are an explicit structured JSON
    # contract on the normalized candidate rather than a single overloaded enum.
    assert "semantic_metadata" in NormalizedValue.__table__.c.keys()
    assert {"load_condition_id", "semantic_metadata"} <= set(NormalizedValue.__table__.c.keys())
    assert {"geometry_role", "coordinate_system_version", "geometry_fidelity"} <= set(GeometryAsset.__table__.c.keys())
    assert {"adapter_version", "mapping_payload", "blocker_list"} <= set(AVTMappingResult.__table__.c.keys())
    assert {"steering_role", "linkage_type", "phase_behavior", "relation_function"} <= set(SteeringRelation.__table__.c.keys())


def test_schema_compiles_for_postgresql_dialect():
    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=postgresql.dialect()))
        assert "sqlite" not in ddl.lower()
