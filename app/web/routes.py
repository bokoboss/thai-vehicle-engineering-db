from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import PROJECT_ROOT
from app.db.models import ReadinessResult, VehicleConfiguration
from app.db.repositories import get_vehicle, list_issue_rows, list_vehicles
from app.db.session import get_session
from app.domain.readiness import evaluate_readiness
from app.exports.exporter import csv_bytes, export_rows, xlsx_bytes


router = APIRouter()
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "app" / "web" / "templates"))


READINESS_LABELS = {
    "IDENTITY_RESOLVED": "Identity",
    "DIMENSION_READY": "Dimensions",
    "AVT_READY": "AVT",
    "RAMP_SCREENING_READY": "Ramp",
}
READINESS_ORDER = tuple(READINESS_LABELS)
READINESS_OPTIONS = tuple(
    {"value": value, "label": label} for value, label in READINESS_LABELS.items()
)
COMPARE_FILTER_KEYS = ("q", "manufacturer", "body_style", "powertrain", "identity_time")
COMPARE_CANDIDATE_LIMIT = 100
IDENTITY_TIME_LABELS = {
    "MODEL_YEAR": "Model year",
    "OEM_REVISION_LABEL": "OEM revision",
    "EDITION_RELEASE": "Edition release",
    "SALE_PERIOD": "Sale period",
    "MULTIPLE": "Multiple time bases",
    "UNKNOWN": "Time basis unknown",
}
STATUS_LABELS = {
    "READY": "Ready",
    "NOT_READY": "Not ready",
    "INDETERMINATE": "Indeterminate",
}
AVAILABILITY_LABELS = {
    "AVAILABLE": "Available",
    "UNKNOWN": "Unknown",
    "NOT_FOUND_AFTER_SEARCH": "Not found",
    "NOT_APPLICABLE": "Not applicable",
}
EVIDENCE_METHOD_LABELS = {
    "PUBLISHED": "Published",
    "MEASURED": "Measured",
    "DERIVED": "Derived",
    "ESTIMATED": "Estimated",
    "NONE": "No evidence",
}
RESOLUTION_LABELS = {
    "UNCONTESTED": "Uncontested",
    "CONFLICTING": "Conflicting",
    "PREFERRED_WITH_CONFLICT": "Preferred; conflict retained",
    "SUPERSEDED": "Superseded",
    "NOT_APPLICABLE": "Not applicable",
}
VERIFICATION_LABELS = {
    "UNREVIEWED": "Unreviewed",
    "REVIEWED": "Reviewed",
    "VERIFIED": "Verified",
    "REJECTED": "Rejected",
}
FAMILY_GROUPS = (
    ("body", "Body dimensions", {"body_geometry"}),
    ("axle", "Axle geometry", {"axle_geometry"}),
    ("lateral", "Track / lateral geometry", {"lateral_geometry"}),
    ("wheel", "Wheel & tyre", {"wheel_tyre"}),
    ("turning", "Turning & steering", {"turning", "steering"}),
    ("avt", "AVT-specific", {"avt_geometry", "avt_steering"}),
    ("clearance", "Clearance & ramp", {"clearance", "ramp_oem", "ramp_physical", "ramp_screening"}),
    ("mass", "Mass", {"mass"}),
)
FAMILY_GROUP_LOOKUP = {
    family: (key, label)
    for key, label, families in FAMILY_GROUPS
    for family in families
}
PARAMETER_LABELS = {
    "overall_length_mm": "Overall length",
    "overall_height_mm": "Overall height",
    "overall_width_reported_mm": "Overall width · reported",
    "overall_width_body_mm": "Overall width · body",
    "overall_width_including_mirrors_mm": "Overall width · mirrors open",
    "overall_width_mirrors_folded_mm": "Overall width · mirrors folded",
    "wheelbase_actual_mm": "Wheelbase",
    "front_overhang_mm": "Front overhang",
    "rear_overhang_mm": "Rear overhang",
    "oem_front_tread_or_track_mm": "OEM front tread / track",
    "oem_rear_tread_or_track_mm": "OEM rear tread / track",
    "avt_front_outer_face_track_mm": "AVT front outer-face tyre track",
    "avt_rear_outer_face_track_mm": "AVT rear outer-face tyre track",
    "front_tyre_size_text": "Front tyre",
    "rear_tyre_size_text": "Rear tyre",
    "front_nominal_section_width_mm": "Front nominal tyre section width",
    "rear_nominal_section_width_mm": "Rear nominal tyre section width",
    "nominal_unloaded_tyre_radius_front_mm": "Front nominal unloaded tyre radius",
    "nominal_unloaded_tyre_radius_rear_mm": "Rear nominal unloaded tyre radius",
    "static_loaded_tyre_radius_front_mm": "Front static-loaded tyre radius",
    "static_loaded_tyre_radius_rear_mm": "Rear static-loaded tyre radius",
    "front_wheel_rim_text": "Front wheel / rim",
    "rear_wheel_rim_text": "Rear wheel / rim",
    "turning_radius_normalized_m": "Turning radius · normalized",
    "oem_turning_value_text": "Turning value · OEM wording",
    "steering_ratio_value": "Steering ratio",
    "steering_wheel_lock_to_lock_turns": "Steering-wheel lock-to-lock turns",
    "maximum_inner_road_wheel_angle_deg": "Maximum inner road-wheel angle",
    "maximum_outer_road_wheel_angle_deg": "Maximum outer road-wheel angle",
    "virtual_center_steering_angle_deg": "Virtual-centre steering angle",
    "avt_maximum_steering_angle_deg": "AVT maximum steering angle",
    "avt_lock_to_lock_time_forward_s": "AVT forward lock-to-lock time",
    "avt_lock_to_lock_time_reverse_s": "AVT reverse lock-to-lock time",
    "clearance_value_mm": "Ground clearance",
    "oem_published_approach_angle_deg": "OEM-published approach angle",
    "oem_published_departure_angle_deg": "OEM-published departure angle",
    "oem_published_breakover_angle_deg": "OEM-published breakover angle",
    "geometry_derived_approach_angle_deg": "Geometry-derived approach angle",
    "geometry_derived_departure_angle_deg": "Geometry-derived departure angle",
    "geometry_derived_breakover_angle_deg": "Geometry-derived breakover angle",
    "screening_front_contact_angle_deg": "Screening front contact angle",
    "screening_rear_contact_angle_deg": "Screening rear contact angle",
    "screening_breakover_angle_deg": "Screening breakover angle",
    "screening_breakover_symmetric_angle_deg": "Screening symmetric breakover angle",
    "kerb_mass_kg": "Kerb mass",
    "gross_vehicle_mass_kg": "Gross vehicle mass",
    "front_axle_load_kg": "Front axle load",
    "rear_axle_load_kg": "Rear axle load",
}
PARAMETER_ORDER = tuple(PARAMETER_LABELS)
PARAMETER_ORDER_LOOKUP = {code: index for index, code in enumerate(PARAMETER_ORDER)}
SUMMARY_PARAMETER_CODES = frozenset(
    {
        "overall_length_mm",
        "overall_height_mm",
        "overall_width_reported_mm",
        "overall_width_body_mm",
        "overall_width_including_mirrors_mm",
        "overall_width_mirrors_folded_mm",
        "wheelbase_actual_mm",
        "front_overhang_mm",
        "rear_overhang_mm",
        "oem_front_tread_or_track_mm",
        "oem_rear_tread_or_track_mm",
        "front_tyre_size_text",
        "rear_tyre_size_text",
        "front_wheel_rim_text",
        "rear_wheel_rim_text",
        "turning_radius_normalized_m",
        "oem_turning_value_text",
        "clearance_value_mm",
        "kerb_mass_kg",
        "gross_vehicle_mass_kg",
    }
)
SEMANTIC_VALUE_LABELS = {
    "BODY_EXCLUDING_MIRRORS": "Body excluding mirrors",
    "INCLUDING_MIRRORS_OPEN": "Mirrors open",
    "INCLUDING_MIRRORS_FOLDED": "Mirrors folded",
    "BODY_AND_FIXED_APPENDAGES": "Body and fixed appendages",
    "OEM_UNSPECIFIED": "OEM definition unspecified",
    "TYRE_CENTERLINE": "Tyre centreline",
    "WHEEL_CENTERLINE": "Wheel centreline",
    "OUTER_TYRE_FACES": "Outer tyre faces",
    "INNER_TYRE_FACES": "Inner tyre faces",
    "RADIUS": "Radius",
    "DIAMETER": "Diameter",
    "CURB_TO_CURB": "Curb-to-curb",
    "WALL_TO_WALL": "Wall-to-wall",
    "WHEEL_PATH_OTHER": "Other wheel path",
    "BODY_PATH_OTHER": "Other body path",
    "ALL_AXLES": "All axles",
    "ACTIVE_AXLES": "Active axles",
    "BODY_ONLY": "Body only",
    "BODY_AND_LOADS": "Body and loads",
    "OEM_MINIMUM_UNSPECIFIED": "OEM clearance type unspecified",
    "RUNNING_CLEARANCE": "Running clearance",
    "BETWEEN_AXLES": "Between axles",
    "FRONT_AXLE": "Front axle",
    "REAR_AXLE": "Rear axle",
    "DIFFERENTIAL": "Differential",
    "BATTERY_PACK": "Battery pack",
    "COMPONENT_SPECIFIC": "Component-specific",
}
SEMANTIC_KEY_LABELS = {
    "width_envelope_definition": "Width definition",
    "track_definition": "Track definition",
    "turning_radius_or_diameter": "Turning shape",
    "turning_reference": "Turning reference",
    "turning_axle_scope": "Axle scope",
    "turning_wall_envelope_scope": "Wall envelope",
    "clearance_type": "Clearance type",
    "source_label": "Source label",
    "source_reported_shape": "Source-reported shape",
    "normalization_blocker": "Normalization blocker",
    "source_qualifier": "Source qualifier",
}
ISSUE_KIND_LABELS = {"READINESS": "Readiness", "QA": "QA finding"}


def _typed_value(value: Any) -> Any:
    if value.numeric_value is not None:
        return float(value.numeric_value)
    if value.text_value is not None:
        return value.text_value
    if value.boolean_value is not None:
        return value.boolean_value
    if value.enum_value is not None:
        return value.enum_value
    return value.json_value


def _humanize(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("_", " ").capitalize()


def _parameter_label(parameter_code: str, display_name: str | None = None) -> str:
    return PARAMETER_LABELS.get(parameter_code, display_name or _humanize(parameter_code))


def _identity_time_label(basis: str, raw_label: str | None, model_year_from: int | None, model_year_to: int | None) -> str:
    label = IDENTITY_TIME_LABELS.get(basis, _humanize(basis))
    if basis == "MODEL_YEAR" and model_year_from is not None:
        years = str(model_year_from)
        if model_year_to is not None:
            years += f"–{model_year_to}"
        return f"{label} {years}"
    return f"{label}: {raw_label}" if raw_label else label


def _format_display_value(value: Any) -> str:
    if value is None:
        return "Unknown"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else format(value, ".12g")
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _date_display(value: Any) -> str | None:
    if value is None:
        return None
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def _semantic_items(metadata: dict[str, Any] | None) -> list[dict[str, str]]:
    if not metadata:
        return []
    items = []
    for key, raw_value in metadata.items():
        value = SEMANTIC_VALUE_LABELS.get(str(raw_value), _format_display_value(raw_value))
        items.append(
            {
                "key": str(key),
                "label": SEMANTIC_KEY_LABELS.get(str(key), _humanize(key)),
                "value": value,
            }
        )
    return items


def _semantic_cue(items: list[dict[str, str]]) -> str:
    preferred_keys = {
        "width_envelope_definition",
        "track_definition",
        "turning_radius_or_diameter",
        "turning_reference",
        "turning_axle_scope",
        "turning_wall_envelope_scope",
        "clearance_type",
        "source_qualifier",
    }
    return " · ".join(item["value"] for item in items if item["key"] in preferred_keys)


def _scope_view(value: Any, fitments: dict[str, Any], load_conditions: dict[str, Any]) -> dict[str, Any]:
    fitment = fitments.get(value.vehicle_fitment_id) if value.vehicle_fitment_id else None
    load_condition = load_conditions.get(value.load_condition_id) if value.load_condition_id else None
    parts = []
    if fitment:
        parts.append(fitment.fitment_code)
    elif value.vehicle_fitment_id:
        parts.append("Fitment scope unresolved")
    if load_condition:
        parts.append(load_condition.name)
    elif value.load_condition_id:
        parts.append("Load condition unresolved")
    return {
        "text": " · ".join(parts) if parts else "Configuration-wide",
        "is_scoped": bool(parts),
        "fitment": (
            {
                "code": fitment.fitment_code,
                "description": fitment.description,
                "wheel_package": fitment.wheel_package,
                "equipment_package": fitment.equipment_package,
                "default": fitment.default_for_configuration,
            }
            if fitment
            else None
        ),
        "load_condition": (
            {
                "name": load_condition.name,
                "mass_basis": load_condition.mass_basis,
                "total_mass_kg": load_condition.total_mass_kg,
                "occupant_count": load_condition.occupant_count,
                "payload_kg": load_condition.payload_kg,
                "tyre_pressure": (
                    f"{load_condition.front_tyre_pressure}/{load_condition.rear_tyre_pressure} "
                    f"{load_condition.tyre_pressure_unit or ''}"
                    if load_condition.front_tyre_pressure is not None or load_condition.rear_tyre_pressure is not None
                    else None
                ),
                "suspension_mode": load_condition.suspension_mode,
                "ride_height_mode": load_condition.ride_height_mode,
                "raw_oem_wording": load_condition.raw_oem_wording,
                "notes": load_condition.notes,
            }
            if load_condition
            else None
        ),
    }


def _state_view(value: Any, *, is_scoped: bool) -> dict[str, str | bool]:
    availability = value.availability_state
    resolution = value.resolution_state
    verification = value.verification_state
    evidence_method = value.evidence_method
    if availability != "AVAILABLE":
        label = AVAILABILITY_LABELS.get(availability, _humanize(availability))
        tone = "unknown"
        is_exception = True
    elif verification == "REJECTED":
        label = "Rejected"
        tone = "rejected"
        is_exception = True
    elif resolution == "CONFLICTING":
        label = "Conflicting"
        tone = "conflict"
        is_exception = True
    elif resolution == "PREFERRED_WITH_CONFLICT":
        label = "Preferred · conflict retained"
        tone = "conflict"
        is_exception = True
    elif resolution == "SUPERSEDED":
        label = "Superseded"
        tone = "muted"
        is_exception = True
    else:
        label = EVIDENCE_METHOD_LABELS.get(evidence_method, _humanize(evidence_method))
        tone = "scoped" if is_scoped else "normal"
        is_exception = is_scoped
    if is_scoped and not label.endswith("scoped") and tone not in {"conflict", "unknown", "rejected"}:
        label += " · scoped"
    return {"label": label, "tone": tone, "is_exception": is_exception}


def _value_view(value: Any, fitments: dict[str, Any], load_conditions: dict[str, Any]) -> dict[str, Any]:
    typed_value = _typed_value(value)
    scope = _scope_view(value, fitments, load_conditions)
    state = _state_view(value, is_scoped=scope["is_scoped"])
    semantic_items = _semantic_items(value.semantic_metadata)
    observations = []
    for link in value.evidence_links:
        observation = link.source_observation
        if observation is None:
            continue
        source = observation.source_document
        observations.append(
            {
                "id": observation.id,
                "source_code": source.source_code,
                "source_title": source.title,
                "source_publisher": source.publisher,
                "publisher": source.publisher,
                "authority_class": source.authority_class,
                "source_url": source.url,
                "retrieved_at": _date_display(source.retrieved_at),
                "page_section_locator": observation.page_section_locator,
                "raw_label": observation.raw_label,
                "raw_value": observation.raw_value,
                "raw_unit": observation.raw_unit,
                "raw_qualifier": observation.raw_qualifier,
                "evidence_role": link.evidence_role,
            }
        )
    source_count = len({observation["source_code"] for observation in observations})
    return {
        "id": value.id,
        "parameter_code": value.parameter_definition.parameter_code,
        "display_name": _parameter_label(value.parameter_definition.parameter_code, value.parameter_definition.display_name),
        "family": value.parameter_definition.family,
        "value": typed_value,
        "display_value": _format_display_value(typed_value),
        "is_numeric": value.numeric_value is not None,
        "unit": value.canonical_unit or value.parameter_definition.canonical_unit,
        "evidence_method": value.evidence_method,
        "evidence_method_label": EVIDENCE_METHOD_LABELS.get(value.evidence_method, _humanize(value.evidence_method)),
        "resolution_state": value.resolution_state,
        "resolution_state_label": RESOLUTION_LABELS.get(value.resolution_state, _humanize(value.resolution_state)),
        "verification_state": value.verification_state,
        "verification_state_label": VERIFICATION_LABELS.get(value.verification_state, _humanize(value.verification_state)),
        "availability_state": value.availability_state,
        "availability_state_label": AVAILABILITY_LABELS.get(value.availability_state, _humanize(value.availability_state)),
        "preferred": value.preferred,
        # Preserve the established detail API fields while the UI uses the
        # richer nested scope view above.
        "fitment_code": scope["fitment"]["code"] if scope["fitment"] else None,
        "fitment_description": scope["fitment"]["description"] if scope["fitment"] else None,
        "load_condition_id": value.load_condition_id,
        "load_condition": scope["load_condition"],
        "authority_grade": value.authority_grade,
        "applicability_grade": value.applicability_grade,
        "precision": value.precision,
        "uncertainty_value": float(value.uncertainty_value) if value.uncertainty_value is not None else None,
        "uncertainty_unit": value.uncertainty_unit,
        "semantic_metadata": value.semantic_metadata or {},
        "semantic_items": semantic_items,
        "semantic_cue": _semantic_cue(semantic_items),
        "scope": scope,
        "scope_text": scope["text"],
        "is_scoped": scope["is_scoped"],
        "state_label": state["label"],
        "state_tone": state["tone"],
        "is_exception": state["is_exception"],
        "source_count": source_count,
        "evidence_label": (
            f"Evidence · {source_count} source" if source_count == 1 else f"Evidence · {source_count} sources"
        )
        if source_count
        else "Evidence · no linked source",
        "observations": observations,
        "derivation_rule": (
            {"code": value.derivation_run.derivation_rule.rule_code, "version": value.derivation_run.derivation_rule.version}
            if value.derivation_run and value.derivation_run.derivation_rule
            else None
        ),
    }


def _group_values(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = {
        key: {"key": key, "label": label, "values": []}
        for key, label, _families in FAMILY_GROUPS
    }
    for value in values:
        key, label = FAMILY_GROUP_LOOKUP.get(
            value["family"], ("other", _humanize(value["family"]))
        )
        grouped.setdefault(key, {"key": key, "label": label, "values": []})["values"].append(value)
    for group in grouped.values():
        group["values"].sort(
            key=lambda item: (
                PARAMETER_ORDER_LOOKUP.get(item["parameter_code"], len(PARAMETER_ORDER_LOOKUP)),
                item["scope_text"],
                item["id"],
            )
        )
    return [group for group in grouped.values() if group["values"]]


def _friendly_blocker(reason: str) -> str:
    friendly = reason
    for code in sorted(PARAMETER_LABELS, key=len, reverse=True):
        friendly = friendly.replace(code, PARAMETER_LABELS[code])
    friendly = friendly.replace("missing available value:", "Missing:")
    friendly = friendly.replace("missing normalized value:", "Missing:")
    friendly = friendly.replace("missing explicit", "Missing explicit")
    return friendly


def _readiness_view(results: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    views = []
    for readiness_type in READINESS_ORDER:
        result = results.get(readiness_type)
        if result is None:
            continue
        blockers = result.get("blocking_reasons") or []
        views.append(
            {
                "type": readiness_type,
                "label": READINESS_LABELS[readiness_type],
                "status": result.get("status", "INDETERMINATE"),
                "status_label": STATUS_LABELS.get(result.get("status"), _humanize(result.get("status"))),
                "status_tone": str(result.get("status", "indeterminate")).lower(),
                "blocker_count": len(blockers),
                "first_reason": _friendly_blocker(blockers[0]) if blockers else None,
                "blockers": [{"friendly": _friendly_blocker(reason), "raw": reason} for reason in blockers],
            }
        )
    return views


def _catalog_option(
    summary: dict[str, Any], *, selected: bool = False, outside_filters: bool = False
) -> dict[str, Any]:
    identity = summary["identity_time_label"]
    return {
        "code": summary["stable_vehicle_code"],
        "label": f"{summary['manufacturer']} · {summary['commercial_model']} · {summary['variant']}",
        "secondary": f"{summary['generation']} · {summary['body_style']} · {identity}",
        "vehicle_label": f"{summary['manufacturer']} · {summary['commercial_model']}",
        "variant": summary["variant"],
        "identity_time": identity,
        "selected": selected,
        "outside_filters": outside_filters,
    }


def _catalog_option_from_config(
    config: VehicleConfiguration, *, selected: bool = False, outside_filters: bool = False
) -> dict[str, Any]:
    identity = _identity_time_label(
        config.identity_time_basis,
        config.identity_time_label_raw,
        config.model_year_from,
        config.model_year_to,
    )
    return _catalog_option(
        {
            "stable_vehicle_code": config.stable_vehicle_code,
            "manufacturer": config.vehicle_model.manufacturer.display_name,
            "commercial_model": config.vehicle_model.display_model_name,
            "variant": config.variant_trim,
            "generation": config.generation_name,
            "body_style": config.body_style,
            "identity_time_label": identity,
        },
        selected=selected,
        outside_filters=outside_filters,
    )


def _catalog_filters(catalog: list[dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    manufacturers = {
        (item["manufacturer_code"], item["manufacturer"])
        for item in catalog
    }
    powertrains = {item["powertrain"] for item in catalog if item.get("powertrain")}
    identity_times = {item["identity_time_basis"] for item in catalog if item.get("identity_time_basis")}
    return {
        "manufacturers": [
            {"value": code, "label": label}
            for code, label in sorted(manufacturers, key=lambda pair: pair[1].lower())
        ],
        "body_styles": [
            {"value": value, "label": value}
            for value in sorted({item["body_style"] for item in catalog}, key=str.lower)
        ],
        "powertrains": [
            {"value": value, "label": value}
            for value in sorted(powertrains, key=str.lower)
        ],
        "identity_times": [
            {"value": value, "label": IDENTITY_TIME_LABELS.get(value, _humanize(value))}
            for value in sorted(identity_times, key=lambda item: IDENTITY_TIME_LABELS.get(item, item).lower())
        ],
        "readiness": list(READINESS_OPTIONS),
    }


def _clean_query_value(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _query_value(params: Any, *names: str) -> str:
    for name in names:
        if name in params:
            return _clean_query_value(params.get(name))
    return ""


def _compare_filter_state(request: Request) -> tuple[dict[str, str], list[dict[str, Any]]]:
    params = request.query_params
    shared = {
        "q": _query_value(params, "q", "search"),
        "manufacturer": _query_value(params, "manufacturer"),
        "body_style": _query_value(params, "body_style"),
        "powertrain": _query_value(params, "powertrain"),
        "identity_time": _query_value(params, "identity_time", "identity_basis"),
    }
    slots = []
    for number in range(1, 5):
        filters = {
            "q": _query_value(
                params,
                f"slot_{number}_q",
                f"slot_{number}_search",
                f"vehicle_{number}_q",
                f"vehicle_{number}_search",
            ),
            "manufacturer": _query_value(
                params,
                f"slot_{number}_manufacturer",
                f"vehicle_{number}_manufacturer",
            ),
            "body_style": _query_value(
                params,
                f"slot_{number}_body_style",
                f"vehicle_{number}_body_style",
            ),
            "powertrain": _query_value(
                params,
                f"slot_{number}_powertrain",
                f"vehicle_{number}_powertrain",
            ),
            "identity_time": _query_value(
                params,
                f"slot_{number}_identity_time",
                f"slot_{number}_identity_basis",
                f"vehicle_{number}_identity_time",
                f"vehicle_{number}_identity_basis",
            ),
        }
        scope = _query_value(params, f"slot_{number}_scope", f"vehicle_{number}_scope") or "shared"
        if scope not in {"shared", "all"}:
            scope = "shared"
        slots.append(
            {
                "number": number,
                "filters": filters,
                "scope": scope,
                "has_override": any(filters.values()),
            }
        )
    return shared, slots


def _effective_compare_filters(shared: dict[str, str], slot: dict[str, Any]) -> dict[str, str]:
    if slot["scope"] == "all":
        return dict(slot["filters"])
    return {
        key: slot["filters"][key] or shared[key]
        for key in COMPARE_FILTER_KEYS
    }


def _slot_action(request: Request) -> tuple[str, int] | None:
    raw_action = _clean_query_value(request.query_params.get("slot_action"))
    action, separator, raw_number = raw_action.partition(":")
    if not separator or action not in {"clear_slot", "search_all", "use_shared"}:
        return None
    try:
        number = int(raw_number)
    except ValueError:
        return None
    return (action, number) if 1 <= number <= 4 else None


def _compare_candidates(
    session: Session,
    filters: dict[str, str],
    *,
    selected_code: str,
    selected_summary: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], int, bool]:
    candidates = list_vehicles(
        session,
        search=filters["q"] or None,
        manufacturer=filters["manufacturer"] or None,
        body_style=filters["body_style"] or None,
        powertrain=filters["powertrain"] or None,
        identity_time=filters["identity_time"] or None,
        limit=COMPARE_CANDIDATE_LIMIT + 1,
    )
    truncated = len(candidates) > COMPARE_CANDIDATE_LIMIT
    candidates = candidates[:COMPARE_CANDIDATE_LIMIT]
    candidate_codes = {config.stable_vehicle_code for config in candidates}
    options = [
        _catalog_option_from_config(config, selected=config.stable_vehicle_code == selected_code)
        for config in candidates
    ]
    if selected_summary is not None and selected_code not in candidate_codes:
        options.insert(0, _catalog_option(selected_summary, selected=True, outside_filters=True))
    return options, len(candidates), truncated


def _assessment_view(assessment: Any, fitments: dict[str, Any]) -> dict[str, Any]:
    fitment = fitments.get(assessment.vehicle_fitment_id) if assessment.vehicle_fitment_id else None
    scope_text = fitment.fitment_code if fitment else "Configuration-wide"
    return {
        "parameter_code": assessment.parameter_definition.parameter_code,
        "display_name": _parameter_label(
            assessment.parameter_definition.parameter_code,
            assessment.parameter_definition.display_name,
        ),
        "family": assessment.parameter_definition.family,
        "unit": assessment.parameter_definition.canonical_unit,
        "availability_state": assessment.availability_state,
        "availability_state_label": AVAILABILITY_LABELS.get(
            assessment.availability_state, _humanize(assessment.availability_state)
        ),
        "unknown_reason": assessment.unknown_reason,
        "source_families_searched": assessment.source_families_searched or [],
        "scope_text": scope_text,
        "fitment": (
            {
                "code": fitment.fitment_code,
                "description": fitment.description,
            }
            if fitment
            else None
        ),
    }


def _issue_view(row: dict[str, Any]) -> dict[str, Any]:
    code = row["code"]
    if code.endswith("_BLOCKED"):
        base = code.removesuffix("_BLOCKED")
        code_label = f"{READINESS_LABELS.get(base, _humanize(base))} blocker"
    else:
        code_label = READINESS_LABELS.get(code, _humanize(code))
    vehicle = row["vehicle"]
    return {
        "kind": row["kind"],
        "kind_label": ISSUE_KIND_LABELS.get(row["kind"], _humanize(row["kind"])),
        "code": code,
        "code_label": code_label,
        "severity": row["severity"],
        "severity_label": _humanize(row["severity"]),
        "status": row["status"],
        "status_label": STATUS_LABELS.get(row["status"], _humanize(row["status"])),
        "vehicle_code": vehicle.stable_vehicle_code if vehicle else None,
        "vehicle_label": (
            f"{vehicle.vehicle_model.manufacturer.display_name} · "
            f"{vehicle.vehicle_model.display_model_name} · {vehicle.variant_trim}"
            if vehicle
            else "Unassigned"
        ),
        "message": row["message"],
    }


def _readiness_dict(session: Session, config: VehicleConfiguration) -> dict[str, dict[str, Any]]:
    persisted = session.scalars(
        select(ReadinessResult).where(
            ReadinessResult.vehicle_configuration_id == config.id,
            ReadinessResult.vehicle_fitment_id.is_(None),
        )
    ).all()
    if not persisted:
        return {
            evaluation.readiness_type.value: {
                "status": evaluation.status.value,
                "blocking_reasons": evaluation.blocking_reasons,
            }
            for evaluation in evaluate_readiness(session, config)
        }
    return {
        row.readiness_type: {
            "status": row.status,
            "blocking_reasons": row.blocking_reasons,
        }
        for row in persisted
        if row.vehicle_fitment_id is None
    }


def _summary(session: Session, config: VehicleConfiguration) -> dict[str, Any]:
    readiness = _readiness_dict(session, config)
    return {
        "id": config.id,
        "stable_vehicle_code": config.stable_vehicle_code,
        "manufacturer_code": config.vehicle_model.manufacturer.canonical_name,
        "manufacturer": config.vehicle_model.manufacturer.display_name,
        "commercial_model": config.vehicle_model.display_model_name,
        "generation": config.generation_name,
        "variant": config.variant_trim,
        "market": config.market_code,
        "powertrain": config.powertrain,
        "body_style": config.body_style,
        "model_year_from": config.model_year_from,
        "model_year_to": config.model_year_to,
        "identity_time_basis": config.identity_time_basis,
        "identity_time_label_raw": config.identity_time_label_raw,
        "identity_time_label": _identity_time_label(
            config.identity_time_basis,
            config.identity_time_label_raw,
            config.model_year_from,
            config.model_year_to,
        ),
        "sale_period_from": config.sale_period_from,
        "sale_period_to": config.sale_period_to,
        "identity_verification_state": config.identity_verification_state,
        "readiness": readiness,
        "readiness_view": _readiness_view(readiness),
    }


def _detail(session: Session, config: VehicleConfiguration) -> dict[str, Any]:
    fitments = {fitment.id: fitment for fitment in config.fitments}
    load_conditions = {load_condition.id: load_condition for load_condition in config.load_conditions}
    values = [
        _value_view(value, fitments, load_conditions)
        for value in config.normalized_values
    ]
    values.sort(
        key=lambda item: (
            PARAMETER_ORDER_LOOKUP.get(item["parameter_code"], len(PARAMETER_ORDER_LOOKUP)),
            item["scope_text"],
            item["id"],
        )
    )
    assessments = [
        _assessment_view(assessment, fitments)
        for assessment in config.parameter_assessments
    ]
    assessments.sort(
        key=lambda item: (
            PARAMETER_ORDER_LOOKUP.get(item["parameter_code"], len(PARAMETER_ORDER_LOOKUP)),
            item["scope_text"],
        )
    )
    groups = _group_values(values)
    summary_values = [value for value in values if value["parameter_code"] in SUMMARY_PARAMETER_CODES]
    summary_groups = _group_values(summary_values)
    assessment_groups = _group_values(
        [
            {
                **assessment,
                "id": f"assessment-{assessment['parameter_code']}",
                "scope_text": assessment["scope_text"],
            }
            for assessment in assessments
        ]
    )
    readiness = _readiness_dict(session, config)
    evaluated = evaluate_readiness(session, config)
    return {
        **_summary(session, config),
        "powertrain": config.powertrain,
        "drivetrain": config.drivetrain,
        "body_configuration": config.body_configuration,
        "identity_notes": config.identity_notes,
        "identity_notes_problematic": config.identity_verification_state
        not in {"RESOLVED_EXACT", "RESOLVED_SAME_GEOMETRY_GROUP"},
        "fitments": [
            {
                "id": fitment.id,
                "code": fitment.fitment_code,
                "description": fitment.description,
                "wheel_package": fitment.wheel_package,
                "equipment_package": fitment.equipment_package,
                "default": fitment.default_for_configuration,
            }
            for fitment in config.fitments
        ],
        "values": values,
        "assessments": assessments,
        "groups": groups,
        "summary_groups": summary_groups,
        "normalized_value_count": len(values),
        "summary_value_count": len(summary_values),
        "assessment_groups": assessment_groups,
        "geometry_assets": [
            {
                "id": asset.id,
                "role": asset.geometry_role,
                "representation_type": asset.representation_type,
                "fidelity": asset.geometry_fidelity,
                "datum": asset.coordinate_system_version,
                "uncertainty": asset.uncertainty_description,
                "unit": asset.unit,
                "method": asset.geometry_method,
                "body_mirror_inclusion": asset.body_mirror_inclusion,
            }
            for asset in config.geometry_assets
        ],
        "readiness_results": [
            {
                "type": evaluation.readiness_type.value,
                "status": evaluation.status.value,
                "blocking_reasons": evaluation.blocking_reasons,
            }
            for evaluation in evaluated
        ],
        "readiness_view": _readiness_view(readiness),
    }


def _comparison_cell(vehicle: dict[str, Any], parameter_code: str) -> dict[str, Any]:
    values = [value for value in vehicle["values"] if value["parameter_code"] == parameter_code]
    if values:
        items = [
            {
                **value,
                "detail_url": f"/vehicles/{vehicle['stable_vehicle_code']}#value-{value['id']}",
            }
            for value in values
        ]
        tones = {item["state_tone"] for item in items}
        state_tone = (
            "conflict"
            if "conflict" in tones
            else "unknown"
            if "unknown" in tones
            else "rejected"
            if "rejected" in tones
            else "scoped"
            if "scoped" in tones
            else "normal"
        )
        return {
            "items": items,
            "status_label": (
                "Conflicting"
                if "conflict" in tones
                else "Unknown"
                if "unknown" in tones
                else "Rejected"
                if "rejected" in tones
                else "Scoped"
                if "scoped" in tones
                else items[0]["state_label"]
            ),
            "state_tone": state_tone,
            "unknown": False,
            "unknown_reason": None,
        }
    assessments = [
        assessment
        for assessment in vehicle["assessments"]
        if assessment["parameter_code"] == parameter_code
    ]
    if assessments:
        return {
            "items": [],
            "status_label": assessments[0]["availability_state_label"],
            "state_tone": "unknown",
            "unknown": True,
            "unknown_reason": assessments[0]["unknown_reason"],
        }
    return {
        "items": [],
        "status_label": "—",
        "state_tone": "empty",
        "unknown": False,
        "unknown_reason": None,
    }


def _comparison_groups(vehicles: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    available: dict[str, dict[str, Any]] = {}
    for vehicle in vehicles:
        for value in vehicle["values"]:
            definition = available.setdefault(
                value["parameter_code"],
                {
                    "code": value["parameter_code"],
                    "label": value["display_name"],
                    "unit": value["unit"],
                    "family": value["family"],
                },
            )
            if definition["unit"] is None and value["unit"] is not None:
                definition["unit"] = value["unit"]
        for assessment in vehicle["assessments"]:
            available.setdefault(
                assessment["parameter_code"],
                {
                    "code": assessment["parameter_code"],
                    "label": assessment["display_name"],
                    "unit": assessment["unit"],
                    "family": assessment["family"],
                },
            )

    group_order = {key: index for index, (key, _label, _families) in enumerate(FAMILY_GROUPS)}

    def row_for(code: str) -> dict[str, Any]:
        definition = available[code]
        cells = [_comparison_cell(vehicle, code) for vehicle in vehicles]
        semantic_cues = sorted(
            {
                item["semantic_cue"]
                for cell in cells
                for item in cell["items"]
                if item["semantic_cue"]
            }
        )
        return {
            **definition,
            "semantic_cues": semantic_cues,
            "cells": cells,
        }

    def grouped(codes: list[str]) -> list[dict[str, Any]]:
        groups: dict[str, dict[str, Any]] = {}
        for code in codes:
            definition = available[code]
            key, label = FAMILY_GROUP_LOOKUP.get(
                definition["family"], ("other", _humanize(definition["family"]))
            )
            groups.setdefault(key, {"key": key, "label": label, "rows": []})["rows"].append(row_for(code))
        for group in groups.values():
            group["rows"].sort(
                key=lambda row: PARAMETER_ORDER_LOOKUP.get(row["code"], len(PARAMETER_ORDER_LOOKUP))
            )
        return sorted(groups.values(), key=lambda group: group_order.get(group["key"], len(group_order)))

    core = [
        code
        for code in available
        if code in SUMMARY_PARAMETER_CODES
    ]
    technical = [
        code
        for code in available
        if code not in SUMMARY_PARAMETER_CODES
    ]
    core_groups = grouped(core)
    readiness_rows = []
    for readiness_type in READINESS_ORDER:
        if not any(readiness_type == result["type"] for vehicle in vehicles for result in vehicle["readiness_view"]):
            continue
        cells = []
        for vehicle in vehicles:
            result = next(
                (item for item in vehicle["readiness_view"] if item["type"] == readiness_type),
                None,
            )
            cells.append(
                {
                    "items": [],
                    "status_label": result["status_label"] if result else "—",
                    "state_tone": result["status_tone"] if result else "empty",
                    "unknown": False,
                    "unknown_reason": result["first_reason"] if result and result["blocker_count"] else None,
                }
            )
        readiness_rows.append(
            {
                "code": readiness_type,
                "label": READINESS_LABELS[readiness_type],
                "unit": None,
                "semantic_cues": [],
                "cells": cells,
            }
        )
    if readiness_rows:
        core_groups.append({"key": "readiness", "label": "Readiness", "rows": readiness_rows})
    return core_groups, grouped(technical)


@router.get("/", include_in_schema=False)
def home() -> RedirectResponse:
    return RedirectResponse(url="/vehicles", status_code=307)


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/vehicles")
def api_vehicles(
    session: Session = Depends(get_session),
    q: str | None = Query(default=None),
    manufacturer: str | None = Query(default=None),
    body_style: str | None = Query(default=None),
    readiness: str | None = Query(default=None),
) -> dict[str, Any]:
    items = list_vehicles(session, search=q, manufacturer=manufacturer, body_style=body_style, readiness=readiness)
    return {"count": len(items), "items": [_summary(session, item) for item in items]}


@router.get("/api/vehicles/{stable_vehicle_code}")
def api_vehicle(stable_vehicle_code: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    config = get_vehicle(session, stable_vehicle_code)
    if config is None:
        raise HTTPException(status_code=404, detail="vehicle configuration not found")
    return _detail(session, config)


@router.get("/api/issues")
def api_issues(session: Session = Depends(get_session)) -> dict[str, Any]:
    rows = list_issue_rows(session)
    return {
        "count": len(rows),
        "items": [
            {
                "kind": row["kind"],
                "code": row["code"],
                "severity": row["severity"],
                "status": row["status"],
                "vehicle": row["vehicle"].stable_vehicle_code if row["vehicle"] else None,
                "message": row["message"],
            }
            for row in rows
        ],
    }


@router.get("/vehicles", response_class=HTMLResponse)
def vehicles_page(
    request: Request,
    session: Session = Depends(get_session),
    q: str | None = Query(default=None),
    manufacturer: str | None = Query(default=None),
    body_style: str | None = Query(default=None),
    readiness: str | None = Query(default=None),
) -> HTMLResponse:
    items = list_vehicles(session, search=q, manufacturer=manufacturer, body_style=body_style, readiness=readiness)
    catalog = [_summary(session, item) for item in list_vehicles(session)]
    return templates.TemplateResponse(
        request=request,
        name="vehicles.html",
        context={
            "vehicles": [_summary(session, item) for item in items],
            "filter_options": _catalog_filters(catalog),
            "q": q or "",
            "manufacturer": manufacturer or "",
            "body_style": body_style or "",
            "readiness": readiness or "",
        },
    )


@router.get("/vehicles/{stable_vehicle_code}", response_class=HTMLResponse)
def vehicle_page(stable_vehicle_code: str, request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    config = get_vehicle(session, stable_vehicle_code)
    if config is None:
        raise HTTPException(status_code=404, detail="vehicle configuration not found")
    return templates.TemplateResponse(request=request, name="vehicle_detail.html", context={"vehicle": _detail(session, config)})


@router.get("/issues", response_class=HTMLResponse)
def issues_page(
    request: Request,
    session: Session = Depends(get_session),
    kind: str | None = Query(default=None),
) -> HTMLResponse:
    rows = list_issue_rows(session)
    if kind:
        rows = [row for row in rows if row["kind"] == kind]
    return templates.TemplateResponse(
        request=request,
        name="issues.html",
        context={
            "issues": [_issue_view(row) for row in rows],
            "issue_kind": kind or "",
        },
    )


@router.get("/compare", response_class=HTMLResponse)
def compare_page(
    request: Request,
    session: Session = Depends(get_session),
    codes: str | None = Query(default=None),
    vehicle_1: str | None = Query(default=None),
    vehicle_2: str | None = Query(default=None),
    vehicle_3: str | None = Query(default=None),
    vehicle_4: str | None = Query(default=None),
) -> HTMLResponse:
    requested_slots = [vehicle_1, vehicle_2, vehicle_3, vehicle_4]
    explicit_slots = any(f"vehicle_{number}" in request.query_params for number in range(1, 5))
    if not explicit_slots:
        legacy_codes = [code.strip() for code in (codes or "").split(",") if code.strip()][:4]
        requested_slots = legacy_codes + [None] * (4 - len(legacy_codes))

    shared_filters, slot_filters = _compare_filter_state(request)
    action = _slot_action(request)
    if action is not None:
        action_name, slot_number = action
        slot = slot_filters[slot_number - 1]
        if action_name == "search_all":
            slot["filters"] = {key: "" for key in COMPARE_FILTER_KEYS}
            slot["scope"] = "all"
        else:
            slot["filters"] = {key: "" for key in COMPARE_FILTER_KEYS}
            slot["scope"] = "shared"
        slot["has_override"] = False

    selection_messages: list[str] = []
    selected_slot_codes: list[str] = []
    configs_by_slot: list[VehicleConfiguration | None] = []
    seen_codes: set[str] = set()
    for number, raw_code in enumerate(requested_slots, start=1):
        code = _clean_query_value(raw_code)
        if not code:
            selected_slot_codes.append("")
            configs_by_slot.append(None)
            continue
        if code in seen_codes:
            selection_messages.append(
                f"Vehicle {number} was cleared because {code} is already selected in another slot."
            )
            selected_slot_codes.append("")
            configs_by_slot.append(None)
            continue
        config = get_vehicle(session, code)
        if config is None:
            selection_messages.append(f"Vehicle {number} was cleared because {code} is not an exact catalog configuration.")
            selected_slot_codes.append("")
            configs_by_slot.append(None)
            continue
        seen_codes.add(code)
        selected_slot_codes.append(code)
        configs_by_slot.append(config)

    vehicles = []
    for number, config in enumerate(configs_by_slot, start=1):
        if config is None:
            continue
        vehicle = _detail(session, config)
        vehicle["comparison_slot"] = number
        vehicles.append(vehicle)

    catalog = list_vehicles(session)
    catalog_filter_records = [
        {
            "manufacturer_code": item.vehicle_model.manufacturer.canonical_name,
            "manufacturer": item.vehicle_model.manufacturer.display_name,
            "body_style": item.body_style,
            "powertrain": item.powertrain,
            "identity_time_basis": item.identity_time_basis,
        }
        for item in catalog
    ]
    filter_options = _catalog_filters(catalog_filter_records)
    selected_by_code = {vehicle["stable_vehicle_code"]: vehicle for vehicle in vehicles}
    compare_slots = []
    for slot, selected_code in zip(slot_filters, selected_slot_codes):
        effective_filters = _effective_compare_filters(shared_filters, slot)
        options, candidate_count, candidate_truncated = _compare_candidates(
            session,
            effective_filters,
            selected_code=selected_code,
            selected_summary=selected_by_code.get(selected_code),
        )
        compare_slots.append(
            {
                **slot,
                "selected_code": selected_code,
                "selected_vehicle": selected_by_code.get(selected_code),
                "effective_filters": effective_filters,
                "candidate_options": options,
                "candidate_count": candidate_count,
                "candidate_truncated": candidate_truncated,
                "scope_label": (
                    "Searches all vehicles"
                    if slot["scope"] == "all"
                    else "Uses slot filters plus shared defaults"
                    if slot["has_override"]
                    else "Uses shared filters"
                ),
            }
        )
    core_groups, technical_groups = _comparison_groups(vehicles)
    return templates.TemplateResponse(
        request=request,
        name="compare.html",
        context={
            "vehicles": vehicles,
            "shared_filters": shared_filters,
            "filter_options": filter_options,
            "compare_slots": compare_slots,
            "selected_codes": ",".join(selected_slot_codes),
            "selected_codes_list": [code for code in selected_slot_codes if code],
            "selected_slot_codes": selected_slot_codes,
            "selection_messages": selection_messages,
            "compare_ready": len(vehicles) >= 2,
            "candidate_limit": COMPARE_CANDIDATE_LIMIT,
            "comparison_core_groups": core_groups,
            "comparison_technical_groups": technical_groups,
            "technical_field_count": sum(len(group["rows"]) for group in technical_groups),
        },
    )


def _export_response(session: Session, codes: str | None, xlsx: bool) -> Response:
    selected_codes = [code.strip() for code in (codes or "").split(",") if code.strip()]
    rows = export_rows(session, selected_codes or None)
    if xlsx:
        return Response(
            content=xlsx_bytes(rows),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=vehicle-engineering-export.xlsx"},
        )
    return Response(
        content=csv_bytes(rows),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=vehicle-engineering-export.csv"},
    )


@router.get("/exports/vehicles.csv")
def export_csv(codes: str | None = Query(default=None), session: Session = Depends(get_session)) -> Response:
    return _export_response(session, codes, xlsx=False)


@router.get("/exports/vehicles.xlsx")
def export_xlsx(codes: str | None = Query(default=None), session: Session = Depends(get_session)) -> Response:
    return _export_response(session, codes, xlsx=True)
