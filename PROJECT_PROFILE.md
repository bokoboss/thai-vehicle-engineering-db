# Project Profile

## Identity
- Project name: Thailand Vehicle Engineering Database
- Repository URL: https://github.com/bokoboss/thai-vehicle-engineering-db
- Primary branch: `main`
- Current phase: **Phase 0 — implementation ready**

## Accepted foundation
- Foundation PR: #1
- Merge method: squash
- Accepted foundation commit: `dbd0f253a3150621faf5a6aaa693638ffc179da7`
- Accepted date: 2026-08-30
- Research gate: `GO WITH CONDITIONS — High confidence`
- Research conditions: incorporated before merge
- Current execution issue: #2

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

Do not expand the application into a large software platform unless a later real use case justifies it.

The main project effort is expected to be:
- source research;
- exact vehicle/configuration resolution;
- parameter semantics;
- provenance;
- QA;
- curation.

## Frozen Phase 0 technology stack
- Python
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic 2.x
- Jinja2
- limited HTMX where useful
- minimal project-owned CSS
- SQLite for local/test/single-instance pilot
- PostgreSQL-compatible persistence for later shared deployment
- pytest
- openpyxl for XLSX export

Do not reopen framework selection without a concrete blocker.

## Architecture / invariants
- Raw source observations and normalized engineering values are separate.
- Every publishable engineering parameter has parameter-level provenance.
- Vehicle identity distinguishes market, generation/chassis, model-year applicability and material variant/fitment differences.
- Unknown values remain unknown; missing data is never filled merely for completeness.
- Evidence method, conflict/resolution, verification and availability are orthogonal.
- Derived, measured, estimated and published values remain distinguishable.
- Source authority, applicability and evidence method are independent metadata dimensions.
- Unit normalization never destroys original wording/value/unit.
- Source-reported generic width does not silently become body or mirror width.
- OEM tread/track does not silently become AVT outer-face tyre track.
- Turning radius/diameter, curb/wall reference, curb axle scope and wall envelope scope remain explicit.
- Actual road-wheel angles, virtual-center/AVT steering angle, steering-wheel turns and AVT lock-to-lock time remain distinct.
- Clearance type, load condition and static-loaded tyre radius remain explicit.
- Rear/four-wheel steering is represented structurally when applicable.
- Side silhouette and longitudinal lower interference envelope are distinct geometry roles.
- OEM-published, geometry-derived physical and screening ramp angles use distinct parameter namespaces.
- Autodesk Vehicle Tracking fields are adapter outputs, not the master record.
- Conflicting evidence is retained rather than silently overwritten.
- Persistence must remain practical to migrate from SQLite to PostgreSQL.

## Protected behavior
Changes require explicit review if they alter:
- vehicle identity semantics;
- parameter definitions;
- geometry definitions/datum;
- source/evidence state model;
- derivation validity rules;
- conflict-resolution rules;
- QA/readiness criteria;
- AVT mappings;
- ramp/vertical-clearance methodology;
- numerical engineering formulas used for published/derived results.

## Important paths

### Normative/control
- `AGENTS.md`
- `docs/VEHICLE_DATA_STANDARD.md`
- `docs/LOGICAL_SCHEMA.md`
- `docs/PARAMETER_REGISTRY_V1.md`
- `docs/AVT_MAPPING_SPEC.md`
- `docs/RAMP_VERTICAL_CLEARANCE_METHOD.md`
- `docs/TECH_STACK_DECISION.md`
- `docs/PHASE_0_EXECUTION_CONTRACT.md`

### Product/research
- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/UI_MVP_SPEC.md`
- `docs/SOURCE_CURATION_PROTOCOL.md`
- `docs/SOURCE_LANDSCAPE.md`
- `docs/PILOT_AND_ACCEPTANCE.md`
- `docs/RESEARCH_GATE_FOUNDATION_2026-08-30.md`
- `docs/SCRUTINY_FOUNDATION_V1.md`

### Machine-readable/reference
- `data/reference/parameter_registry_v1.json`
- `data/pilot/pilot_targets_v1.json`
- `data/pilot/source_pack_01.json`

### Codex
- GitHub Issue #2
- `docs/CODEX_PHASE_0_PROMPT.md`

## Validation matrix
| Gate | Method | Required |
|---|---|---|
| Schema / contract | schema tests + migrations | Yes |
| Data provenance | deterministic evidence validation | Yes |
| Orthogonal state model | contract fixtures | Yes |
| Derived engineering values | lineage + reference tests | Yes |
| AVT fail-closed mapping | deterministic semantic fixtures | Yes |
| Ramp namespace/data readiness | contract fixtures | Yes |
| Browser/UI | smoke/E2E as needed | When UI exists |
| CSV/XLSX export | deterministic export tests | Yes |
| Real vehicle data | primary/strongest-source cross-check | Pilot onward |
| CI | GitHub Actions | Phase 0 onward |
| Independent semantic review | fresh-context review | Phase 0 acceptance |

## Execution characteristics
- Data acquisition/identity resolution ambiguity: high.
- Bounded software implementation ambiguity after foundation: low to moderate.
- High-risk areas: source interpretation, vehicle identity, turning semantics, AVT track/steering mapping, clearance/load state, rear steering, lower-envelope geometry.
- Safe to parallelize later: independent vehicle research batches after pilot rules are proven.
- Tightly controlled: schema, parameter definitions, derivation rules, evidence state model, AVT/ramp semantics.

## Git / release policy
- Use branches + PRs for material schema, methodology, architecture and application changes.
- Review actual diffs and evidence before merge.
- Prefer squash merge unless a phase specifically benefits from preserved commit history.
- Data releases carry schema/registry versions and source retrieval dates.
- Do not commit large raw OEM document archives blindly to Git.

## Development workflow
Lean adoption of:
https://github.com/bokoboss/engineering-development-workflow

Operating model:
- ChatGPT: research / data methodology / architecture / execution contracts / GitHub review
- GitHub: authoritative project state
- Codex: bounded implementation requiring local code/runtime/browser work

## Current known limitations / risks
- No production application implementation exists yet.
- The seven-record source pack is curation/reference input, not a final production dataset.
- Public OEM material is often weak for true AVT outer-face track, actual wheel lock, wall-to-wall radius, overhang and lower-underbody geometry.
- Detailed ramp clearance will require stronger lower-envelope/load/tyre evidence than ordinary retail specifications provide.
- Production ATL/ATX automation remains unproven and is outside Phase 0.
- Automated scraping is outside Phase 0.

## Current next objective

Execute GitHub Issue #2 / `docs/PHASE_0_EXECUTION_CONTRACT.md` with Codex GPT-5.6 Luna Max on a dedicated branch, then perform independent semantic and ChatGPT PR review before merge.
