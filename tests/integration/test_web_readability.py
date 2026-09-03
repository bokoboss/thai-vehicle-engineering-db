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


def test_shared_ui_hooks_mark_navigation_and_dense_page_boundaries(client):
    vehicles = client.get("/vehicles").text
    assert '<a class="nav-link is-active" href="/vehicles" aria-current="page">Vehicles</a>' in vehicles
    assert vehicles.count('aria-current="page"') == 1
    assert 'class="filter-panel filter-bar catalog-filter-panel"' in vehicles
    assert 'class="muted result-summary result-count"' in vehicles

    detail = client.get("/vehicles/FIXTURE-PRIMARY-PUBLISHED").text
    assert '<a class="nav-link is-active" href="/vehicles" aria-current="page">Vehicles</a>' in detail
    assert detail.count('aria-current="page"') == 1

    compare = client.get(
        "/compare",
        params={"codes": "FIXTURE-PRIMARY-PUBLISHED,FIXTURE-CLEARANCE-LOADS"},
    ).text
    assert '<a class="nav-link is-active" href="/compare" aria-current="page">Compare</a>' in compare
    assert 'class="selection-summary"' in compare
    assert "Scroll horizontally to inspect every selected vehicle column." in compare

    design = client.get(
        "/design-check",
        params={"available_clear_height_mm": "2100"},
    ).text
    assert '<a class="nav-link is-active" href="/design-check" aria-current="page">Design Check</a>' in design
    assert 'class="constraint-cluster-grid"' in design
    assert "Scroll horizontally to inspect every constraint and control column." in design

    issues = client.get("/issues").text
    assert '<a class="nav-link is-active" href="/issues" aria-current="page">Data Issues</a>' in issues
    assert 'class="filter-panel issue-filter"' in issues
    assert 'class="muted result-summary result-count"' in issues


def test_empty_catalog_and_issue_states_use_shared_table_language(client):
    catalog = client.get("/vehicles", params={"q": "no-such-configuration"})
    assert catalog.status_code == 200
    assert 'class="empty table-empty"' in catalog.text
    assert "Reset the catalog filters to show the full catalog." in catalog.text

    issues = client.get("/issues", params={"kind": "not-a-real-kind"})
    assert issues.status_code == 200
    assert 'class="empty table-empty"' in issues.text
    assert "Show all issue types to restore the complete work queue." in issues.text


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

    mixed_unit_response = client.get(
        "/compare",
        params={"codes": "FIXTURE-UNKNOWN-ASSESSMENT,FIXTURE-STEERING-SEPARATION"},
    )
    mixed_unit_row = re.search(
        r'<tr>\s*<th scope="row">.*?maximum_inner_road_wheel_angle_deg.*?</tr>',
        mixed_unit_response.text,
        re.DOTALL,
    )
    assert mixed_unit_row is not None
    assert "<td>deg</td>" in mixed_unit_row.group(0)


def test_compare_shared_filters_keep_selected_configurations_visible(client):
    response = client.get(
        "/compare",
        params={
            "manufacturer": "does-not-match",
            "vehicle_1": "FIXTURE-PRIMARY-PUBLISHED",
            "vehicle_2": "FIXTURE-CLEARANCE-LOADS",
        },
    )

    assert response.status_code == 200
    html = response.text
    assert "Shared candidate filters" in html
    assert "Selected exact configuration" in html
    assert html.count("Selected ·") == 2
    assert 'value="FIXTURE-PRIMARY-PUBLISHED" selected' in html
    assert 'value="FIXTURE-CLEARANCE-LOADS" selected' in html
    assert 'name="slot_1_q"' in html
    assert 'name="slot_4_identity_time"' in html

    typed_filters = client.get(
        "/compare",
        params={"powertrain": "semantic test configuration", "identity_time": "MODEL_YEAR"},
    )
    assert typed_filters.status_code == 200
    assert 'value="semantic test configuration" selected' in typed_filters.text
    assert 'value="MODEL_YEAR" selected' in typed_filters.text


def test_compare_slots_keep_positions_and_slot_filters_override_shared_filters(client):
    response = client.get(
        "/compare",
        params={
            "body_style": "not-the-fixture-body-style",
            "vehicle_1": "",
            "vehicle_2": "",
            "vehicle_3": "FIXTURE-PRIMARY-PUBLISHED",
            "slot_3_body_style": "fixture",
        },
    )

    assert response.status_code == 200
    html = response.text
    slot_1 = re.search(r'<select id="vehicle-1".*?</select>', html, re.DOTALL)
    slot_2 = re.search(r'<select id="vehicle-2".*?</select>', html, re.DOTALL)
    slot_3 = re.search(r'<select id="vehicle-3".*?</select>', html, re.DOTALL)
    assert slot_1 and slot_2 and slot_3
    assert ' selected>' not in slot_1.group(0)
    assert ' selected>' not in slot_2.group(0)
    assert 'value="FIXTURE-PRIMARY-PUBLISHED" selected' in slot_3.group(0)
    assert 'value="fixture" selected' in html
    assert "Uses slot filters plus shared defaults" in html
    assert "Advanced filters for Vehicle 3" in html


def test_compare_search_all_action_and_duplicate_selection_are_explicit(client):
    search_all = client.get(
        "/compare",
        params={
            "body_style": "fixture",
            "vehicle_1": "FIXTURE-PRIMARY-PUBLISHED",
            "slot_action": "search_all:2",
        },
    )
    assert search_all.status_code == 200
    assert "Searches all vehicles" in search_all.text
    assert 'name="slot_2_scope" value="all"' in search_all.text
    assert "Search all vehicles ignores every shared filter" in search_all.text

    duplicate = client.get(
        "/compare",
        params={
            "vehicle_1": "FIXTURE-PRIMARY-PUBLISHED",
            "vehicle_2": "FIXTURE-PRIMARY-PUBLISHED",
        },
    )
    assert duplicate.status_code == 200
    assert "already selected in another slot" in duplicate.text
    slot_2 = re.search(r'<select id="vehicle-2".*?</select>', duplicate.text, re.DOTALL)
    assert slot_2 and 'value="FIXTURE-PRIMARY-PUBLISHED" selected' not in slot_2.group(0)


def test_engineering_summary_is_a_short_scan_set_before_full_record(client):
    response = client.get("/vehicles/FIXTURE-AVT-TRACK-DIRECT")

    assert response.status_code == 200
    html = response.text
    summary = html.split('id="normalized-values"', 1)[0]
    full_record = html.split('id="normalized-values"', 1)[1]
    assert "High-value scan set" in summary
    assert "AVT maximum steering angle" not in summary
    assert "AVT maximum steering angle" in full_record
    assert "All engineering data" in html


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
