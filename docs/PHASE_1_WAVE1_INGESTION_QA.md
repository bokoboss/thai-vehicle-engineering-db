# Phase 1 Wave 1 ingestion and real-data UI QA

Status: **PASS — local curated database built and promoted after staging QA**
Date: 2026-08-31
Starting `main`: `60f157e832fe0425e706d07fb9052b939449117f`
Execution branch: `codex/phase-1-wave1-controlled-ingestion-web-smoke`

## Reproduction

From the repository root:

```text
python scripts/build_wave1_curated_db.py
$env:DATABASE_URL="sqlite:///./vehicle_engineering_curated.db"
python -m uvicorn app.main:app --reload
```

The build script uses a disposable `vehicle_engineering_curated.staging.db`, runs Alembic, registry-only `app.curate init`, validates all manifests, imports them through the existing create-only importer, performs database-level QA, proves CSV/XLSX exports, and only then promotes the database to `vehicle_engineering_curated.db`. Both database names and the generated export proofs are ignored by Git.

The script refuses an existing staging database and refuses to replace an existing final database unless `--replace-final` is explicit. A failed run therefore cannot replace an accepted final database.

## Manifest gate

- Sentinel manifests: 3
- Wave 1 manifests: 18
- Total manifests validated/imported: 21
- Distinct `stable_vehicle_code` values: 21
- HOLD records imported: 0
- Phase 0 synthetic vehicle rows imported: 0
- Post-`app.curate init` registry-only proof: 48 parameter definitions, 0 vehicles
- Manifest source entries: 55
- Unique compatible source codes persisted: 54

The two Isuzu manifests sharing `ISUZU_TH_22_4WD_LAUNCH_20260227` were corrected to carry one common source-level applicability note. Exact model/grade applicability remains on each source observation identity claim. No engineering numeric value was changed, and the importer’s strict source metadata reuse guard remains active.

## Final database QA counts

| Record | Count |
|---|---:|
| Vehicle configurations | 21 |
| Parameter definitions | 48 |
| Manufacturers | 13 |
| Vehicle models | 21 |
| Source documents | 54 |
| Source observations | 211 |
| Normalized values | 247 |
| Parameter assessments | 47 |
| Load conditions | 21 |
| Fitments | 14 |
| Axles | 0 |
| Steering relations | 0 |
| Geometry assets | 0 |
| Conflict decisions | 0 |
| Persisted readiness results | 140 |

The QA also passed source-observation lineage for every published/measured value, no naked published/measured values, same-vehicle fitment/load scope, no direct derived/estimated values, assessment-state semantics, deterministic stable-code matching, and readiness evaluation/persistence for all 21 configurations and 14 fitment scopes.

Readiness status by scope:

- `IDENTITY_RESOLVED`: 35 READY
- `DIMENSION_READY`: 27 READY, 8 NOT_READY
- `AVT_READY`: 35 NOT_READY
- `RAMP_SCREENING_READY`: 35 NOT_READY

## Representative engineering proofs

- BYD ATTO 3 retains separate 175 mm unladen and 150 mm laden clearances with `UNLADEN` and `OEM_LADEN` load conditions.
- Mitsubishi Triton retains `EDITION_RELEASE`, null model-year fields, and the published 6.2 m turning radius with `OEM_UNSPECIFIED` reference semantics.
- Volvo EX30 retains `WHEEL19`, distinct body/open-mirror/folded-mirror widths, kerb-plus-one-person load scope, two `CONFLICTING` official turning text values (`10.7 m` and `11 m`), zero conflict decisions, and no normalized turning radius.
- Honda Civic and Accord authority-B values remain linked to `REPUTABLE_SECONDARY` source documents.
- Tesla Model 3 and Model Y retain turning-circle text only; no half-diameter radius was hand-created.
- MG IM6 retains the OEM four-wheel-steering observation without invented rear-steering kinematics or steering-relation rows.

## Export proof

- CSV: `vehicle_engineering_curated.wave1.csv`, 294 data rows covering all 21 vehicles.
- XLSX: `vehicle_engineering_curated.wave1.xlsx`, readable `Engineering Data` sheet with the accepted export headers.
- Identity-time fields, source observation/document codes, conflict state, fitment scope, load-condition scope, and assessment reasons were present in the export proof.
- No credentials were exposed.

## Real-data web smoke

HTTP/TestClient and live-Uvicorn smoke against `vehicle_engineering_curated.db` passed:

- `/vehicles`: 200; renders the evidence-aware catalog wording and 21 exact configurations without the Phase 0 fixture label.
- `/vehicles?q=ATTO 3`: 200; returns the BYD ATTO 3 stable code.
- BYD detail: 200; renders scope and source-document title.
- Volvo API detail: 200; renders all three width parameters, four `WHEEL19` values, two load-scoped values, identified source documents, and both conflicting turning text values.
- `/compare` with BYD, Tesla, Honda, and MG: 200; all four selected stable codes render.
- `/issues` and `/api/issues`: 200; readiness blockers are visible.
- `/api/vehicles`: 200; count 21.
- CSV/XLSX export routes: 200 with the expected media types.

## Verification record

- `python -m pytest`: **104 passed**.
- Alembic SQLite upgrade completed from base to head during the controlled build.
- The migration suite's PostgreSQL offline DDL qualification passed; no live PostgreSQL service was required.
- A live local Uvicorn smoke against the promoted database returned HTTP 200 for the routes listed above and was stopped after the check.
- Running the build command without `--replace-final` correctly refuses to overwrite the accepted final database.

## Residual findings

The database is intentionally not AVT-ready or ramp-screening-ready. Current blockers include missing AVT outer-face tyre tracks, unresolved turning-envelope semantics, missing explicit AVT steering inputs/body envelope geometry, and no approved screening-angle result. Eight configuration/fitment scopes remain dimension-not-ready because the required reported-width parameter is not available under the accepted width semantics. These are surfaced as readiness/issues findings; no values were guessed or promoted. The nine HOLD records remain excluded.

No schema migration, importer-rule weakening, automatic derivation, AVT geometry synthesis, or major UI redesign was needed.
