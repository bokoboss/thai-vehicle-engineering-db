from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.build_curated_db import BuildError, collect_inventory


ROOT = Path(__file__).resolve().parents[2]
BYD_MANIFEST = ROOT / "data/curation/manifests/sentinel/byd_atto3_my24_extended_local_v1.json"
TRITON_MANIFEST = ROOT / "data/curation/manifests/sentinel/mitsubishi_triton_ultra_4wd_at_2023_v1.json"
FIRST_ACCEPTED_RELEASE = ROOT / "data/curation/releases/release_2026_09_a.json"


def _release_document(paths: list[str], *, release_id: str = "test_release") -> dict:
    return {
        "release_schema_version": "1.0",
        "release_id": release_id,
        "release_date": "2026-09-01",
        "release_status": "ACCEPTED",
        "data_standard_version": "1.0",
        "methodology_versions": {"curation_ingestion_contract": "1.0"},
        "manifest_paths": paths,
    }


def _write_release(tmp_path: Path, paths: list[str], *, release_id: str = "test_release") -> Path:
    release_path = tmp_path / f"{release_id}.json"
    release_path.write_text(
        json.dumps(_release_document(paths, release_id=release_id)),
        encoding="utf-8",
    )
    return release_path


def _copy_manifest(tmp_path: Path, name: str, source: Path = BYD_MANIFEST) -> tuple[Path, dict]:
    document = json.loads(source.read_text(encoding="utf-8"))
    path = tmp_path / name
    path.write_text(json.dumps(document), encoding="utf-8")
    return path, document


def _write_local_release(tmp_path: Path, manifest_paths: list[Path | str]) -> Path:
    relative_paths = [path.name if isinstance(path, Path) else path for path in manifest_paths]
    return _write_release(tmp_path, relative_paths, release_id="local_release")


def test_first_release_explicitly_derives_27_vehicle_inventory():
    inventory = collect_inventory(FIRST_ACCEPTED_RELEASE)

    assert inventory.release.release_id == "release_2026_09_a"
    assert len(inventory.release.manifest_paths) == 27
    assert len(inventory.manifests) == 27
    assert len(inventory.stable_vehicle_codes) == 27
    assert len(set(inventory.stable_vehicle_codes)) == 27
    assert inventory.expected_counts == {
        "vehicles": 27,
        "source_entries": 75,
        "sources": 74,
        "observations": 268,
        "values": 319,
        "assessments": 80,
        "loads": 26,
        "fitments": 14,
        "axles": 0,
        "steering_relations": 0,
        "geometry_assets": 0,
        "conflict_decisions": 0,
        "conflicting_values": 2,
    }
    assert all(
        value.evidence_method.value not in {"DERIVED", "ESTIMATED"}
        for manifest in inventory.manifests
        for value in manifest.values
    )


def test_unlisted_manifest_file_is_ignored(tmp_path: Path):
    listed, _ = _copy_manifest(tmp_path, "listed.json")
    unlisted, unlisted_document = _copy_manifest(tmp_path, "unlisted.json", TRITON_MANIFEST)
    release_path = _write_local_release(tmp_path, [listed])

    inventory = collect_inventory(release_path, root=tmp_path)

    assert inventory.expected_counts["vehicles"] == 1
    assert inventory.paths == (listed.resolve(),)
    assert unlisted.exists()
    assert unlisted_document["vehicle"]["stable_vehicle_code"] not in inventory.stable_vehicle_codes


def test_release_with_n_listed_manifests_derives_n_vehicles(tmp_path: Path):
    first, _ = _copy_manifest(tmp_path, "first.json")
    second, second_document = _copy_manifest(tmp_path, "second.json", TRITON_MANIFEST)
    release_path = _write_local_release(tmp_path, [first, second])

    inventory = collect_inventory(release_path, root=tmp_path)

    assert len(inventory.manifests) == 2
    assert inventory.expected_counts["vehicles"] == 2
    assert second_document["vehicle"]["stable_vehicle_code"] in inventory.stable_vehicle_codes


def test_listed_missing_manifest_is_rejected(tmp_path: Path):
    release_path = _write_local_release(tmp_path, ["missing.json"])

    with pytest.raises(BuildError, match="listed manifest is missing"):
        collect_inventory(release_path, root=tmp_path)


def test_duplicate_manifest_path_is_rejected(tmp_path: Path):
    manifest, _ = _copy_manifest(tmp_path, "same.json")
    release_path = _write_local_release(tmp_path, [manifest.name, manifest.name])

    with pytest.raises(BuildError, match="duplicate manifest path"):
        collect_inventory(release_path, root=tmp_path)


def test_duplicate_record_id_is_rejected(tmp_path: Path):
    first, first_document = _copy_manifest(tmp_path, "first.json")
    second, _ = _copy_manifest(tmp_path, "second.json")
    assert first_document["record_id"]
    release_path = _write_local_release(tmp_path, [first, second])

    with pytest.raises(BuildError, match="duplicate record_id"):
        collect_inventory(release_path, root=tmp_path)


def test_duplicate_stable_vehicle_code_is_rejected(tmp_path: Path):
    first, _ = _copy_manifest(tmp_path, "first.json")
    second, second_document = _copy_manifest(tmp_path, "second.json")
    second_document["record_id"] = "COPY-RECORD-ID"
    second.write_text(json.dumps(second_document), encoding="utf-8")
    release_path = _write_local_release(tmp_path, [first, second])

    with pytest.raises(BuildError, match="duplicate stable_vehicle_code"):
        collect_inventory(release_path, root=tmp_path)


def test_incompatible_source_code_reuse_is_rejected(tmp_path: Path):
    first, _ = _copy_manifest(tmp_path, "first.json")
    second, second_document = _copy_manifest(tmp_path, "second.json")
    second_document["record_id"] = "COPY-RECORD-ID"
    second_document["vehicle"]["stable_vehicle_code"] = "th-byd-atto3-my24-extended-local-copy"
    second_document["sources"][0]["title"] = "Incompatible source metadata"
    second.write_text(json.dumps(second_document), encoding="utf-8")
    release_path = _write_local_release(tmp_path, [first, second])

    with pytest.raises(BuildError, match="incompatible manifest metadata"):
        collect_inventory(release_path, root=tmp_path)


def test_phase0_fixture_identity_is_rejected(tmp_path: Path):
    manifest, document = _copy_manifest(tmp_path, "fixture.json")
    document["vehicle"]["stable_vehicle_code"] = "FIXTURE-RELEASE-TEST"
    manifest.write_text(json.dumps(document), encoding="utf-8")
    release_path = _write_local_release(tmp_path, [manifest])

    with pytest.raises(BuildError, match="Phase 0 fixture identities"):
        collect_inventory(release_path, root=tmp_path)


@pytest.mark.parametrize("evidence_method", ["DERIVED", "ESTIMATED"])
def test_direct_derived_or_estimated_manifest_value_is_rejected(tmp_path: Path, evidence_method: str):
    manifest, document = _copy_manifest(tmp_path, "invalid-value.json")
    document["values"][0]["evidence_method"] = evidence_method
    manifest.write_text(json.dumps(document), encoding="utf-8")
    release_path = _write_local_release(tmp_path, [manifest])

    with pytest.raises(BuildError, match="does not allow direct"):
        collect_inventory(release_path, root=tmp_path)


def test_adding_a_valid_manifest_changes_inventory_without_builder_edit(tmp_path: Path):
    first, _ = _copy_manifest(tmp_path, "first.json")
    second, second_document = _copy_manifest(tmp_path, "second.json")
    second_document["record_id"] = "COPY-RECORD-ID"
    second_document["vehicle"]["stable_vehicle_code"] = "th-byd-atto3-my24-extended-local-copy"
    second.write_text(json.dumps(second_document), encoding="utf-8")

    one_manifest_release = _write_release(tmp_path, [first.name], release_id="one_manifest")
    two_manifest_release = _write_release(tmp_path, [first.name, second.name], release_id="two_manifests")

    one = collect_inventory(one_manifest_release, root=tmp_path)
    two = collect_inventory(two_manifest_release, root=tmp_path)

    assert one.expected_counts["vehicles"] == 1
    assert two.expected_counts["vehicles"] == 2
    assert two.stable_vehicle_codes == (one.stable_vehicle_codes[0], second_document["vehicle"]["stable_vehicle_code"])
