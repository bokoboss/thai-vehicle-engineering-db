# Project Profile

## Identity
- Project name: Thailand Vehicle Engineering Database
- Repository: `bokoboss/thai-vehicle-engineering-db`
- Repository URL: https://github.com/bokoboss/thai-vehicle-engineering-db
- Primary branch: `main`
- Local repository path used by the current Windows workflow: `D:\R&D\thai-vehicle-engineering-db`
- Project character: engineering-data project with an intentionally thin web application

## Current accepted state — 2026-09-04

Repository/Git/GitHub/release artifacts are authoritative for current state. Do not rely on previous ChatGPT/Codex account history.

- Accepted `main` SHA: `357474a7193f0a6d9b50aa7148c6dd5012548a28`
- Accepted release: `release_2026_09_d`
- Accepted catalog: **41 vehicle configurations**
- `data/curation/releases/current_release.json` points to `release_2026_09_d.json`
- Release D stable-code digest: `923c5607f4789a44368172cfe88c9fe1c6190ab2e895e61476430c1546258306`
- PR #59 / Issue #56 — UI Polish Pass 2: merged/completed
- PR #57 — Wave 2C tranche 2: **OPEN / NOT MERGED**
- PR #57 branch: `chatgpt/wave2c-tranche2-data-expansion`
- PR #57 HEAD at this state snapshot: `01754019fbd771e5da5e406515832580b1f8475b`
- Issue #58 — Wave 2C T2 importer qualification gate: OPEN; previously stopped correctly before import on Maybach manufacturer-display conflict
- Issue #60 — Mercedes-Maybach marque identity remediation: OPEN
- Issue #61 — control-plane state sync for account-independent continuity: current prerequisite work
- Defender 130 X-Dynamic HSE MY27 remains HOLD and is excluded from Wave 2C tranche 2

Do not derive the current vehicle count from older milestones below. Current GitHub/release evidence controls.

## Current execution sequence

The active sequence is:

1. complete and independently review Issue #61 control-plane state synchronization;
2. execute Issue #60 bounded Mercedes-Maybach marque remediation;
3. independently review Issue #60;
4. rerun Issue #58 from a fresh accepted Release D disposable 41-configuration baseline;
5. only after successful 41 -> 44 qualification, decide separately whether PR #57 is acceptable for merge.

Do **not** automatically create or promote a 44-vehicle release after qualification. Release promotion is a separate controlled decision.

## Current Wave 2C tranche 2

PR #57 proposes three research-clean CREATE_ONLY manifests:

1. Toyota Alphard HEV Premium Luxury — bounded Thailand SALE_PERIOD snapshot 2026-09-03;
2. Porsche Taycan Turbo GT MY2027 — exact Thailand MY2027 identity with exact-model global structural evidence retained as `SAME_GEOMETRY_CONFIRMED`;
3. Mercedes-Maybach S 580 e Premium — bounded Thailand SALE_PERIOD snapshot 2026-09-03.

The first Issue #58 qualification attempt established:

- accepted Release D disposable baseline = 41 configurations;
- Alphard validation = PASS;
- Taycan validation = PASS;
- Maybach validation = FAIL before import;
- no candidate data was imported;
- staging remained 41 configurations;
- no 44-record application/API/export smoke or original-41 post-import fingerprint comparison was claimed.

The recorded blocker was an existing-manufacturer display-metadata conflict caused by the pre-remediation Maybach identity mapping.

## Mercedes-Maybach identity decision

The reviewed target identity for Issue #60 is:

- `manufacturer_name = Mercedes-Maybach`
- `manufacturer_display_name = Mercedes-Maybach`
- `canonical_model_name = s-class`
- `display_model_name = S-Class`
- variant remains `S 580 e Premium`

This repository's manufacturer dimension is operationally used as commercial marque/brand identity. Therefore:

`Mercedes-Maybach · S-Class · S 580 e Premium`

must remain distinct from the accepted:

`Mercedes-Benz · S-Class · S 350 d Exclusive`.

Do not collapse Mercedes-Maybach into Mercedes-Benz merely because they belong to the same corporate group. A successful later 44-vehicle staging import is expected to have **22 manufacturers**, subject to actual importer/database counts.

Issue #60 is a bounded identity-metadata remediation only. It must not change engineering values, raw evidence, applicability grades, conflict semantics, importer/schema/application logic, Defender HOLD status, or release membership.

## Product purpose
Create an engineering-grade, traceable database and intentionally small web application for vehicle geometry and maneuverability relevant to vehicles used in Thailand.

Primary uses:
- Autodesk Vehicle Tracking preparation and swept-path work
- parking/access/porte-cochère design
- turning and maneuverability assessment
- ramp and vertical-clearance assessment
- vehicle comparison
- future Thai design-vehicle development
- traceable client-facing engineering answers

The project must not become a generic automotive specification website.

## Product scope principle

This is a **data project with a thin web interface**.

The software foundation is implemented. The principal work is:
- source research;
- exact vehicle/configuration resolution;
- parameter semantics;
- provenance;
- conflict/readiness handling;
- QA;
- controlled curation and release qualification.

Vehicle growth is release-data driven. Do not hard-code vehicle names or vehicle counts into application logic.

## Accepted technology foundation
- Python
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic 2.x
- Jinja2
- limited HTMX
- SQLite local/test
- PostgreSQL-compatible relational design
- pytest
- openpyxl

## Accepted capabilities
- 21-table evidence-first relational schema
- 48-parameter engineering registry
- frozen/versioned migration foundation
- orthogonal evidence/resolution/verification/availability states
- parameter-level provenance enforcement
- auditable conflict retention/selection
- exact configuration, fitment, load and temporal-scope validation
- structured clearance/steering/geometry semantics
- fail-closed AVT mapping/readiness
- fail-closed physical geometry-derived ramp namespace
- search, vehicle detail, Compare and Issues UI
- evidence-aware CSV/XLSX exports
- Engineering Design Check v1 with deterministic PASS / FAIL / INDETERMINATE fail-closed semantics
- generic release/build/promotion pipeline driven by explicit immutable release membership
- Windows local launcher/updater workflow for the curated application
- responsive UI polish and screenshot-driven QA through PR #59

## Core invariants
- Raw source observations and normalized values are separate.
- Raw evidence is immutable.
- Every publishable engineering parameter requires parameter-level provenance.
- Exact vehicle/configuration identity matters.
- Commercial model name alone is never sufficient identity.
- Model year is used only when evidence supports model-year semantics; other evidence-backed temporal bases remain valid.
- Unknown values remain unknown.
- Unsupported precision is not acceptable.
- Conflicting authoritative evidence is retained and surfaced; do not silently choose one value.
- OEM tread/track is not AVT outer-face track by default.
- Turning radius/diameter and reference-envelope semantics remain explicit.
- Do not silently convert turning diameter/circle to engineering radius unless an approved semantic rule allows it.
- Clearance data retains load/ride-height applicability where known; ride-height state is not vehicle load state.
- Derived values require an approved versioned method, input provenance, validity domain and tests.
- Readiness is use-case specific.
- Geometry-derived physical ramp angles remain unavailable until the approved required geometry exists.
- Persistence remains portable beyond SQLite.

## Release pipeline status

The generic builder is the accepted production build path. Release membership is controlled only by immutable versioned release definitions selected through `data/curation/releases/current_release.json`.

Current accepted release:

- `data/curation/releases/release_2026_09_d.json`
- status: `ACCEPTED`
- membership: 41 explicit manifests
- current pointer: `data/curation/releases/current_release.json`

The builder must remain catalog-generic. Adding accepted vehicles does not by itself justify application, Compare, Design Check, API, export, launcher or builder source changes.

The accepted database is not an incremental import target. Qualification uses disposable staging databases and promotion occurs only through the controlled release pipeline.

## Important paths

### Normative/control
- `AGENTS.md`
- `PROJECT_PROFILE.md`
- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/VEHICLE_DATA_STANDARD.md`
- `docs/LOGICAL_SCHEMA.md`
- `docs/PARAMETER_REGISTRY_V1.md`
- `docs/AVT_MAPPING_SPEC.md`
- `docs/RAMP_VERTICAL_CLEARANCE_METHOD.md`
- `docs/SOURCE_CURATION_PROTOCOL.md`
- `docs/SOURCE_LANDSCAPE.md`

### Current release / qualification
- `data/curation/releases/current_release.json`
- `data/curation/releases/release_2026_09_d.json`
- `scripts/build_curated_db.py`
- `docs/RELEASE_PIPELINE_V1.md`
- `docs/WAVE_2C_RESEARCH_QA.md`
- `docs/WAVE_2C_T2_IMPORT_QUALIFICATION.md` on PR #57
- `data/curation/phase2/wave2c_target_registry_v1.json` on PR #57
- `data/curation/manifests/wave2c/` for current Wave 2C manifests

### Software
- `app/`
- `alembic/`
- `tests/`
- Windows launcher/updater files at repository root

## Current known limitations
- Public OEM sources are often insufficient for actual road-wheel lock, AVT outer-face track, wall-to-wall radius and lower-underbody geometry.
- OEM turning labels may remain semantically ambiguous even when numeric values are published.
- Physical geometry-derived ramp angles are intentionally blocked without the required contact/lower-envelope/static-loaded-tyre geometry.
- Detailed vertical-clearance assessment may require lower-underbody geometry not available publicly.
- Production ATL/ATX automation remains unproven.
- Automated scraping remains deferred.
- Current Wave 2C tranche 2 is not importer-qualified until #60 is remediated/reviewed and #58 completes a clean full rerun.

## Historical accepted milestones

The milestones below are historical context, not current-state selectors:

- Foundation PR #1 squash merge: `dbd0f253a3150621faf5a6aaa693638ffc179da7`
- Phase 0 implementation PR #3 squash merge: `fbdc5bcd60b1e560a3151d33b907e5e812a8909a`
- Phase 0 acceptance: PASS after R1–R5 and S1–S3 remediation
- Identity Time Basis v1 PR #6 squash merge: `112dd67deab4c4832a4645d5127ebfe7165213ed`
- Identity-time implementation PR #13 squash merge: `f2e311578694479a8bce52ecdcb46dc18fdc4c28`
- Phase 1 30-vehicle research baseline PR #12 squash merge: `4aa268bb65b36347e077a3e4d5ddaedf24605633`
- Curation Ingestion Contract v1 PR #14 squash merge: `15bd1256e35c69b81fb6d43171dfaca0a32dbc6a`
- Wave 2 second-review PR #16 squash merge: `5466e16350c4c9c982be581f14ff5a46e3b3d3b9`
- Wave 2 closure PR #17 squash merge: `62a502f196e98077327519a38fa9da3c3867d942`
- Engineering Design Check v1: commit `1261238f4bb017f767ab27d0f3d3cf1dfbf6df91`
- Windows local launcher: commit `5990666ab122d0da3cb89da48b8f92a6659f8b7e`
- Release D 41-vehicle publication: commit `85546ce2b1ab2288e7a894230a887899e2966070`
- UI Polish Pass 1: commit `6776f703e9b181cfda4745503b0d236f642a1929`
- UI Polish Pass 2 / current accepted main: `357474a7193f0a6d9b50aa7148c6dd5012548a28`

## Current next objective

Complete the control-plane synchronization in Issue #61 so future ChatGPT/Codex work can reconstruct authoritative state without prior-account chat history. Then execute and independently review Issue #60 exactly as bounded, followed by a fresh full Issue #58 importer qualification against the accepted 41-configuration Release D baseline.

Do not bypass the create-only importer, weaken evidence/identity semantics, add Defender to tranche 2, update `current_release.json`, or promote a 44-vehicle release as part of these steps.
