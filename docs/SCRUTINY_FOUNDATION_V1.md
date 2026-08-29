# Foundation v1 Scrutiny

Date: 2026-08-29  
Decision: **GO WITH CONDITIONS**  
Scope reviewed: product framing, data semantics, architecture direction and pilot acceptance strategy.

## Decision under review

Is the project sufficiently framed to begin a bounded Phase 0 software foundation without prematurely scaling vehicle-data collection or encoding unsupported engineering assumptions?

## What is strong enough

- The product is correctly framed as an engineering evidence system, not a generic car-spec catalog.
- Raw observations are separated from normalized and derived values.
- Exact vehicle configuration identity is protected.
- Missing/ambiguous values can remain unknown.
- Conflicting evidence is retained.
- AVT-specific fields are treated as mappings rather than OEM synonyms.
- Persistence is not irreversibly tied to SQLite.
- Bulk scraping/population is deferred until the pilot proves the schema.

## Issues found and resolved during scrutiny

### Geometry reference frame
Initial draft lacked a canonical datum/coordinate system for body and underbody geometry.

Resolution: v1 now defines a vehicle-fixed coordinate convention and requires transformation metadata for source geometries using other datums.

### Steering turns vs AVT steering time
Initial draft stored steering-wheel turns lock-to-lock but did not separately model AVT lock-to-lock time.

Resolution: v1 now stores/labels them separately and prohibits unsupported conversion from turns to seconds.

### Precision / uncertainty
Initial draft could allow image-scaled or measured values to appear numerically as precise as primary OEM dimensions.

Resolution: source observations and normalized values now carry precision/uncertainty metadata where applicable.

## Conditions carried into Phase 0

1. **Do not implement production ATL/ATX generation yet.** Implement an AVT mapping/preparation layer only. Automated library generation remains a separate feasibility gate.
2. **Do not bulk-populate hundreds of vehicles.** Phase 0 uses deterministic fixtures; pilot curation follows after schema/API foundation.
3. **Do not freeze a physical database schema that bypasses the evidence model.** The implementation must support multiple observations per parameter and auditable preferred/conflict decisions.
4. **Do not convert OEM turning labels into AVT semantics by convention.** Unknown remains unknown.
5. **Do not treat SQLite as a permanent product constraint.** Persistence access must remain portable to shared hosted storage.
6. **Schema/data-contract changes remain protected.** Any material simplification requires explicit review against the data standard.

## Residual risks

- OEM naming and Thai variant resolution will be labor-intensive for some models.
- Many manufacturers do not publish overhang, wall-to-wall turning circle, road-wheel angle or vertical profile geometry.
- Actual tyre mounted section width can differ from nominal tyre size, limiting accuracy of outer-face-track derivations.
- Detailed ramp clearance ultimately needs profile geometry, load/ride-height state and possibly physical measurement.
- AVT library file automation still requires empirical verification with the installed Autodesk environment.

## Success gates strengthened

Phase 0 must include fixtures for:
- published exact value;
- OEM-ambiguous turning value;
- derived AVT track with explicit derivation;
- conflicting source observations;
- unknown value;
- measured/estimated value with uncertainty;
- separate steering-wheel turns and AVT lock-to-lock time;
- coordinate-geometry asset metadata.

## Verdict rationale

The remaining uncertainties do not block building the data/evidence foundation. They do block claiming full AVT automation or scaling the vehicle catalog.

Proceed with a bounded Phase 0 implementation only under the conditions above.
