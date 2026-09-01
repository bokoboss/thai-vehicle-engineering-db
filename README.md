# Thailand Vehicle Engineering Database

Engineering-grade vehicle geometry and maneuverability database for vehicles used in Thailand.

## Product intent

This is a **data project with a thin web application**.

The difficult work is:
- finding the right vehicle/configuration;
- locating authoritative sources;
- preserving source semantics;
- separating published / measured / derived / estimated / unknown data;
- determining when a record is genuinely ready for engineering use.

The web application should remain simple.

## Intended engineering use

- Autodesk Vehicle Tracking preparation and swept-path work
- parking/access/porte-cochère design
- ramp and vertical-clearance assessment
- vehicle comparison
- future Thai design-vehicle development
- traceable client-facing engineering answers

## Working principle

> Unknown is a valid engineering result. Unsupported precision is not.

## Current state

**Phase 1 Wave 1 curation is accepted for controlled local ingestion.** The repository contains 21 reviewed manifests; the curated SQLite database and export proofs are generated locally and remain ignored by Git.

Foundation research returned **GO WITH CONDITIONS — High confidence** and the required data-contract amendments have been incorporated on PR #1.

The repository now contains:
- product requirements
- evidence-first Vehicle Data Standard
- logical relational schema
- machine-readable parameter registry
- AVT mapping specification
- ramp/vertical-clearance methodology
- source curation protocol
- Thailand source landscape
- 30-vehicle pilot target registry
- first 7-vehicle real-source semantic pack
- fixed lean technology stack
- bounded Codex Phase 0 execution contract/prompt
- the FastAPI/SQLAlchemy/Alembic Phase 0 foundation, deterministic semantic fixtures, exports and CI

## Lean application stack

Phase 0 is fixed to:
- Python
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic 2.x
- Jinja2
- limited HTMX
- SQLite locally / PostgreSQL-compatible persistence
- pytest
- openpyxl

No React SPA or microservices are planned for the MVP.

## Run the accepted curated application locally

The current local-use workflow is the accepted Wave 1 curated application, backed only by the ignored file `vehicle_engineering_curated.db`. This is a FastAPI/Jinja server-rendered web application: pages are rendered by the server, no static `index.html` is required, and `/` is the application start URL that redirects to the vehicle catalog at `/vehicles`.

### Windows first-time setup

From the repository folder, run the following once if the project environment or accepted database is not already present:

```text
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe scripts\build_wave1_curated_db.py
```

The controlled build creates the accepted curated database after its staging and QA steps. It refuses an existing final database by default; do not use `--replace-final` unless an intentional, reviewed rebuild is required. If an accepted `vehicle_engineering_curated.db` is already present, install dependencies and do not run the build again.

### Windows normal daily launch

Double-click [`Start Vehicle Engineering DB.cmd`](Start%20Vehicle%20Engineering%20DB.cmd) in the repository folder. It finds the repository-relative runner, prefers `.venv`, sets the curated database URL, starts the server without reload, and opens `http://127.0.0.1:8000/` in the default browser. The root URL redirects to `/vehicles`.

The launcher does not run seed, migration, build, or replacement commands on each launch. To stop the local server, press `Ctrl+C` in its console window.

### Manual equivalent

From the repository root, the manual equivalent is:

```text
.venv\Scripts\python.exe scripts\run_local_app.py
```

If `.venv` is not available, use an installed Python 3.11+ interpreter:

```text
py -3 scripts\run_local_app.py
```

When invoked with absolute paths, the runner also resolves the repository correctly if the caller's working directory is elsewhere.

The runner uses `sqlite:///./vehicle_engineering_curated.db` and never falls back to `vehicle_engineering.db`. If port 8000 belongs to another process, it reports the conflict and does not kill that process. If the curated application is already safely detected on port 8000, it reuses that running URL.

If `vehicle_engineering_curated.db` is missing, run the one-time controlled build above and launch again. The runner fails clearly rather than creating an empty database or using synthetic data.

Do not run `python -m app.seed` against `vehicle_engineering_curated.db`; that command creates Phase 0 synthetic fixtures and is not part of the curated workflow.

### Controlled curated database build details

The build script performs Alembic upgrade, registry-only curation initialization, validation and create-only import of the three sentinels plus all 18 Wave 1 manifests, database-level QA, CSV/XLSX export proof, and final promotion. It refuses an existing staging database and does not replace an existing final database unless `--replace-final` is supplied after a successful staging run. If a run stops, inspect and remove only the disposable `vehicle_engineering_curated.staging.db` (and any matching SQLite sidecar files) before retrying. The database, generated export proofs, and staging artifacts are local/ignored files.

See [`docs/PHASE_1_WAVE1_INGESTION_QA.md`](docs/PHASE_1_WAVE1_INGESTION_QA.md) for the accepted curation and verification record.

## Historical Phase 0 fixture workflow

The original Phase 0 workflow remains useful for software-contract qualification, but it is not the current real-data application path. The local fixture database is intentionally disposable and is ignored by Git. From the repository root:

```text
python -m pip install -e ".[dev]"
python -m alembic upgrade head
python -m app.seed
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/vehicles`. These seeded records are deterministic semantic fixtures only; they are not production vehicle records. See [`docs/PHASE_0_IMPLEMENTATION.md`](docs/PHASE_0_IMPLEMENTATION.md) for the physical schema/file layout, fixture matrix and export/API details.

Run the complete Phase 0 qualification with:

```text
python -m pytest
python -m alembic downgrade base
python -m alembic upgrade head
python -m app.seed
```

## Core documents

Start with:

1. `PROJECT_PROFILE.md`
2. `AGENTS.md`
3. `docs/PRODUCT_REQUIREMENTS.md`
4. `docs/VEHICLE_DATA_STANDARD.md`
5. `docs/LOGICAL_SCHEMA.md`
6. `docs/PARAMETER_REGISTRY_V1.md`
7. `docs/AVT_MAPPING_SPEC.md`
8. `docs/RAMP_VERTICAL_CLEARANCE_METHOD.md`
9. `docs/SOURCE_CURATION_PROTOCOL.md`
10. `docs/SOURCE_LANDSCAPE.md`
11. `docs/PILOT_AND_ACCEPTANCE.md`
12. `docs/PHASE_0_EXECUTION_CONTRACT.md`
13. `docs/CURATION_INGESTION_CONTRACT_V1.md`
14. `docs/PHASE_1_WAVE1_INGESTION_QA.md`

Machine-readable/reference material:
- `data/reference/parameter_registry_v1.json`
- `data/pilot/pilot_targets_v1.json`
- `data/pilot/source_pack_01.json`

## Roadmap

### Foundation
Research, semantics, architecture, source strategy.

Status: candidate ready for acceptance.

### Phase 0 — Software foundation
Build the small evidence-first FastAPI application, physical schema, migrations, fixtures, exports and CI.

Executor: Codex after Foundation PR #1 is accepted/merged.

### Phase 1 — Pilot curation
Curate the 30 target configurations using the source protocol.

Primary effort: ChatGPT research/data curation + engineering QA.

### Phase 2 — Usable shared MVP
Complete practical search/compare/evidence UI, deploy a shared read-only service, and validate with real engineering questions.

### Phase 3 — Scale data
Expand by Thai market relevance and fill difficult missing parameters over time.

This phase is continuous data work, not a large software rebuild.

## Development workflow

Lean adoption of:
https://github.com/bokoboss/engineering-development-workflow

Operating model:

```text
ChatGPT   = research / data methodology / control plane / review
GitHub    = authoritative project state
Codex     = bounded implementation when local code/runtime work is needed
```

## Large source files

Do not blindly commit OEM PDF/image archives into Git.

Git should hold:
- metadata;
- structured observations;
- curated reference data where appropriate;
- schema;
- rules;
- tests;
- documentation.

Large source snapshots should use a separate retention/storage strategy.
