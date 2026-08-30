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

**Foundation candidate complete; Phase 0 implementation not yet started.**

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
