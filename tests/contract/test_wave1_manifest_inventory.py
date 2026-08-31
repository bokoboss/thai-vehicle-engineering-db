from __future__ import annotations

from scripts.build_wave1_curated_db import collect_inventory


def test_accepted_wave1_manifest_inventory_is_deterministic():
    inventory = collect_inventory()

    assert len(inventory.manifests) == 21
    assert len(inventory.stable_vehicle_codes) == 21
    assert len(set(inventory.stable_vehicle_codes)) == 21
    assert inventory.expected_counts == {
        "vehicles": 21,
        "source_entries": 55,
        "sources": 54,
        "observations": 211,
        "values": 247,
        "assessments": 47,
        "loads": 21,
        "fitments": 14,
        "axles": 0,
        "steering_relations": 0,
        "geometry_assets": 0,
        "conflict_decisions": 0,
        "conflicting_values": 2,
    }
