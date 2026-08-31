# Phase 0 Implementation Notes

Status: implementation plus bounded control-plane remediation on `codex/phase-0-data-foundation`
Date: 2026-08-31

## Bootstrap

```text
python -m pip install -e ".[dev]"
python -m alembic upgrade head
python -m app.seed
python -m uvicorn app.main:app --reload
```

The default SQLite file is `vehicle_engineering.db`. Set `DATABASE_URL` to a PostgreSQL-compatible SQLAlchemy URL for a shared relational deployment. The domain does not use SQLite-specific SQL or semantics.

## Implemented layout

```text
app/
├─ main.py                         FastAPI application and static mount
├─ config.py                       environment/project settings
├─ db/
│  ├─ base.py                      Alembic metadata import boundary
│  ├─ session.py                   portable engine/session factory
│  ├─ models/entities.py            relational evidence-first schema
│  └─ repositories.py               search/detail/issues access boundary
├─ domain/
│  ├─ enums.py                     controlled semantic vocabulary
│  ├─ schemas.py                    Pydantic 2 typed contracts
│  ├─ validation.py                 fail-closed semantic validators
│  ├─ readiness.py                  rule-based readiness results
│  ├─ avt_mapping.py                Level 0/1 AVT preparation adapter
│  └─ derivations.py                versioned deterministic derivation helpers
├─ services/foundation.py           validated persistence orchestration
├─ exports/exporter.py              evidence-aware CSV/XLSX flattening
├─ seed/registry.py                 machine registry validation/seed
├─ seed/fixtures.py                 deterministic Phase 0 contract fixtures
└─ web/                             Jinja2 pages and project-owned CSS
alembic/                             versioned schema boundary
tests/                               unit, contract and integration qualification
```

The physical schema retains separate tables for configurations, fitments, axles, steering relations, load conditions, source documents, raw observations, parameter definitions, normalized values, evidence links, assessments, derivation rules/runs/inputs, conflict decisions, geometry assets, readiness, QA findings and AVT mapping results.

## Deterministic fixture matrix

The seed builder creates `FIXTURE-*` records only. The 17 required cases are represented by these fixtures:

| Required case | Fixture |
|---|---|
| Exact primary published value | `FIXTURE-PRIMARY-PUBLISHED` |
| OEM turning value with unknown curb/wall semantics | `FIXTURE-TURNING-UNSPECIFIED` |
| Published + conflicting observations | `FIXTURE-CONFLICTING-VALUE` |
| Nominal-width AVT track estimate rejected | `FIXTURE-AVT-TRACK-SCREENING` |
| Direct AVT outer-face track | `FIXTURE-AVT-TRACK-DIRECT` |
| Unknown/not-found assessment | `FIXTURE-UNKNOWN-ASSESSMENT` |
| Measured/scaled estimate with uncertainty | `FIXTURE-SCALED-ESTIMATE` |
| Steering-wheel turns separate from wheel angle/time | `FIXTURE-STEERING-SEPARATION` |
| Curb-to-curb with unresolved axle scope | `FIXTURE-CURB-UNKNOWN-AXLE` |
| Body-only vs body+loads wall envelope scope | `FIXTURE-WALL-SCOPES` |
| Laden between-axles vs axle clearance | `FIXTURE-CLEARANCE-LOADS` |
| Structured load condition | `FIXTURE-CLEARANCE-LOADS` |
| Static-loaded tyre radius | `FIXTURE-STATIC-LOADED-RADIUS` |
| Four-wheel/rear steering structure | `FIXTURE-REAR-STEERING` |
| Width with unknown mirror semantics | `FIXTURE-WIDTH-UNSPECIFIED` |
| Side silhouette vs lower envelope geometry roles | `FIXTURE-GEOMETRY-ROLES` |
| Screening ramp namespace and lineage | `FIXTURE-RAMP-SCREENING` |

The direct AVT fixture additionally contains the complete set of explicit fields needed for a positive `AVT_READY` result. The screening track fixture retains its estimated value and derivation lineage but remains `NOT_READY`.

## Control-plane remediation controls

- Alembic revision `0001_phase0_foundation` is a frozen, self-contained set of explicit table, constraint, index and reverse-order downgrade operations; it does not execute live ORM metadata.
- The normalized-value write service applies the parameter registry's `requires_attributes`, including controlled turning semantics and clearance type/load-condition scope.
- `AVAILABLE + NONE` is rejected. `PUBLISHED`/`MEASURED` values require source-observation links, while `ESTIMATED` values require source evidence or controlled derivation lineage plus method/limitation metadata.
- Readiness and AVT mapping use one auditable candidate resolver. Unresolved, superseded or rejected candidates cannot be selected; conflicting candidates require a non-superseded `ConflictDecision` selecting the exact value in the applicable scope.
- Derivations propagate a single input fitment scope and reject mixed fitments before creating an output.

## Read surfaces and exports

- `GET /vehicles` — search/list page
- `GET /vehicles/{stable_vehicle_code}` — evidence-aware detail page
- `GET /compare?codes=CODE_A,CODE_B` — compact comparison page
- `GET /issues` — readiness/QA work queue
- `GET /api/vehicles` and `GET /api/vehicles/{stable_vehicle_code}` — typed JSON-equivalent read surfaces
- `GET /exports/vehicles.csv` — UTF-8 CSV with state/source/lineage columns
- `GET /exports/vehicles.xlsx` — readable workbook with the same columns

No write endpoint is exposed in Phase 0. Curation helpers are deliberately service-level and maintainer-oriented.

## Qualification

The required local qualification is:

```text
python -m pytest
python -m alembic downgrade base
python -m alembic upgrade head
python -m app.seed
```

The test suite includes a fresh migration upgrade/downgrade/re-upgrade cycle, orthogonal state checks, raw-to-normalized evidence links, controlled derivation lineage, AVT/ramp fail-closed rules, readiness blockers, API/page smoke tests and deterministic CSV/XLSX checks.

## Explicit Phase 0 boundaries

This implementation does not populate production vehicles, scrape sources, solve ramps, model 3D underbody collision, reverse-engineer ATL/ATX or write production ATL/ATX files. The checked-in `data/pilot/source_pack_01.json` remains reference material for semantic curation.
