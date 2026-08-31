from __future__ import annotations

import re


def test_vehicle_catalog_uses_human_filters_and_compact_readiness(client):
    response = client.get("/vehicles")

    assert response.status_code == 200
    html = response.text
    assert 'id="vehicle-search"' in html
    assert 'type="search"' in html
    assert 'id="manufacturer-filter"' in html
    assert 'id="body-style-filter"' in html
    assert 'id="readiness-filter"' in html
    assert '<option value="AVT_READY">AVT</option>' in html
    assert 'Configuration code: <code>FIXTURE-' in html
    assert all('scope="' in tag for tag in re.findall(r"<th\b[^>]*>", html))
    for control_id in ("vehicle-search", "manufacturer-filter", "body-style-filter", "readiness-filter"):
        assert f'for="{control_id}"' in html
    assert "skip-link" in html
    assert "value-card" not in html

    filtered = client.get("/vehicles", params={"readiness": "AVT_READY"})
    assert filtered.status_code == 200
    assert 'value="AVT_READY" selected' in filtered.text


def test_vehicle_detail_groups_values_and_discloses_provenance(client):
    response = client.get("/vehicles/FIXTURE-WIDTH-UNSPECIFIED")

    assert response.status_code == 200
    html = response.text
    for heading in (
        "Engineering summary",
        "Body dimensions",
        "All engineering data",
        "Unknown / research assessments",
    ):
        assert heading in html
    direct = client.get("/vehicles/FIXTURE-AVT-TRACK-DIRECT")
    assert "Axle geometry" in direct.text
    assert "Turning &amp; steering" in direct.text
    assert "AVT-specific" in direct.text
    screening = client.get("/vehicles/FIXTURE-AVT-TRACK-SCREENING")
    assert "Track / lateral geometry" in screening.text
    assert "Wheel &amp; tyre" in screening.text
    clearance = client.get("/vehicles/FIXTURE-CLEARANCE-LOADS")
    assert "Clearance &amp; ramp" in clearance.text
    assert "engineering-table" in html
    assert '<th scope="col">Parameter</th>' in html
    assert "Overall width · reported" in html
    assert "Evidence · 1 source" in html
    assert "Authority grade" in html
    assert "Applicability grade" in html
    assert 'class="evidence-details"' in html
    assert "value-card" not in html


def test_detail_keeps_conflicts_and_load_scope_visible(client):
    clearance = client.get("/vehicles/FIXTURE-CLEARANCE-LOADS")
    assert clearance.status_code == 200
    assert "Unladen" in clearance.text
    assert "OEM laden" in clearance.text
    assert "Load detail" in clearance.text

    conflict = client.get("/vehicles/FIXTURE-CONFLICTING-VALUE")
    assert conflict.status_code == 200
    assert "Conflicting" in conflict.text
    assert "Preferred candidate" in conflict.text
    assert "Source observations" in conflict.text


def test_compare_is_a_parameter_by_vehicle_matrix_with_four_selectors(client):
    response = client.get(
        "/compare",
        params={
            "codes": ",".join(
                [
                    "FIXTURE-PRIMARY-PUBLISHED",
                    "FIXTURE-CLEARANCE-LOADS",
                    "FIXTURE-CONFLICTING-VALUE",
                    "FIXTURE-UNKNOWN-ASSESSMENT",
                ]
            )
        },
    )

    assert response.status_code == 200
    html = response.text
    assert html.count('name="vehicle_') == 4
    assert "Engineering comparison matrix" in html
    assert 'class="comparison-matrix"' in html
    assert '<th scope="col">Parameter</th>' in html
    assert '<th scope="col">Unit</th>' in html
    assert 'scope="rowgroup"' in html
    assert "Overall length" in html
    assert "Readiness" in html
    assert "Not ready" in html
    assert "Unknown" in html
    assert "Conflicting" in html
    assert "Clearance" in html
    assert "Unladen" in html

    slot_response = client.get(
        "/compare",
        params={
            "vehicle_1": "FIXTURE-PRIMARY-PUBLISHED",
            "vehicle_2": "FIXTURE-AVT-TRACK-DIRECT",
        },
    )
    assert slot_response.status_code == 200
    assert 'name="vehicle_1"' in slot_response.text
    assert 'value="FIXTURE-PRIMARY-PUBLISHED" selected' in slot_response.text


def test_issues_view_uses_human_labels_and_bounded_filter(client):
    response = client.get("/issues")

    assert response.status_code == 200
    html = response.text
    assert 'id="issue-kind-filter"' in html
    assert '<option value="READINESS">Readiness</option>' in html
    assert "Readiness blocker" in html
    assert "QA finding" in html
    assert "FIXTURE-" in html
    assert 'scope="col"' in html

    filtered = client.get("/issues", params={"kind": "READINESS"})
    assert filtered.status_code == 200
    assert 'value="READINESS" selected' in filtered.text
