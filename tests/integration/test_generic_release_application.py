from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.session import get_session, make_engine
from app.main import app
from app.curate.loader import import_manifest, initialize_registry
from scripts.build_curated_db import collect_inventory


NEW_RELEASE_CODES = {
    "th-honda-crv-ehev-rs4wd-minorchange-release-2025-11-28",
    "th-kia-carnival-hev-7seat-luxury-release-2025-10-03",
    "th-lexus-lm350h-executive-7seat-allnew-2023",
    "th-nissan-serena-epower-highway-star-release-2025-03-24",
    "th-toyota-corolla-cross-hev-premium-luxury-revision-2569",
    "th-toyota-innova-zenix-hev-premium-revision-2568",
}
BYD_CODE = "th-byd-atto3-my24-extended-local"
KIA_CODE = "th-kia-carnival-hev-7seat-luxury-release-2025-10-03"
KIA_POWERTRAIN = "1.6L turbo gasoline hybrid / 6-speed automatic"


@pytest.fixture(scope="module")
def generic_release_session(tmp_path_factory: pytest.TempPathFactory) -> Generator[tuple[Session, object, Path], None, None]:
    database_path = tmp_path_factory.mktemp("generic-release") / "release.sqlite"
    engine = make_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = factory()
    initialize_registry(session)
    inventory = collect_inventory()
    for manifest in inventory.manifests:
        import_manifest(session, manifest)
    try:
        yield session, inventory, database_path
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def generic_release_client(generic_release_session):
    session, _inventory, _database_path = generic_release_session

    def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def test_generic_27_release_is_visible_without_application_catalog_edits(
    generic_release_client: TestClient,
    generic_release_session,
):
    _session, inventory, _database_path = generic_release_session
    response = generic_release_client.get("/api/vehicles")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 27
    assert {item["stable_vehicle_code"] for item in payload["items"]} == set(inventory.stable_vehicle_codes)
    assert NEW_RELEASE_CODES.issubset({item["stable_vehicle_code"] for item in payload["items"]})
    assert generic_release_client.get("/", follow_redirects=False).status_code == 307


def test_new_release_filters_detail_compare_design_issues_and_exports_are_data_driven(
    generic_release_client: TestClient,
):
    kia = generic_release_client.get("/api/vehicles", params={"manufacturer": "Kia"})
    assert kia.status_code == 200
    assert kia.json()["count"] == 1
    assert kia.json()["items"][0]["stable_vehicle_code"] == KIA_CODE

    body_filtered = generic_release_client.get(
        "/api/vehicles", params={"body_style": "Large hybrid MPV"}
    )
    assert body_filtered.status_code == 200
    assert body_filtered.json()["count"] == 1
    assert body_filtered.json()["items"][0]["stable_vehicle_code"] == KIA_CODE

    vehicles_page = generic_release_client.get("/vehicles", params={"manufacturer": "Kia"})
    assert vehicles_page.status_code == 200
    assert KIA_CODE in vehicles_page.text

    for code in sorted(NEW_RELEASE_CODES):
        assert generic_release_client.get(f"/api/vehicles/{code}").status_code == 200
        assert generic_release_client.get(f"/vehicles/{code}").status_code == 200

    compare = generic_release_client.get(
        "/compare", params={"codes": f"{BYD_CODE},{KIA_CODE}"}
    )
    assert compare.status_code == 200
    assert BYD_CODE in compare.text
    assert KIA_CODE in compare.text

    filtered_compare = generic_release_client.get(
        "/compare",
        params={"powertrain": KIA_POWERTRAIN, "vehicle_1": KIA_CODE},
    )
    assert filtered_compare.status_code == 200
    assert KIA_CODE in filtered_compare.text

    design_check = generic_release_client.get(
        "/design-check",
        params={
            "q": KIA_CODE,
            "available_clear_width_mm": "3000",
            "lateral_allowance_each_side_mm": "0",
            "width_envelope": "BODY_EXCLUDING_MIRRORS",
            "maximum_turning_value_m": "20",
            "turning_input_shape": "RADIUS",
            "turning_reference": "CURB_TO_CURB",
        },
    )
    assert design_check.status_code == 200
    assert "INDETERMINATE" in design_check.text

    issues = generic_release_client.get("/api/issues")
    assert issues.status_code == 200
    issue_codes = {item["vehicle"] for item in issues.json()["items"]}
    assert NEW_RELEASE_CODES.issubset(issue_codes)

    exported = generic_release_client.get(
        "/exports/vehicles.csv", params={"codes": f"{BYD_CODE},{KIA_CODE}"}
    )
    assert exported.status_code == 200
    export_text = exported.content.decode("utf-8-sig")
    assert BYD_CODE in export_text
    assert KIA_CODE in export_text
