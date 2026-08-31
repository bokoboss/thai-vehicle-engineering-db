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
- Identity Time Basis v1 PR #6 squash merge: `112dd67deab4c4832a4645d5127ebfe7165213ed`
- Identity-time methodology: ACCEPTED
- Identity Time Basis v1 implementation PR #13 squash merge: `f2e311578694479a8bce52ecdcb46dc18fdc4c28`
- Identity-time implementation: ACCEPTED; final CI 78 tests passed
- Phase 1 30-vehicle research baseline PR #12 squash merge: `4aa268bb65b36347e077a3e4d5ddaedf24605633`
- Phase 1 research coverage: PASS WITH INGESTION CONDITIONS
- Current work: controlled pilot ingestion preparation and sentinel proof

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
- Model year is optional unless the source explicitly supports MODEL_YEAR semantics; non-MY exact identity may use an evidence-backed revision label, edition release, bounded sale period, or approved combination.
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
- `docs/PHASE_1_PILOT_COVERAGE_QA.md`
- `data/curation/phase1/ingestion_readiness_v1.json`
- `data/curation/phase1/geometry_asset_register_v1.json`
- `data/curation/phase1/batch_a_v1.json` through `batch_e_v1.json`
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

Implement and validate the bounded create-only curation ingestion path, then prove it with three sentinel vehicles before expanding Wave 1. Wave 1 has 14 research-clean candidates; Wave 2 has 11 second-review records; 5 records remain HOLD. Production ingestion must not bypass provenance/conflict/identity validation.
