# Architecture Proposal v1.0

Status: Draft for foundation review  
Date: 2026-08-29

## 1. Architectural objective

Support an engineering-grade web application whose core asset is a traceable vehicle-data model, not a UI-specific table.

## 2. Logical architecture

```text
Source discovery / research
        |
        v
Source documents + metadata
        |
        v
Raw observations
        |
        v
Normalization / identity resolution
        |
        v
Controlled derivations + QA
        |
        v
Curated engineering database
        |
        +--> Web app search/detail/compare
        +--> Excel/CSV engineering exports
        +--> AVT preparation/export layer
        +--> Data-quality dashboard
```

## 3. Persistence

### Initial implementation
Use a relational domain model. SQLite is acceptable for development, tests and an initial single-instance deployment.

### Shared deployment
The application must isolate persistence behind a repository/data-access layer so production can move to PostgreSQL or another managed relational service without changing engineering semantics.

Do not embed domain rules in database-specific SQL where avoidable.

## 4. Proposed domain entities

- manufacturers
- vehicle_models
- vehicle_configurations
- market_applicability
- source_documents
- source_observations
- parameter_definitions
- normalized_values
- derivation_rules
- derivation_runs
- evidence_links
- conflict_decisions
- readiness_results
- qa_findings
- body_outline_assets
- source_snapshot_metadata

The exact physical schema is deferred to the implementation design after review of `VEHICLE_DATA_STANDARD.md`.

## 5. Application modules

### Catalog
Search/filter and vehicle identity navigation.

### Vehicle engineering sheet
Dimensions, axle/tyre geometry, turning/steering, vertical geometry, evidence and readiness.

### Compare
Side-by-side comparison with explicit unavailable/conflicting states.

### Evidence explorer
Parameter -> normalized value -> raw observation -> source document.

### Data curation
Controlled entry/import/review. No public anonymous edits.

### QA dashboard
Missing values, conflicts, stale sources, failed validators, readiness regression.

### Engineering tools
Initially limited to deterministic derived fields and screening checks. Detailed ramp and swept-path tools should be added only after methods are validated.

### Export
Excel/CSV first. AVT preparation sheet first; ATL/ATX automation only after feasibility is proven.

## 6. API boundary

UI must consume typed domain/API contracts rather than query tables directly.

Recommended endpoint/domain shapes include:
- vehicle search
- vehicle detail
- evidence detail
- comparison
- data-quality findings
- import/curation operations
- export generation

## 7. Source-document storage

Do not store large PDF/image archives in Git.

Store in Git:
- source metadata;
- small structured observations;
- schema/migrations;
- derivation rules;
- tests;
- curated seed/pilot data where licensing permits.

Store large snapshots in a separate object/file store when retention is appropriate. Keep hashes/references in the database.

## 8. Data ingestion strategy

Do not begin with autonomous scraping.

Phase order:
1. manual/assisted curated pilot;
2. structured import helpers;
3. parsers for recurring OEM formats;
4. controlled automation with review queue;
5. periodic source monitoring only after identity/provenance QA is mature.

Automated extraction creates observations, not verified engineering values.

## 9. Security / access

Initial shared application may be read-only for ordinary users with curated write access for maintainers.

Do not expose credentials, private source archives or licensed documents through public endpoints.

## 10. Technology-selection guidance for Codex

The implementation stack should optimize for:
- reliable typed schema/model validation;
- strong automated tests;
- simple browser deployment;
- maintainable relational data access;
- deterministic Excel/CSV export;
- future PostgreSQL migration.

No specific frontend/backend framework is normative yet. The Phase 0 Codex task should propose the smallest stack meeting these constraints, with preference for established technologies and minimal infrastructure.

## 11. Deployment stages

### Stage A — local development
Local web app + SQLite.

### Stage B — internal/shared pilot
Single hosted application, authenticated if necessary, using persistent relational storage.

### Stage C — production/shared engineering service
Managed relational database, source snapshot storage, backups, audit controls and scheduled data-quality checks.

## 12. AVT integration boundary

AVT is an external engineering consumer.

The master database must preserve richer semantics than AVT requires. An AVT adapter maps only records that meet explicit AVT readiness rules.

Current official Autodesk documentation confirms user-created vehicle libraries and supports AVT library/import workflows, but direct automated production of a reliable custom library remains an implementation-stage feasibility item rather than an assumed capability.

References:
- https://help.autodesk.com/cloudhelp/2024/ENU/Autodesk-VehicleTracking-Help/files/GUID-6F7BD13F-9363-40EC-AF22-A56D2270C410.htm
- https://help.autodesk.com/cloudhelp/2022/ENU/Autodesk-VehicleTracking-Help/files/GUID-C67846CE-ACA1-4123-879D-7AD4C6BED5B9.htm
- https://help.autodesk.com/view/CIV3D/2026/ENU/?caas=caas%2Fsfdcarticles%2Fsfdcarticles%2FHow-to-import-a-DWG-model-of-a-car-in-Autodesk-Vehicle-Tracking-for-AutoCAD.html

## 13. Architecture acceptance questions

Before implementation:
1. Is raw evidence sufficiently separated from normalized data?
2. Can one vehicle parameter retain multiple conflicting observations?
3. Can persistence move away from SQLite without redefining the domain?
4. Can AVT mapping evolve independently of the source data?
5. Can the system fail closed when evidence is insufficient?
6. Can a value shown to a client be traced to its evidence chain?
