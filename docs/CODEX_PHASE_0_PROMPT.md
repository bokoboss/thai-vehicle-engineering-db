# Codex Prompt — Phase 0 Evidence-First Data Foundation

Repository:
https://github.com/bokoboss/thai-vehicle-engineering-db

Issue:
https://github.com/bokoboss/thai-vehicle-engineering-db/issues/2

## Model / effort / context

- Model: **GPT-5.6 Luna**
- Reasoning effort: **Max**
- Start a **new Codex chat**

## Mission

Implement GitHub Issue #2 exactly as bounded by the accepted repository contracts.

This is a small, data-heavy engineering web application. Do not expand it into a large software platform.

## Before changing anything

1. Confirm Foundation PR #1 is merged/accepted into `main`.
2. Confirm the working tree is clean.
3. Read:
   - `PROJECT_PROFILE.md`
   - `AGENTS.md`
   - `docs/VEHICLE_DATA_STANDARD.md`
   - `docs/LOGICAL_SCHEMA.md`
   - `docs/PARAMETER_REGISTRY_V1.md`
   - `data/reference/parameter_registry_v1.json`
   - `docs/ARCHITECTURE.md`
   - `docs/TECH_STACK_DECISION.md`
   - `docs/PILOT_AND_ACCEPTANCE.md`
   - `docs/PHASE_0_EXECUTION_CONTRACT.md`
   - `docs/SOURCE_CURATION_PROTOCOL.md`
   - `data/pilot/source_pack_01.json`
   - Issue #2

Treat repository documents and Issue #2 as authoritative.

If they conflict materially, stop and report the exact conflict instead of choosing silently.

## Fixed stack

Implement:
- Python
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic 2.x
- Jinja2
- HTMX only where modestly useful
- minimal project-owned CSS
- SQLite locally/tests
- PostgreSQL-compatible persistence
- pytest
- openpyxl

Do not replace this with React/Next.js, Streamlit, microservices or a separate frontend/backend architecture unless a concrete blocker makes the accepted stack impossible.

## Scope rule

Your job is to **implement and prove the data contract**, not redesign it.

Use the logical schema as the starting point for physical SQLAlchemy models and migrations.

Use the machine-readable parameter registry as the seed source.

Use `source_pack_01.json` only to understand real-world semantics and construct appropriate deterministic fixtures. Do not claim those seven records are final curated production data unless the Issue explicitly authorizes it.

## Critical protected behaviours

You must preserve all invariants in `AGENTS.md`, especially:

- raw observations separate from normalized/derived values;
- orthogonal evidence method / resolution / verification / availability states;
- conflicting evidence retained;
- no fake numeric value for unknown/not-found;
- source-reported generic width does not silently become body width;
- OEM tread/track does not silently become AVT outer-face track;
- nominal tyre width approximation alone fails AVT_READY;
- turning radius/diameter, curb/wall reference, curb axle scope and wall envelope scope stay distinct;
- actual wheel angle, virtual-centre/AVT steering angle, steering-wheel turns and lock-to-lock time stay distinct;
- clearance type/load/static-loaded-radius semantics stay distinct;
- rear/four-wheel steering is representable structurally;
- side silhouette is not a longitudinal lower interference envelope;
- screening ramp angles cannot populate OEM-published or geometry-derived physical-angle parameters;
- persistence is not hard-coupled to SQLite.

## Branch and PR

Create:
`codex/phase-0-data-foundation`

Do not modify or merge `main` directly.

Open one PR when implementation and local validation are complete.

Do not merge the PR.

## Validation

At minimum:
- all deterministic semantic fixtures/tests from Issue #2 and `PILOT_AND_ACCEPTANCE.md`;
- migration initialization/upgrade;
- migration rollback/re-upgrade where practical;
- API/page smoke tests;
- CSV export test;
- XLSX export test;
- parameter registry seed/forbidden-code tests;
- readiness fail-closed tests;
- GitHub Actions CI.

Prefer deterministic constraints/tests to instruction-only enforcement.

## UI expectation

Keep it plain and usable.

Minimum:
- vehicle list/search;
- basic vehicle detail showing data/evidence state;
- minimal data-issues/readiness blocker view.

Do not spend Phase 0 effort on visual polish.

Compare UI may be deferred if necessary to protect data-contract quality.

## Stop conditions

Stop and report rather than expanding scope if:
- PR #1 is not merged;
- the physical schema cannot represent a required fixture without changing protected semantics;
- you believe a protected contract must change;
- ATL/ATX reverse engineering becomes necessary;
- the work starts requiring a ramp solver/3D system/SPA;
- you need real bulk vehicle research to proceed.

## Final report

Return:

1. branch
2. final HEAD SHA
3. PR number/link
4. architecture/file layout implemented
5. schema/migration summary
6. required fixture/test matrix with PASS/FAIL
7. exact local validation commands and results
8. CI run/status
9. any protected contract deviation — expected to be none
10. residual limitations
11. explicit statement that production vehicle curation, scraping, ramp solver and ATL/ATX writer were not implemented

Do not claim completion based only on code existence. Completion requires the required evidence and CI.
