# Architecture Proposal v1.0

Status: Foundation candidate after Deep Research amendment  
Date: 2026-08-30

## 1. Architectural objective

Build a deliberately small web application around a rigorous engineering evidence model.

The product is a **data project with a thin web interface**, not a large software platform.

## 2. Logical architecture

```text
Research / source discovery
        |
        v
Source documents + source metadata
        |
        v
Raw observations
        |
        +--> parameter assessments (unknown / not found)
        |
        v
Identity resolution + semantic normalization
        |
        v
Controlled derivations + conflict decisions + QA
        |
        v
Curated engineering domain
        |
        +--> simple web search/detail/compare
        +--> CSV/Excel engineering exports
        +--> AVT preparation adapter
        +--> data-quality/issues view
```

## 3. Product-scope rule

Keep the MVP thin.

Required application surfaces:
- search/filter;
- vehicle detail;
- compare;
- source/evidence drill-down;
- data issue/readiness view;
- CSV/Excel export.

Do not add dashboards, 3D viewers, AI chat, complex user administration, advanced charting or simulation engines unless a later use case justifies them.

## 4. Persistence

SQLite is acceptable for Phase 0/local development.

The domain must remain portable to PostgreSQL or another conventional relational service for shared deployment. Persistence-specific details must not define engineering semantics.

Use a repository/data-access boundary rather than allowing UI code to query physical tables directly.

## 5. Core domain entities

The physical schema may refine names, but must support:
- manufacturers;
- vehicle models;
- exact vehicle configurations;
- equipment/wheel fitments;
- market applicability;
- source documents;
- source observations;
- parameter definitions;
- parameter assessments;
- normalized values;
- evidence links;
- orthogonal evidence/resolution/verification/availability states;
- derivation rules/runs;
- conflict/preferred-value decisions;
- structured load conditions;
- axle/steering relationships;
- readiness results;
- QA findings;
- geometry assets with role/datum/fidelity/uncertainty;
- source snapshot metadata;
- AVT mapping/adapter results.

The implementation must support multiple observations per parameter and must not collapse this into one naked vehicle-spec table.

## 6. Geometry architecture

Store geometry independently from scalar specifications.

Geometry roles include:
- plan body envelope;
- AVT plan profile;
- side silhouette;
- longitudinal lower envelope;
- underbody low points;
- tyre circles;
- axle/datum geometry.

A visual side silhouette and an engineering interference envelope are different roles even when they originate from the same drawing.

All normalized geometry uses the project vehicle-fixed datum defined in `VEHICLE_DATA_STANDARD.md`.

## 7. Load/state architecture

Clearance, static-loaded tyre radius and ramp-relevant geometry can depend on:
- mass/load basis;
- occupants/payload;
- tyre pressure;
- suspension mode;
- ride height.

Represent those conditions as reusable structured records rather than free text embedded in numeric values.

## 8. Steering architecture

Represent:
- primary steering;
- actual wheel angles;
- virtual-center/AVT steering quantities;
- steering transition time;
- secondary/rear steering linkage.

Do not design the domain around conventional front-steer-only vehicles. The pilot deliberately includes rear/four-wheel-steering cases.

## 9. AVT integration boundary

AVT is an external consumer, not the master schema.

Supported foundation levels:
- Level 0 — evidence-backed engineering data sheet;
- Level 1 — AVT input preparation sheet;
- Level 2 — assisted/manual Vehicle Wizard/library workflow.

Deferred research/experiment:
- Level 3 — automated ATL/ATX or equivalent exchange;
- Level 4 — automated company-library management.

No public official serialization/API contract sufficient for a production external ATL/ATX writer has been established by the current research. Do not make it a Phase 0 dependency.

AVT adapter results should carry adapter/mapping-rule version; target AVT product version may be added when needed.

## 10. Ramp-analysis boundary

No ramp solver is part of Phase 0.

The architecture must only be able to store future required inputs:
- axle positions;
- static-loaded tyre radii;
- structured load condition;
- longitudinal lower envelope;
- geometry fidelity/uncertainty;
- road/ramp profile in a later analysis module.

A future 2D quasi-static longitudinal collision method can be built as a separate engineering module without redefining the vehicle evidence model.

## 11. Source-document storage

Do not commit large PDF/image archives to Git by default.

Git stores metadata, schema/migrations, small curated structured records where licensing permits, derivation rules, tests and decision/audit records.

Large snapshots belong in separate object/file storage when retention is appropriate, with hashes/references in the database.

## 12. Data ingestion strategy

Do not begin with autonomous scraping.

Sequence:
1. curated pilot;
2. structured import helpers;
3. parsers for recurring OEM formats;
4. controlled automation producing reviewable raw observations;
5. periodic source monitoring only after QA/identity workflows mature.

Automated extraction creates observations, not verified engineering facts.

## 13. API/UI boundary

UI consumes typed domain/API contracts.

Minimum read operations:
- search vehicles;
- vehicle engineering detail;
- evidence/source detail;
- compare vehicles;
- readiness/data-quality findings;
- export.

Curation/write operations may initially be maintainer-only and minimal.

## 14. Security/access

Shared application may be read-only for ordinary users.

Do not expose credentials, private source archives or licensed documents through public endpoints.

## 15. Technology-selection guidance

Choose the smallest established stack supporting:
- typed domain validation;
- relational migrations;
- deterministic tests;
- simple browser deployment;
- SQLite locally with practical PostgreSQL migration;
- CSV/Excel export.

Avoid microservices and infrastructure complexity.

## 16. Deployment stages

### Stage A — local development
Web app + SQLite.

### Stage B — shared pilot
Single hosted app + persistent relational database.

### Stage C — mature internal engineering service
Managed relational storage, backups, source-snapshot storage and scheduled QA.

## 17. Architecture acceptance questions

Before implementation acceptance:

1. Can multiple observations/conflicts coexist for one parameter?
2. Are method/conflict/review/availability states independent?
3. Can OEM track/tread remain separate from AVT outer-face track?
4. Can clearance/load semantics be represented without free-text ambiguity?
5. Can rear steering be represented without pretending it is a fixed rear axle?
6. Can side silhouette and lower interference envelope coexist?
7. Can persistence move from SQLite without redefining the domain?
8. Can the system fail closed when evidence is insufficient?
9. Can every client-visible value be traced to evidence/derivation?
10. Is the MVP still simple enough that data acquisition remains the dominant project effort?
