# Scrutiny — Phase 1 Curation Ingestion Path v1

Date: 2026-08-31  
Decision: **GO WITH CONDITIONS**  
Confidence: High

## Decision under review

What is the smallest safe way to move accepted Phase 1 research evidence into the real relational database?

## Current state

The application already has:

- typed Pydantic contracts;
- SQLAlchemy models;
- strong service-layer semantic validation;
- provenance enforcement;
- conflict handling;
- scope validation;
- readiness evaluation;
- synthetic Phase 0 seed fixtures.

It does **not** have a production curation/import workflow.

The accepted Batch A–E research JSON is intentionally review-oriented and is not safe to import directly.

## Failure modes tested

### Direct SQL inserts
**NO-GO.**

Would bypass:
- provenance validation;
- fitment/configuration scope;
- turning/clearance semantics;
- conflict rules;
- future Identity Time Basis validation.

### Reuse `app.seed`
**NO-GO for curated data.**

The current seed command intentionally creates Phase 0 synthetic fixtures and is not a production curation boundary.

### Build an admin UI
**REJECTED for Phase 1.**

Adds unnecessary UI/write complexity to a project whose main work is evidence curation.

### Import Batch A–E JSON directly
**NO-GO.**

Research packets do not always contain one-to-one source-observation-value linkage.

Direct import would force provenance guesses.

### Create-only manifest CLI through existing services
**SELECTED.**

Smallest approach that:
- preserves source attribution;
- reuses accepted validators;
- supports transaction rollback;
- stays auditable in Git;
- avoids product/UI growth.

## Key conditions

1. Manifest observations must explicitly reference source codes.
2. Normalized values must explicitly reference supporting observation codes.
3. PUBLISHED/MEASURED values cannot be imported without evidence.
4. Arbitrary DERIVED/ESTIMATED values are prohibited in manifest v1.
5. Vehicle import is CREATE_ONLY.
6. Existing source codes are reused only if metadata is compatible.
7. Import is atomic.
8. Curated DB must not automatically include Phase 0 synthetic fixtures.
9. Issue #7 Identity Time Basis implementation must merge before non-MY exact records are imported.
10. First proof is limited to three sentinel vehicles.

## Reversibility

Because vehicle imports are create-only and atomic:

- failed import rolls back;
- successful imported records are not silently re-run or overwritten.

No destructive delete/update workflow is added in Phase 1.

If a curated record later requires correction:

- handle it through an explicit reviewed update/migration workflow;
- do not weaken create-only safety merely for convenience.

## False-success protection

An importer is not accepted merely because JSON parses.

Required success evidence:

- invalid source-observation reference fails;
- naked published value fails;
- duplicate vehicle code fails;
- conflicting source-code metadata fails;
- unknown parameter code fails;
- Issue #7 identity rules enforced;
- transaction rollback verified;
- sentinel imports query back with full lineage;
- readiness remains fail-closed;
- CSV/XLSX export preserves imported provenance.

## Scope risk

The largest risk is turning a simple ingestion helper into a generic ETL platform.

Avoid:
- plugin frameworks;
- mapping DSLs;
- automatic source parsing;
- update/merge modes;
- background jobs.

The current project needs a deterministic loader, not an ingestion platform.

## Verdict

**GO WITH CONDITIONS**

Proceed with a bounded create-only manifest importer after Issue #7.

Do not ingest research packets directly.
