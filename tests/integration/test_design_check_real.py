from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.curate.loader import import_manifest, initialize_registry
from app.db.base import Base
from app.db.repositories import get_vehicle, list_vehicles
from app.db.session import get_session, make_engine
from app.domain.design_check import (
    DesignCheckInputs,
    DesignCheckState,
    evaluate_height_constraint,
    evaluate_turning_constraint,
    evaluate_width_constraint,
)
from app.main import app
from app.services.design_check import design_vehicle_from_configuration, evaluate_configurations
from scripts.build_wave1_curated_db import collect_inventory


@pytest.fixture
def wave1_session(tmp_path: Path) -> Generator[Session, None, None]:
    """Build the accepted 21-manifest curation into an isolated test database."""

    database_path = tmp_path / "wave1-design-check.sqlite"
    engine = make_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = factory()
    initialize_registry(session)
    for manifest in collect_inventory().manifests:
        import_manifest(session, manifest)
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def wave1_client(wave1_session: Session) -> Generator[TestClient, None, None]:
    def override_session():
        yield wave1_session

    app.dependency_overrides[get_session] = override_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def exact_vehicle(session: Session, code: str):
    config = get_vehicle(session, code)
    assert config is not None
    return design_vehicle_from_configuration(config)


def test_real_curated_volvo_width_definitions_and_height_scope_are_preserved(wave1_session: Session):
    config = get_vehicle(wave1_session, "th-volvo-ex30-ultra-smer-my2026-19")
    assert config is not None
    vehicle = design_vehicle_from_configuration(config)

    widths = {
        candidate.parameter_code: candidate
        for candidate in vehicle.values
        if candidate.parameter_code.startswith("overall_width_")
    }
    assert {
        widths["overall_width_body_mm"].value,
        widths["overall_width_including_mirrors_mm"].value,
        widths["overall_width_mirrors_folded_mm"].value,
    } == {1838, 2032, 1940}
    assert widths["overall_width_body_mm"].semantic_metadata["width_envelope_definition"] == "BODY_EXCLUDING_MIRRORS"
    assert widths["overall_width_including_mirrors_mm"].semantic_metadata["width_envelope_definition"] == "INCLUDING_MIRRORS_OPEN"
    assert widths["overall_width_mirrors_folded_mm"].semantic_metadata["width_envelope_definition"] == "INCLUDING_MIRRORS_FOLDED"

    width_inputs = {
        "BODY_EXCLUDING_MIRRORS": ("overall_width_body_mm", "body excluding mirrors"),
        "INCLUDING_MIRRORS_OPEN": ("overall_width_including_mirrors_mm", "mirrors open"),
        "INCLUDING_MIRRORS_FOLDED": ("overall_width_mirrors_folded_mm", "mirrors folded"),
    }
    for envelope, (parameter_code, semantic_label) in width_inputs.items():
        result = evaluate_width_constraint(
            vehicle,
            DesignCheckInputs(
                available_clear_width_mm=2100,
                lateral_allowance_each_side_mm=0,
                width_envelope=envelope,
            ),
        )
        assert result.state == DesignCheckState.PASS
        assert result.vehicle_value == widths[parameter_code].value
        assert semantic_label in result.semantic_cue.lower()

    raw_clearances = [
        value.numeric_value
        for value in config.normalized_values
        if value.parameter_definition.parameter_code == "clearance_value_mm"
    ]
    assert raw_clearances == [171]
    height = evaluate_height_constraint(
        vehicle,
        DesignCheckInputs(available_clear_height_mm=1600),
    )
    assert height.state == DesignCheckState.PASS
    assert height.vehicle_value == 1550
    assert all(candidate.parameter_code != "clearance_value_mm" for candidate in vehicle.values)


def test_real_curated_reported_width_is_not_promoted_to_body_width(wave1_session: Session):
    config = get_vehicle(wave1_session, "th-byd-atto3-my24-extended-local")
    assert config is not None
    vehicle = design_vehicle_from_configuration(config)

    result = evaluate_width_constraint(
        vehicle,
        DesignCheckInputs(
            available_clear_width_mm=2100,
            lateral_allowance_each_side_mm=0,
            width_envelope="BODY_EXCLUDING_MIRRORS",
        ),
    )

    assert result.state == DesignCheckState.INDETERMINATE
    assert result.vehicle_value is None
    assert "cannot be substituted" in result.reason
    assert "OEM definition unspecified" in result.reason

    clearances = [
        value
        for value in config.normalized_values
        if value.parameter_definition.parameter_code == "clearance_value_mm"
    ]
    assert sorted(value.numeric_value for value in clearances) == [150, 175]
    assert len({value.load_condition_id for value in clearances}) == 2
    height = evaluate_height_constraint(
        vehicle,
        DesignCheckInputs(available_clear_height_mm=1600),
    )
    assert height.state == DesignCheckState.FAIL
    assert height.vehicle_value == 1615
    assert height.margin == -15
    assert all(candidate.parameter_code != "clearance_value_mm" for candidate in vehicle.values)


def test_real_curated_commuter_fails_height_while_passenger_vehicle_passes(wave1_session: Session):
    commuter = exact_vehicle(wave1_session, "th-toyota-commuter-28-at-highroof-revision-2568")
    accord = exact_vehicle(wave1_session, "th-honda-accord-ehev-rs-release-2025-08-22")
    inputs = DesignCheckInputs(available_clear_height_mm=2100)

    commuter_result = evaluate_height_constraint(commuter, inputs)
    accord_result = evaluate_height_constraint(accord, inputs)

    assert commuter_result.state == DesignCheckState.FAIL
    assert commuter_result.vehicle_value == 2280
    assert commuter_result.margin == -180
    assert accord_result.state == DesignCheckState.PASS
    assert accord_result.vehicle_value == 1449


def test_real_curated_tesla_turning_wording_remains_non_inferred(wave1_session: Session):
    vehicle = exact_vehicle(wave1_session, "th-tesla-model3-premium-long-range-rwd-2024plus")
    raw = [item for item in vehicle.values if item.parameter_code == "oem_turning_value_text"]
    assert [item.value for item in raw] == ["11.7 m curb-to-curb turning circle"]
    assert not any(item.parameter_code == "turning_radius_normalized_m" for item in vehicle.values)

    result = evaluate_turning_constraint(
        vehicle,
        DesignCheckInputs(
            maximum_turning_value_m=12,
            turning_input_shape="DIAMETER",
            turning_reference="CURB_TO_CURB",
        ),
    )

    assert result.state == DesignCheckState.INDETERMINATE
    assert "not parsed" in result.reason
    assert "halved" in result.reason


def test_real_curated_triton_turning_semantics_are_not_reinterpreted(wave1_session: Session):
    vehicle = exact_vehicle(wave1_session, "th-mitsubishi-triton-ultra-4wd-at-release-2023")
    candidate = next(item for item in vehicle.values if item.parameter_code == "turning_radius_normalized_m")
    assert candidate.value == 6.2
    assert candidate.semantic_metadata == {
        "turning_radius_or_diameter": "RADIUS",
        "turning_reference": "OEM_UNSPECIFIED",
        "turning_axle_scope": "OEM_UNSPECIFIED",
    }

    result = evaluate_turning_constraint(
        vehicle,
        DesignCheckInputs(
            maximum_turning_value_m=12,
            turning_input_shape="DIAMETER",
            turning_reference="CURB_TO_CURB",
        ),
    )

    assert result.state == DesignCheckState.INDETERMINATE
    assert "OEM reference unspecified" in result.reason
    assert "OEM reference unspecified" in result.semantic_cue
    assert "OEM axle scope unspecified" in result.semantic_cue


def test_real_curated_conflicting_volvo_turning_values_remain_blocked(wave1_session: Session):
    config = get_vehicle(wave1_session, "th-volvo-ex30-ultra-smer-my2026-19")
    assert config is not None
    raw_values = [
        value
        for value in config.normalized_values
        if value.parameter_definition.parameter_code == "oem_turning_value_text"
    ]
    assert {value.resolution_state for value in raw_values} == {"CONFLICTING"}
    assert {value.text_value for value in raw_values} == {"10.7 m", "11 m"}

    result = evaluate_turning_constraint(
        design_vehicle_from_configuration(config),
        DesignCheckInputs(
            maximum_turning_value_m=12,
            turning_input_shape="DIAMETER",
            turning_reference="CURB_TO_CURB",
        ),
    )

    assert result.state == DesignCheckState.INDETERMINATE
    assert "conflicting" in result.reason.lower()
    assert "not parsed" in result.reason


def test_real_curated_candidate_filtering_keeps_vehicle_segments_explicit(wave1_session: Session):
    all_configs = list_vehicles(wave1_session)
    electric_crossovers = list_vehicles(
        wave1_session,
        body_style="Battery-electric crossover/SUV",
    )
    assert all_configs
    assert electric_crossovers
    assert len(electric_crossovers) < len(all_configs)
    assert all(config.body_style == "Battery-electric crossover/SUV" for config in electric_crossovers)

    inputs = DesignCheckInputs(available_clear_height_mm=2100)
    report = evaluate_configurations(
        [get_vehicle(wave1_session, config.stable_vehicle_code) for config in electric_crossovers],
        inputs,
    )
    assert len(report.vehicles) == len(electric_crossovers)
    assert {item.vehicle.body_style for item in report.vehicles} == {"Battery-electric crossover/SUV"}


def test_design_check_route_preserves_query_state_and_exposes_result_matrix(wave1_client: TestClient):
    response = wave1_client.get(
        "/design-check",
        params={
            "available_clear_height_mm": "2100",
            "vertical_allowance_mm": "100",
            "maximum_vehicle_length_mm": "5000",
            "body_style": "Battery-electric crossover/SUV",
            "sort": "height",
        },
    )

    assert response.status_code == 200
    html = response.text
    assert "DESIGN_CHECK_V1" in html
    assert 'value="2100"' in html
    assert 'value="100"' in html
    assert 'value="5000"' in html
    assert 'value="Battery-electric crossover/SUV" selected' in html
    assert "PASS" in html
    assert "FAIL" in html
    assert "INDETERMINATE" in html
    assert "Closest active limit" in html
    assert "Vehicle value" in html
    assert "Effective limit" in html
    assert "Signed margin" in html
    assert "Evidence / detail" in html

    mixed_result_response = wave1_client.get(
        "/design-check",
        params={
            "available_clear_height_mm": "2100",
            "maximum_vehicle_length_mm": "5000",
        },
    )
    assert mixed_result_response.status_code == 200
    assert "Largest exceedance" in mixed_result_response.text

    indeterminate_response = wave1_client.get(
        "/design-check",
        params={
            "available_clear_width_mm": "2100",
            "lateral_allowance_each_side_mm": "0",
            "width_envelope": "BODY_EXCLUDING_MIRRORS",
            "body_style": "Battery-electric crossover/SUV",
        },
    )
    assert indeterminate_response.status_code == 200
    assert "Decision blocker(s)" in indeterminate_response.text


def test_design_check_route_rejects_incomplete_active_inputs(client: TestClient):
    response = client.get(
        "/design-check",
        params={"available_clear_width_mm": "2100"},
    )

    assert response.status_code == 200
    assert "Choose the vehicle width envelope" in response.text
    assert "Enter the required lateral allowance per side" in response.text
    assert "Run design check" in response.text
