from __future__ import annotations

import hashlib
import json
import os
import shutil
from argparse import Namespace
from pathlib import Path

import pytest

from scripts import build_curated_db as builder


ROOT = Path(__file__).resolve().parents[2]
BYD_MANIFEST = ROOT / "data/curation/manifests/sentinel/byd_atto3_my24_extended_local_v1.json"


def _write_release(tmp_path: Path, paths: list[str], release_id: str) -> Path:
    document = {
        "release_schema_version": "1.0",
        "release_id": release_id,
        "release_date": "2026-09-01",
        "release_status": "ACCEPTED",
        "data_standard_version": "1.0",
        "methodology_versions": {"curation_ingestion_contract": "1.0"},
        "manifest_paths": paths,
    }
    path = tmp_path / f"{release_id}.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def _build_args(release_path: Path, tmp_path: Path) -> Namespace:
    return Namespace(
        release=release_path,
        staging=tmp_path / "staging.db",
        final=tmp_path / "accepted.db",
        csv=tmp_path / "export.csv",
        xlsx=tmp_path / "export.xlsx",
        qualification=tmp_path / "qualification.json",
        no_promote=False,
        replace_final=True,
    )


def _copy_fingerprint_inputs(root: Path) -> Path:
    manifest = root / "data/curation/manifests/sentinel/byd.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BYD_MANIFEST, manifest)
    registry = root / "data/reference/parameter_registry_v1.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "data/reference/parameter_registry_v1.json", registry)
    return _write_release(
        root,
        [manifest.relative_to(root).as_posix()],
        "fingerprint_release",
    )


def test_fingerprint_is_logical_path_independent_and_detects_content_changes(tmp_path: Path):
    first_root = tmp_path / "repo-one"
    second_root = tmp_path / "repo-two"
    first_release = _copy_fingerprint_inputs(first_root)
    second_release = _copy_fingerprint_inputs(second_root)

    first = builder.collect_inventory(first_release, root=first_root)
    second = builder.collect_inventory(second_release, root=second_root)

    assert first.stable_vehicle_codes == second.stable_vehicle_codes
    assert first.build_input_digest_sha256 == second.build_input_digest_sha256
    assert "\\" not in first.build_input_digest_sha256

    changed_manifest = first_root / "data/curation/manifests/sentinel/byd.json"
    document = json.loads(changed_manifest.read_text(encoding="utf-8"))
    document["sources"][0]["notes"] = "A reviewed source-content correction with the same vehicle identity."
    changed_manifest.write_text(json.dumps(document), encoding="utf-8")
    changed = builder.collect_inventory(first_release, root=first_root)

    assert changed.stable_vehicle_codes == first.stable_vehicle_codes
    assert changed.build_input_digest_sha256 != first.build_input_digest_sha256


def test_fingerprint_changes_for_registry_and_build_compatibility_inputs(tmp_path: Path):
    release = _copy_fingerprint_inputs(tmp_path)
    inventory = builder.collect_inventory(release, root=tmp_path)
    registry_path = tmp_path / "data/reference/parameter_registry_v1.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["registry_version"] = "test-compatible-change"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")

    changed_registry = builder.collect_inventory(release, root=tmp_path)
    assert changed_registry.build_input_digest_sha256 != inventory.build_input_digest_sha256

    assert builder.build_input_fingerprint(
        changed_registry,
        root=tmp_path,
        compatibility_version="test-compatible-change",
    ) != changed_registry.build_input_digest_sha256


def test_successful_promotion_writes_matching_database_metadata(tmp_path: Path):
    release = _write_release(tmp_path, [
        "data/curation/manifests/sentinel/byd_atto3_my24_extended_local_v1.json",
    ], "metadata_release")
    report = builder.build(_build_args(release, tmp_path))
    database = tmp_path / "accepted.db"
    metadata_path = builder.metadata_path_for(database)

    assert report["build_input_digest_sha256"]
    assert metadata_path.is_file()
    metadata = builder.validate_promoted_database_metadata(database)
    assert metadata["release_id"] == "metadata_release"
    assert metadata["vehicle_count"] == 1
    assert metadata["database_sha256"] == hashlib.sha256(database.read_bytes()).hexdigest()
    assert metadata["promoted_database_sha256"] == metadata["database_sha256"]
    assert metadata["build_input_digest_sha256"] == report["build_input_digest_sha256"]
    assert metadata["promotion_result"] == "PROMOTED"


def test_replacement_preserves_matching_previous_database_and_metadata(tmp_path: Path):
    first_release = _write_release(tmp_path, [
        "data/curation/manifests/sentinel/byd_atto3_my24_extended_local_v1.json",
    ], "first_metadata_release")
    builder.build(_build_args(first_release, tmp_path))
    database = tmp_path / "accepted.db"
    metadata_path = builder.metadata_path_for(database)
    first_database_bytes = database.read_bytes()
    first_metadata_bytes = metadata_path.read_bytes()

    second_release = _write_release(tmp_path, [
        "data/curation/manifests/sentinel/mitsubishi_triton_ultra_4wd_at_2023_v1.json",
    ], "second_metadata_release")
    builder.build(_build_args(second_release, tmp_path))

    previous = tmp_path / "accepted.db.previous"
    previous_metadata = builder.metadata_path_for(previous)
    assert previous.read_bytes() == first_database_bytes
    assert previous_metadata.read_bytes() == first_metadata_bytes
    assert builder.validate_promoted_database_metadata(previous)["release_id"] == "first_metadata_release"


def test_failed_staging_build_leaves_accepted_database_and_metadata_unchanged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    first_release = _write_release(tmp_path, [
        "data/curation/manifests/sentinel/byd_atto3_my24_extended_local_v1.json",
    ], "accepted_before_failure")
    builder.build(_build_args(first_release, tmp_path))
    database = tmp_path / "accepted.db"
    metadata_path = builder.metadata_path_for(database)
    before_database = database.read_bytes()
    before_metadata = metadata_path.read_bytes()

    def fail_qa(session, inventory):
        del session, inventory
        raise builder.BuildError("injected v2 staging failure")

    monkeypatch.setattr(builder, "_qa_database", fail_qa)
    second_release = _write_release(tmp_path, [
        "data/curation/manifests/sentinel/mitsubishi_triton_ultra_4wd_at_2023_v1.json",
    ], "failed_metadata_release")
    with pytest.raises(builder.BuildError, match="injected v2 staging failure"):
        builder.build(_build_args(second_release, tmp_path))

    assert database.read_bytes() == before_database
    assert metadata_path.read_bytes() == before_metadata


def test_database_sha_mismatch_against_metadata_is_detected(tmp_path: Path):
    release = _write_release(tmp_path, [
        "data/curation/manifests/sentinel/byd_atto3_my24_extended_local_v1.json",
    ], "hash_mismatch_release")
    builder.build(_build_args(release, tmp_path))
    database = tmp_path / "accepted.db"
    database.write_bytes(database.read_bytes() + b"tampered")

    with pytest.raises(builder.BuildError, match="SHA-256 mismatch against metadata"):
        builder.validate_promoted_database_metadata(database)


def test_no_promote_writes_staging_metadata_without_promoting(tmp_path: Path):
    release = _write_release(tmp_path, [
        "data/curation/manifests/sentinel/byd_atto3_my24_extended_local_v1.json",
    ], "staging_metadata_release")
    args = _build_args(release, tmp_path)
    args.no_promote = True
    report = builder.build(args)

    staging = tmp_path / "staging.db"
    metadata = builder.validate_database_metadata(staging)
    assert report["promoted_database"] is None
    assert metadata["promotion_result"] == "NOT_REQUESTED"
    assert not (tmp_path / "accepted.db").exists()


def test_failed_pair_promotion_restores_accepted_db_and_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    staging = tmp_path / "staging.db"
    final = tmp_path / "accepted.db"
    staging.write_bytes(b"candidate")
    builder.metadata_path_for(staging).write_text("candidate-marker", encoding="utf-8")
    final.write_bytes(b"accepted")
    final_metadata = builder.metadata_path_for(final)
    final_metadata.write_text("accepted-marker", encoding="utf-8")
    before_final = final.read_bytes()
    before_metadata = final_metadata.read_bytes()
    candidate_hash = hashlib.sha256(staging.read_bytes()).hexdigest()

    original_replace = os.replace

    def fail_final_metadata(source, destination):
        if Path(destination).resolve() == final_metadata.resolve():
            raise OSError("injected paired-promotion failure")
        return original_replace(source, destination)

    monkeypatch.setattr(builder.os, "replace", fail_final_metadata)
    with pytest.raises(builder.BuildError, match="paired-promotion failure"):
        builder._promote_staging(
            staging,
            final,
            metadata_document={
                "database_sha256": candidate_hash,
                "promoted_database_sha256": candidate_hash,
            },
        )

    assert final.read_bytes() == before_final
    assert final_metadata.read_bytes() == before_metadata
    assert staging.read_bytes() == b"candidate"
    assert builder.metadata_path_for(staging).read_text(encoding="utf-8") == "candidate-marker"
