from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ReadinessReport:
    fitment_code: str
    readiness_type: str
    status: str
    blocking_reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ImportReport:
    status: str
    stable_vehicle_code: str
    database_identifier: str
    sources_created: int
    sources_reused: int
    observations: int
    normalized_values: int
    assessments: int
    loads: int
    fitments: int
    axles: int
    steering_relations: int
    geometry_assets: int
    conflicts: int
    conflict_decisions: int
    readiness: list[ReadinessReport]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def render(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=2, sort_keys=True)


def render_init_report(parameter_count: int) -> str:
    return json.dumps(
        {
            "action": "init",
            "parameter_definitions": parameter_count,
            "status": "PASS",
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def render_validation_report(stable_vehicle_code: str) -> str:
    return json.dumps(
        {
            "action": "validate",
            "stable_vehicle_code": stable_vehicle_code,
            "status": "PASS",
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
