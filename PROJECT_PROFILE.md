# Project Profile

## Identity
- Project name: Thailand Vehicle Engineering Database
- Repository URL: https://github.com/bokoboss/thai-vehicle-engineering-db
- Primary branch: `main`
- Current phase: **Phase 1 — Pilot Data Curation**

## Accepted baselines
- Foundation PR #1 squash merge: `dbd0f253a3150621faf5a6aaa693638ffc179da7`
- Phase 0 implementation PR #3 squash merge: `fbdc5bcd60b1e560a3151d33b907e5e812a8909a`
- Phase 0 final CI: run `33379240873`, 65/65 tests passed
- Phase 0 acceptance: PASS after R1–R5 and S1–S3 remediation
- Current work: Phase 1 pilot data curation

## Product purpose
Create an engineering-grade, traceable database and intentionally small web application for vehicle geometry and maneuverability relevant to vehicles used in Thailand.

Primary uses:
- Autodesk Vehicle Tracking preparation and swept-path work
- parking/access/porte-cochère design
- ramp and vertical-clearance assessment
- vehicle comparison
- future Thai design-vehicle development
- traceable client-facing engineering answers

## Product scope principle

This is a **data project with a thin web interface**.

The software foundation is implemented. The main project effort now moves to:
- source research;
- exact vehicle/configuration resolution;
- parameter semantics;
- provenance;
- QA;
- curation.

## Implemented Phase 0 stack
- Python
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic 2.x
- Jinja2
- limited HTMX
- minimal project-owned CSS
- SQLite local/test
- PostgreSQL-compatible relational design
- pytest
- openpyxl

## Phase 0 accepted capabilities
- 21-table evidence-first relational schema
- frozen explicit Alembic revision
- 48-parameter registry
- orthogonal evidence/resolution/verification/availability states
- provenance enforcement
- auditable conflict selection
- exact-configuration/fitment scope validation
- structured load/clearance/steering/geometry semantics
- fail-closed AVT mapping/readiness
- fail-closed physical ramp-angle namespace
- search/detail/compare/issues web UI
- CSV/XLSX evidence-aware exports
- deterministic semantic fixtures and CI

## Core invariants
- Raw source observations and normalized values are separate.
- Every publishable engineering parameter has parameter-level provenance.
- Exact vehicle identity matters.
- Unknown values remain unknown.
- Conflicts are retained and resolved audibly.
- OEM tread/track is not AVT outer-face track by default.
- Turning and steering semantics remain explicit.
- Static-loaded tyre radius requires structured load applicability.
- Cross-configuration evidence/fitment/axle/load relationships fail closed.
- Geometry-derived physical ramp angles remain unavailable until a dedicated approved method exists.
- Persistence remains portable beyond SQLite.

## Important paths

### Normative/control
- `AGENTS.md`
- `docs/VEHICLE_DATA_STANDARD.md`
- `docs/LOGICAL_SCHEMA.md`
- `docs/PARAMETER_REGISTRY_V1.md`
- `docs/AVT_MAPPING_SPEC.md`
- `docs/RAMP_VERTICAL_CLEARANCE_METHOD.md`

### Curation
- `docs/SOURCE_CURATION_PROTOCOL.md`
- `docs/SOURCE_LANDSCAPE.md`
- `docs/PILOT_AND_ACCEPTANCE.md`
- `data/pilot/pilot_targets_v1.json`
- `data/pilot/source_pack_01.json`

### Software
- `docs/PHASE_0_IMPLEMENTATION.md`
- `app/`
- `alembic/`
- `tests/`

## Current known limitations
- Pilot source pack is reference input, not final curated production data.
- Public OEM sources are often weak for actual wheel lock, AVT outer-face track, wall-to-wall radius and lower-underbody geometry.
- Physical geometry-derived ramp angles are intentionally blocked.
- Production ATL/ATX automation remains unproven.
- Automated scraping remains deferred.

## Current next objective

Run Phase 1 as ChatGPT-led pilot curation of approximately 30 exact Thai-market configurations. Use Codex only for bounded code/schema/tooling changes discovered through evidence.
