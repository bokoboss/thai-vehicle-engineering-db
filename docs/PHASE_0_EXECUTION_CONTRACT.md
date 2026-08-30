# Phase 0 Execution Contract

Status: READY AFTER FOUNDATION PR #1 MERGE  
Prepared: 2026-08-30

## Objective

Implement the smallest maintainable FastAPI application and relational data foundation that proves the accepted vehicle evidence/data contract without expanding into production data collection or advanced engineering tools.

## Authoritative inputs

Read in this order:

1. `PROJECT_PROFILE.md`
2. `AGENTS.md`
3. `docs/VEHICLE_DATA_STANDARD.md`
4. `docs/LOGICAL_SCHEMA.md`
5. `docs/PARAMETER_REGISTRY_V1.md`
6. `data/reference/parameter_registry_v1.json`
7. `docs/ARCHITECTURE.md`
8. `docs/TECH_STACK_DECISION.md`
9. `docs/PILOT_AND_ACCEPTANCE.md`
10. `docs/SOURCE_CURATION_PROTOCOL.md`
11. `data/pilot/source_pack_01.json`
12. GitHub Issue #2

If these conflict, stop and report rather than choosing silently.

## Fixed technology decision

Use:

- Python
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic 2.x
- Jinja2 server-rendered HTML
- HTMX only for small interactions when useful
- project-owned minimal CSS
- SQLite local/test
- PostgreSQL-compatible relational design
- pytest
- openpyxl for XLSX

Do not reopen React/Next.js/Django/microservice selection unless a concrete blocker is demonstrated.

## Repository layout target

A reasonable target is:

```text
app/
├─ main.py
├─ config.py
├─ db/
│  ├─ base.py
│  ├─ session.py
│  ├─ models/
│  └─ repositories/
├─ domain/
│  ├─ enums.py
│  ├─ schemas.py
│  ├─ validation.py
│  ├─ readiness.py
│  └─ avt_mapping.py
├─ services/
├─ exports/
├─ web/
│  ├─ routes/
│  ├─ templates/
│  └─ static/
└─ seed/

alembic/
tests/
├─ unit/
├─ integration/
├─ contract/
└─ fixtures/

data/reference/
docs/
```

Codex may adjust file boundaries while preserving a monolithic application and clear domain/persistence separation.

## Scope

Implement:

1. project/bootstrap configuration;
2. SQLAlchemy physical schema and Alembic migration(s);
3. parameter registry seed;
4. typed domain schemas/enums;
5. repository/data-access layer;
6. deterministic validation rules;
7. derivation-rule/run lineage model;
8. readiness evaluation skeleton with fail-closed semantics;
9. AVT mapping/preparation skeleton;
10. seed/test fixtures representing all Phase 0 semantic cases;
11. basic read-only search/detail pages or endpoints sufficient to exercise the data model;
12. CSV/XLSX evidence-aware export;
13. automated tests;
14. GitHub Actions CI;
15. local run/test/migration documentation.

## Out of scope

Do not implement:

- automated web research/scraping;
- production curation of the seven source-pack vehicles;
- bulk vehicle catalog;
- ramp solver;
- 3D geometry viewer;
- swept-path solver;
- production ATL/ATX writer;
- authentication system;
- advanced admin portal;
- chart dashboard;
- React/SPA;
- complex visual polish.

The source pack exists as semantic/reference material for fixture design, not as authorization to create final verified production records.

## Mandatory semantic fixtures

Implement all fixtures listed in `docs/PILOT_AND_ACCEPTANCE.md`.

Additionally prove:

### F-A — orthogonal state
A value can be:
- evidence_method=PUBLISHED
- resolution_state=CONFLICTING
- verification_state=REVIEWED
- availability_state=AVAILABLE

simultaneously.

### F-B — unknown has no fake number
A NOT_FOUND/UNKNOWN assessment must not contain numeric zero as a placeholder.

### F-C — width fail closed
A raw source value called only “Overall Width” with unknown mirror semantics cannot automatically populate `overall_width_body_mm`.

### F-D — turning fail closed
A raw “Minimum turning radius 5.35 m” with no curb/wall definition may normalize the number/radius form only if rule supports it, but cannot become an AVT curb/wall radius.

### F-E — AVT track rejection
OEM centerline/tread + nominal tyre section width may produce at most an ESTIMATED/SCREENING output and must fail AVT_READY.

### F-F — rear steering
A four-wheel-steer fixture must store rear axle steering relationship without converting it into a conventional fixed-rear-axle vehicle.

### F-G — ramp namespace
A screening angle cannot be inserted under an OEM-published or geometry-derived physical parameter code.

## Database constraints

Prefer mechanical constraints/tests for invariants.

At minimum:

- stable vehicle code unique;
- parameter code unique;
- source code unique;
- derivation rule code+version unique;
- derived normalized value requires derivation lineage;
- available typed values obey parameter data type;
- non-available assessments do not pretend to be numeric values;
- no duplicate evidence links;
- parameter registry rejects forbidden ambiguous codes;
- geometry asset role required;
- normalized geometry datum/version required;
- AVT mapping stores adapter version.

Where SQL constraints would become database-specific or excessively complex, enforce via domain validators + deterministic tests.

## Readiness

Phase 0 does not need a complete production readiness engine.

Implement enough structure/rules to prove fail-closed behaviour for:

- IDENTITY_RESOLVED
- DIMENSION_READY
- AVT_READY
- RAMP_SCREENING_READY

The rule result must include explicit blockers.

## API/UI minimum

### Vehicles
- search/list page;
- vehicle detail page;
- no elaborate styling.

### Evidence
Vehicle detail must make evidence status visible.

### Data Issues
A minimal page/list showing QA/readiness blockers is sufficient.

### Compare
Can be deferred within Phase 0 if time/scope pressure occurs; do not sacrifice data-contract tests for compare UI.

## Export minimum

Provide:

### CSV
One evidence-aware flattened export with:
- vehicle identity;
- parameter code;
- normalized value/unit;
- four state dimensions;
- source IDs;
- derivation rule/version when applicable.

### XLSX
Same engineering content in a readable workbook.

No decorative report design required.

## Validation

Expected local gates should include equivalents of:

```text
python -m pytest
alembic upgrade head
alembic downgrade <appropriate prior revision>   # migration reversibility where practical
alembic upgrade head
```

Add lint/type tooling only if it remains lightweight and stable; do not turn Phase 0 into tooling work.

## Git / PR

- create a dedicated `codex/phase-0-data-foundation` branch;
- keep `main` untouched;
- open one reviewable PR;
- do not merge;
- report exact branch/head/PR and CI.

## Independent review

Required after implementation.

Review scope:
- physical schema vs logical schema;
- orthogonal state dimensions;
- turning semantics;
- AVT track fail-closed fixture;
- rear steering;
- clearance/load/static-loaded-radius;
- geometry roles;
- ramp screening namespace;
- persistence portability.

Executor self-review is not sufficient for final acceptance.

## Stop conditions

Stop and report if:

- Foundation PR #1 is not merged/accepted;
- implementation requires changing a protected semantic;
- FastAPI/SQLAlchemy stack exposes a genuine blocker;
- a fixture cannot be represented without semantic loss;
- ATL/ATX reverse engineering becomes necessary;
- work drifts into real production data curation;
- scope requires a SPA/microservice/ramp solver.

## Routing

- Model: GPT-5.6 Luna
- Effort: Max
- Chat: new Codex chat

Escalate to Terra only after demonstrating a capability-level problem rather than an unclear specification, environment issue or implementation defect.

## Definition of done

Phase 0 is done only when:

- physical schema/migrations exist;
- all mandatory semantic fixtures pass;
- parameter registry is seeded;
- basic app runs;
- evidence-aware CSV/XLSX export works;
- CI is green;
- documentation is updated;
- PR remains open for ChatGPT review;
- independent semantic review has a clear PASS / REMEDIATE / BLOCKED result.
