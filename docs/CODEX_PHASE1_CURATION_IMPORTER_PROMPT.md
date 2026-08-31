# Codex Prompt — Phase 1 Create-Only Curation Importer v1

Repository:
https://github.com/bokoboss/thai-vehicle-engineering-db

Local working directory:
D:\R&D\thai-vehicle-engineering-db

GitHub Issue:
https://github.com/bokoboss/thai-vehicle-engineering-db/issues/15

## Model / effort / context

- Model: **GPT-5.6 Luna**
- Reasoning effort: **Max**
- Start a **new Codex chat**

## Mission

Implement Issue #15 exactly as a bounded Phase 1 maintainer tool.

The goal is a small create-only manifest importer that writes curated evidence through the existing evidence-first service/domain boundary and proves the path with three real sentinel manifests.

Do not widen scope into a generic ETL system, admin UI, public write API, scraping, update/merge mode, AVT changes, ramp changes, or a new migration.

## Preflight

Before implementation:

1. Work in:
   `D:\R&D\thai-vehicle-engineering-db`

2. Run:
   - `git status`
   - current branch / HEAD
   - remotes
   - `git fetch origin`

3. Confirm:
   - PR #14 has been accepted and merged;
   - Issue #15 status is READY FOR EXECUTION;
   - local `main` can safely fast-forward to `origin/main`;
   - working tree is clean.

4. Read all authoritative files:
   - `PROJECT_PROFILE.md`
   - `AGENTS.md`
   - `docs/CURATION_INGESTION_CONTRACT_V1.md`
   - `docs/SCRUTINY_PHASE1_INGESTION_V1.md`
   - `docs/PHASE_1_SENTINEL_MANIFEST_QA.md`
   - `data/curation/schema/curation_manifest_v1.example.json`
   - three files under `data/curation/manifests/sentinel/`
   - `docs/VEHICLE_DATA_STANDARD.md`
   - `docs/LOGICAL_SCHEMA.md`
   - `docs/SOURCE_CURATION_PROTOCOL.md`
   - Issue #15
   - existing `app/services/foundation.py`
   - existing readiness/export implementation
   - existing tests

If PR #14 is not merged, stop.

## Branch

Create:

`codex/phase-1-curation-importer-v1`

Do not modify main directly.

## Fixed CLI

Implement:

```text
python -m app.curate init
python -m app.curate validate <manifest.json>
python -m app.curate import <manifest.json>
python -m app.curate import <manifest.json> --dry-run
```

Use a small maintainable layout under `app/curate/`.

No frontend work.

## Critical contract rules

### CREATE_ONLY

If `stable_vehicle_code` already exists:
- fail before vehicle writes;
- do not overwrite/update/merge.

### Atomic transaction

One manifest = one transaction.

Any failure rolls back all rows created by that manifest.

### Registry-only init

`app.curate init` seeds parameter definitions only.

It must not seed Phase 0 synthetic vehicle fixtures.

### Strict manifest schemas

Use Pydantic with extra fields forbidden.

Validate:
- manifest version/mode;
- unique local codes;
- all cross-references;
- controlled enum values;
- Identity Time Basis;
- parameter registry membership.

### Typed value routing

Manifest field `value` is mapped using parameter registry `data_type`:

- NUMBER -> numeric_value
- TEXT -> text_value
- BOOLEAN -> boolean_value
- ENUM -> enum_value
- JSON -> json_value

Reject incompatible primitive types. Do not silently cast.

### Evidence

PUBLISHED/MEASURED available values require observation references.

Resolve them and call existing `create_normalized_value` with evidence links.

Do not create normalized engineering values directly through ORM.

### No direct derivation entry

Manifest v1 rejects:
- DERIVED
- ESTIMATED

Do not add exceptions.

### Sources

Canonical source type must use current app enum.

Preserve manifest `source_subtype_raw` losslessly in an existing notes field because no physical subtype column exists.

Existing source_code:
- compatible -> reuse
- incompatible -> fail
- never silently mutate

### Manufacturer/model

Reuse exact canonical manufacturer/model keys.

Create only if absent.

Do not silently rewrite existing manufacturer/model display/canonical metadata.

### Scope

Load conditions, fitments, axles, observations, steering, geometry and values must resolve within the imported exact configuration as required by existing scope validators.

### Conflicts

Do not auto-resolve.

The Volvo sentinel must retain two conflicting turning text values and zero conflict decisions.

### Missing parameters

Use parameter assessments.

Never create numeric 0/null normalized placeholders.

## Required negative tests

Implement every negative gate in Issue #15, including:
- unknown parameter
- undeclared source
- missing evidence observation
- missing load/fitment reference
- direct DERIVED/ESTIMATED
- wrong primitive type
- duplicate stable vehicle code
- incompatible source reuse
- invalid Identity Time Basis
- final-step failure -> full rollback
- validate/dry-run persist nothing
- init has no Phase 0 synthetic vehicles

## Sentinel acceptance proof

Use a deterministic clean curated SQLite DB.

Import exactly:

1. BYD ATTO 3 MY24 Extended Local
2. Mitsubishi Triton ULTRA 4WD AT 2023
3. Volvo EX30 Ultra SMER MY2026

Prove after import:

### BYD
- exact MODEL_YEAR identity
- two distinct load conditions
- 175 mm unladen clearance
- 150 mm laden clearance
- both values retain observation/source lineage
- AVT outer-face track remains unknown

### Triton
- exact EDITION_RELEASE identity
- `model_year_from IS NULL`
- identity readiness passes
- turning radius 6.2 m remains OEM_UNSPECIFIED curb/wall reference
- AVT readiness remains blocked

### Volvo
- exact MY2026 identity
- exact WHEEL19 fitment exists
- fitment-specific tyre/wheel values stay scoped to it
- body/open/folded width values remain distinct
- kerb+1 clearance state preserved
- both conflicting turning text values exist
- no conflict decision exists
- normalized turning radius is absent
- UNKNOWN turning-radius assessment exists
- turning/AVT readiness fails closed

### Lineage

For representative values from all 3 vehicles, query:

vehicle -> normalized value -> evidence link -> source observation -> source document

and assert the intended source code/raw label.

### Export

Export curated data to CSV and XLSX.

Verify identity-time fields and provenance fields are present and Volvo conflict state is not collapsed.

## Qualification

Run:

```text
python -m pytest
```

Then on a clean dedicated curated DB:

```powershell
$env:DATABASE_URL="sqlite:///./vehicle_engineering_curated_test.db"
python -m alembic upgrade head
python -m app.curate init
python -m app.curate validate data/curation/manifests/sentinel/byd_atto3_my24_extended_local_v1.json
python -m app.curate validate data/curation/manifests/sentinel/mitsubishi_triton_ultra_4wd_at_2023_v1.json
python -m app.curate validate data/curation/manifests/sentinel/volvo_ex30_ultra_smer_my2026_v1.json
python -m app.curate import data/curation/manifests/sentinel/byd_atto3_my24_extended_local_v1.json
python -m app.curate import data/curation/manifests/sentinel/mitsubishi_triton_ultra_4wd_at_2023_v1.json
python -m app.curate import data/curation/manifests/sentinel/volvo_ex30_ultra_smer_my2026_v1.json
```

Also qualify:
- PostgreSQL metadata/offline portability
- CSV/XLSX
- full existing test suite
- CI

Do not commit generated SQLite databases or exported QA files unless the contract explicitly requires a fixture file.

## No migration

Issue #15 should require **no Alembic revision**.

If you conclude a migration is necessary, stop and report the exact blocker rather than creating one.

## PR

Push the branch and open one PR against `main`.

Do not merge.

## Final report

Return:

1. starting main SHA
2. branch
3. final HEAD
4. PR number/link
5. changed files
6. importer architecture
7. negative-test matrix
8. sentinel proof matrix
9. lineage proof
10. readiness results for all 3 sentinels
11. CSV/XLSX qualification
12. total pytest result
13. CI run/link/status
14. confirmation no migration was created
15. protected-contract deviations, expected none
16. residual limitations
17. explicit confirmation PR remains open and unmerged
