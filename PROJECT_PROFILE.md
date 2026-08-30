# Project Profile

## Identity
- Project name: Thailand Vehicle Engineering Database
- Repository URL: https://github.com/bokoboss/thai-vehicle-engineering-db
- Primary branch: `main`
- Current phase: Foundation / pre-implementation

## Current accepted baseline
- Accepted branch: `main`
- Accepted HEAD SHA at project initialization: `79841b58c15a0d6fba587aa8d80e69e1cdb0df8f`
- Accepted date: 2026-08-29
- Current milestone: Vehicle Data Standard + product/architecture foundation

## Product purpose
Create an engineering-grade, traceable database and web application for vehicle geometry and maneuverability relevant to vehicles used in Thailand, with outputs suitable for swept-path analysis, ramp/access design, vehicle comparison, design-vehicle selection and Autodesk Vehicle Tracking preparation.

## Technology stack
Not frozen yet. Foundation preference:
- Web application: browser-based, shareable
- Master data model: relational
- Development / single-instance persistence: SQLite is acceptable
- Shared production persistence: must be deployable without coupling the domain model to SQLite
- Code stack: to be selected during Phase 0 implementation after schema review

## Architecture / invariants
- Raw source observations and normalized engineering values are separate.
- Every publishable engineering parameter has parameter-level provenance.
- Vehicle identity must distinguish market, generation/chassis, model-year applicability and variant/configuration where geometry differs.
- Unknown values remain unknown; missing data is never filled merely for completeness.
- Derived, measured, estimated and published values remain distinguishable.
- Source authority, applicability and evidence method are independent metadata dimensions.
- Unit normalization never destroys the original reported wording/value/unit.
- Autodesk Vehicle Tracking normalized fields are mappings from the engineering database, not the master record itself.
- The system must support conflicting sources without silently overwriting evidence.

## Protected behavior
Changes require explicit review if they alter:
- vehicle identity semantics;
- geometry definitions;
- source/evidence grading;
- derivation validity rules;
- conflict-resolution rules;
- QA/readiness criteria;
- Autodesk Vehicle Tracking parameter mappings;
- numerical engineering formulas used for published/derived results.

## Important paths
- Product / methodology documentation: `docs/`
- Schema/migrations: to be created under `database/`
- Source metadata: to be created under `data/sources/` or equivalent
- Tests: to be created under `tests/`
- Large/raw source documents: storage strategy to be decided; do not commit large archives blindly to Git

## Validation matrix
| Gate | Method | Required |
|---|---|---|
| Schema / contract | schema tests + migrations | Yes |
| Data provenance | deterministic evidence validation | Yes |
| Derived engineering values | reference cases / independent recomputation | Yes |
| AVT mapping | reference vehicle fixtures + manual AVT verification where needed | Yes |
| Browser/UI | E2E + human review | When UI changes |
| Real vehicle data | primary-source cross-check | Yes for pilot/release |
| CI | GitHub Actions | After implementation starts |

## Execution characteristics
- Typical ambiguity: high in data acquisition/identity resolution; moderate in bounded software implementation after specifications are frozen
- High-risk areas: source interpretation, vehicle identity, turning-circle definitions, steering geometry, vertical-clearance geometry, AVT mapping
- Safe to parallelize later: independent vehicle research batches after the data standard is frozen
- Tightly coupled / single-owner: schema, definitions, derivation rules, grading, acceptance semantics

## Git / release policy
- Use branches + PRs for material schema, methodology, architecture and application changes.
- Review actual diffs and evidence before merge.
- Prefer squash merge unless a phase specifically benefits from preserved commit history.
- Data releases should carry a data-schema version and source retrieval date.

## Development workflow
Lean adoption of https://github.com/bokoboss/engineering-development-workflow, current observed baseline v1.5.0 on 2026-08-29.
- ChatGPT: control plane / research / specification / review
- GitHub: authoritative project state
- Codex: bounded execution plane when local code/runtime/browser work is required

## Current known limitations / risks
- No implementation exists yet.
- No pilot vehicle records exist yet.
- Availability and definitions of OEM turning/steering/overhang/ramp data vary substantially.
- Public OEM pages may disappear or change; source snapshot strategy is required.
- Exact AVT library automation/export feasibility still requires implementation-stage verification.

## Current next objective
Review and accept Product Requirements v1, Vehicle Data Standard v1, architecture proposal and pilot acceptance criteria before Codex implementation begins.
