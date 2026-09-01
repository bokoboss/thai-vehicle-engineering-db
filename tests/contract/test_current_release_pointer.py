from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import build_curated_db as builder


ROOT = Path(__file__).resolve().parents[2]
BYD_MANIFEST = ROOT / "data/curation/manifests/sentinel/byd_atto3_my24_extended_local_v1.json"
TRITON_MANIFEST = ROOT / "data/curation/manifests/sentinel/mitsubishi_triton_ultra_4wd_at_2023_v1.json"


def _copy_manifest(root: Path, name: str, source: Path) -> Path:
    path = root / name
    path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return path


def _write_versioned_release(
    root: Path,
    filename: str,
    manifest_paths: list[Path],
    *,
    release_status: str = "ACCEPTED",
) -> Path:
    releases = root / "data/curation/releases"
    releases.mkdir(parents=True, exist_ok=True)
    document = {
        "release_schema_version": "1.0",
        "release_id": Path(filename).stem,
        "release_date": "2026-09-01",
        "release_status": release_status,
        "data_standard_version": "1.0",
        "methodology_versions": {"curation_ingestion_contract": "1.0"},
        "manifest_paths": [path.relative_to(root).as_posix() for path in manifest_paths],
    }
    path = releases / filename
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def _write_pointer(root: Path, target: str) -> Path:
    pointer = root / "data/curation/releases/current_release.json"
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text(
        json.dumps(
            {
                "pointer_schema_version": "1.0",
                "release": target,
            }
        ),
        encoding="utf-8",
    )
    return pointer


def test_default_builder_resolves_current_release_pointer():
    args = builder._parser().parse_args([])
    pointer = json.loads(
        (ROOT / "data/curation/releases/current_release.json").read_text(encoding="utf-8")
    )
    expected_target = ROOT / "data/curation/releases" / pointer["release"]

    assert args.release is None
    assert builder.resolve_release_path(args.release) == expected_target.resolve()
    assert builder.collect_inventory(args.release).release.path == expected_target.resolve()


def test_current_pointer_target_inventory_is_derived_from_selected_release():
    target = builder.resolve_current_release_path()
    inventory = builder.collect_inventory()
    pointer = json.loads(
        (ROOT / "data/curation/releases/current_release.json").read_text(encoding="utf-8")
    )

    assert target == (ROOT / "data/curation/releases" / pointer["release"]).resolve()
    assert inventory.release.path == target
    assert len(inventory.manifests) == len(inventory.release.manifest_paths)
    assert len(inventory.stable_vehicle_codes) == len(inventory.manifests)
    assert len(set(inventory.stable_vehicle_codes)) == len(inventory.stable_vehicle_codes)
    assert inventory.manifests


def test_changing_only_pointer_changes_default_membership_without_source_edits(tmp_path: Path):
    first = _copy_manifest(tmp_path, "first.json", BYD_MANIFEST)
    second = _copy_manifest(tmp_path, "second.json", TRITON_MANIFEST)
    first_release = _write_versioned_release(tmp_path, "release_2026_10_a.json", [first])
    second_release = _write_versioned_release(
        tmp_path,
        "release_2026_11_a.json",
        [first, second],
    )
    pointer = _write_pointer(tmp_path, first_release.name)
    builder_source_before = (ROOT / "scripts/build_curated_db.py").read_bytes()
    launcher_before = (ROOT / "Update Vehicle Database.cmd").read_bytes()

    one = builder.collect_inventory(root=tmp_path)
    pointer.write_text(
        json.dumps(
            {
                "pointer_schema_version": "1.0",
                "release": second_release.name,
            }
        ),
        encoding="utf-8",
    )
    two = builder.collect_inventory(root=tmp_path)

    assert one.release.path == first_release.resolve()
    assert two.release.path == second_release.resolve()
    assert one.expected_counts["vehicles"] == 1
    assert two.expected_counts["vehicles"] == 2
    assert set(one.stable_vehicle_codes) != set(two.stable_vehicle_codes)
    assert (ROOT / "scripts/build_curated_db.py").read_bytes() == builder_source_before
    assert (ROOT / "Update Vehicle Database.cmd").read_bytes() == launcher_before


def test_explicit_release_overrides_current_pointer(tmp_path: Path):
    first = _copy_manifest(tmp_path, "first.json", BYD_MANIFEST)
    second = _copy_manifest(tmp_path, "second.json", TRITON_MANIFEST)
    first_release = _write_versioned_release(tmp_path, "release_2026_10_a.json", [first])
    second_release = _write_versioned_release(tmp_path, "release_2026_11_a.json", [first, second])
    _write_pointer(tmp_path, second_release.name)

    inventory = builder.collect_inventory(first_release, root=tmp_path)

    assert inventory.release.path == first_release.resolve()
    assert inventory.expected_counts["vehicles"] == 1
    assert inventory.stable_vehicle_codes == ("th-byd-atto3-my24-extended-local",)


def test_explicit_release_does_not_require_current_pointer(tmp_path: Path):
    manifest = _copy_manifest(tmp_path, "manifest.json", BYD_MANIFEST)
    release = _write_versioned_release(tmp_path, "release_2026_10_a.json", [manifest])

    inventory = builder.collect_inventory(release, root=tmp_path)

    assert inventory.release.path == release.resolve()
    assert inventory.expected_counts["vehicles"] == 1


def test_missing_current_pointer_fails_closed(tmp_path: Path):
    with pytest.raises(builder.BuildError, match="current release pointer was not found"):
        builder.collect_inventory(root=tmp_path)


def test_invalid_current_pointer_json_fails_closed(tmp_path: Path):
    pointer = tmp_path / "data/curation/releases/current_release.json"
    pointer.parent.mkdir(parents=True)
    pointer.write_text("{", encoding="utf-8")

    with pytest.raises(builder.BuildError, match="invalid current release pointer"):
        builder.collect_inventory(root=tmp_path)


def test_unsupported_current_pointer_schema_fails_closed(tmp_path: Path):
    _write_pointer(tmp_path, "release_2026_10_a.json")
    pointer = tmp_path / "data/curation/releases/current_release.json"
    pointer.write_text(
        json.dumps(
            {
                "pointer_schema_version": "2.0",
                "release": "release_2026_10_a.json",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(builder.BuildError, match="unsupported current release pointer schema"):
        builder.collect_inventory(root=tmp_path)


def test_missing_pointer_target_fails_closed(tmp_path: Path):
    _write_pointer(tmp_path, "release_2026_10_a.json")

    with pytest.raises(builder.BuildError, match="pointer target was not found"):
        builder.collect_inventory(root=tmp_path)


@pytest.mark.parametrize(
    "target",
    [
        "../release_2026_10_a.json",
        "data/curation/releases/release_2026_10_a.json",
        "current_release.json",
        "not_a_release.txt",
        "C:/outside/release_2026_10_a.json",
    ],
)
def test_invalid_pointer_target_path_fails_closed(tmp_path: Path, target: str):
    _write_pointer(tmp_path, target)

    with pytest.raises(builder.BuildError):
        builder.collect_inventory(root=tmp_path)


def test_pointer_target_release_must_pass_release_validation(tmp_path: Path):
    manifest = _copy_manifest(tmp_path, "manifest.json", BYD_MANIFEST)
    _write_versioned_release(
        tmp_path,
        "release_2026_10_a.json",
        [manifest],
        release_status="DRAFT",
    )
    _write_pointer(tmp_path, "release_2026_10_a.json")

    with pytest.raises(builder.BuildError, match="release_status must be ACCEPTED"):
        builder.collect_inventory(root=tmp_path)
