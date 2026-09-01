from __future__ import annotations

import hashlib
import json
import sqlite3
from argparse import Namespace
from pathlib import Path

import pytest

from scripts import build_curated_db as builder
from scripts.run_local_app import validate_curated_database


ROOT = Path(__file__).resolve().parents[2]
BYD_PATH = "data/curation/manifests/sentinel/byd_atto3_my24_extended_local_v1.json"
TRITON_PATH = "data/curation/manifests/sentinel/mitsubishi_triton_ultra_4wd_at_2023_v1.json"


def _write_release(tmp_path: Path, paths: list[str], release_id: str = "test_build_release") -> Path:
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


def _build_args(
    release_path: Path,
    tmp_path: Path,
    *,
    replace_final: bool = True,
) -> Namespace:
    return Namespace(
        release=release_path,
        staging=tmp_path / "staging.db",
        final=tmp_path / "accepted.db",
        csv=tmp_path / "export.csv",
        xlsx=tmp_path / "export.xlsx",
        qualification=tmp_path / "qualification.json",
        no_promote=False,
        replace_final=replace_final,
    )


def test_failed_staging_build_leaves_accepted_database_unchanged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    release_path = _write_release(tmp_path, [BYD_PATH], release_id="failing_release")
    accepted = tmp_path / "accepted.db"
    accepted.write_bytes(b"accepted-database-before-build")
    before_hash = hashlib.sha256(accepted.read_bytes()).hexdigest()

    def fail_qa(session, inventory):
        del session, inventory
        raise builder.BuildError("injected staging QA failure")

    monkeypatch.setattr(builder, "_qa_database", fail_qa)

    with pytest.raises(builder.BuildError, match="injected staging QA failure"):
        builder.build(_build_args(release_path, tmp_path))

    assert hashlib.sha256(accepted.read_bytes()).hexdigest() == before_hash
    assert accepted.read_bytes() == b"accepted-database-before-build"
    assert (tmp_path / "staging.db").is_file()


def test_successful_promotion_contains_exact_release_stable_code_set(tmp_path: Path):
    release_path = _write_release(tmp_path, [BYD_PATH, TRITON_PATH], release_id="promoted_release")
    expected = set(builder.collect_inventory(release_path).stable_vehicle_codes)

    report = builder.build(_build_args(release_path, tmp_path))

    assert report["status"] == "PASS"
    assert report["manifest_count"] == len(expected) == 2
    assert set(report["stable_vehicle_codes"]) == expected
    assert (tmp_path / "accepted.db").is_file()
    assert not (tmp_path / "staging.db").exists()
    assert json.loads((tmp_path / "qualification.json").read_text(encoding="utf-8"))["promotion"]["result"] == "PROMOTED"
    with sqlite3.connect(tmp_path / "accepted.db") as connection:
        rows = connection.execute(
            "SELECT stable_vehicle_code FROM vehicle_configuration ORDER BY stable_vehicle_code"
        ).fetchall()
    assert {row[0] for row in rows} == expected


def test_start_launcher_reads_the_promoted_release_without_a_vehicle_count_constant(tmp_path: Path):
    release_path = _write_release(tmp_path, [BYD_PATH, TRITON_PATH], release_id="launcher_release")
    builder.build(_build_args(release_path, tmp_path))

    assert validate_curated_database(tmp_path / "accepted.db") == frozenset(
        builder.collect_inventory(release_path).stable_vehicle_codes
    )


def test_update_launcher_is_data_only_and_never_seeds_phase0():
    launcher = (ROOT / "Update Vehicle Database.cmd").read_text(encoding="utf-8").lower()

    assert "build_curated_db.py" in launcher
    assert "--release" not in launcher
    assert "release_2026_09_a.json" not in launcher
    assert "--replace-final" in launcher
    assert "app.seed" not in launcher
