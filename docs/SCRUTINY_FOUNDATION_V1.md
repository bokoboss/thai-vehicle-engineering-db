# Foundation v1 Scrutiny

Date: 2026-08-29, updated 2026-08-30  
Decision: **GO WITH CONDITIONS -> CONDITIONS INCORPORATED INTO FOUNDATION CANDIDATE**  
Scope reviewed: product framing, data semantics, architecture direction and pilot acceptance strategy.

## Decision under review

Is the project sufficiently framed to begin a bounded Phase 0 software foundation without prematurely scaling vehicle-data collection or encoding unsupported engineering assumptions?

## Initial scrutiny findings

The original foundation was directionally correct, but required protection around:

- geometry datum/reference frame;
- steering-wheel lock-to-lock turns vs AVT lock-to-lock time;
- precision/uncertainty;
- ATL/ATX automation;
- bulk data scale-up;
- turning semantics;
- persistence portability;
- provenance/conflict integrity.

These conditions were carried into the initial draft.

## Deep Research follow-up — 2026-08-30

A dedicated Foundation Research Gate returned:

**GO WITH CONDITIONS — High confidence.**

The product concept, evidence-first architecture, source hierarchy and bounded Phase 0 direction were confirmed. The research did **not** justify REPLAN or NO-GO.

It did identify nine foundation-level semantic corrections required before schema implementation.

## Research conditions now incorporated

### 1. Orthogonal evidence/value state
Evidence method, conflict/resolution, verification and availability are no longer represented by one mutually exclusive status enum.

The data model must support states such as:

> PUBLISHED + CONFLICTING + REVIEWED + AVAILABLE

without information loss.

### 2. Exact AVT turning semantics
Turning data now preserves:

- radius vs diameter;
- curb vs wall vs other/unknown envelope;
- curb axle scope;
- wall body-only vs body+loads envelope scope.

Unknown scope fails closed for AVT readiness.

### 3. Steering-angle semantics
Actual inner/outer road-wheel angles remain distinct from a virtual-center steering angle and the AVT Maximum Steering Angle adapter output.

Steering-wheel turns remain separate.

### 4. Stricter AVT outer-face track rule
OEM tread/track remains semantically separate from AVT outer-face tyre track.

A centerline/tread value plus nominal tyre section width may only create an estimated/screening result and cannot alone pass AVT_READY.

### 5. Structured clearance semantics
Clearance now has controlled type semantics such as between-axles, running, axle, battery/component-specific or OEM-unspecified minimum.

### 6. Load condition + static-loaded tyre radius
Physical ramp/contact geometry can require structured load state, tyre pressure/ride-height applicability and static-loaded tyre radius.

### 7. Lower-envelope and screening-angle semantics
Side silhouette is distinct from longitudinal lower interference geometry.

OEM-published, geometry-derived physical and engineering-screening ramp angles use distinct parameter codes.

### 8. Rear/secondary steering
Rear steering is represented by axle, linkage/relationship, phase/mode/speed behaviour and evidence—not a simple boolean.

### 9. Width/mirror semantics
A source-reported generic width remains semantically unspecified until body/mirror inclusion is established.

## Conditions that still remain after foundation merge

These are not blockers to Phase 0, but remain explicit project boundaries:

1. Do not implement production ATL/ATX generation; only AVT preparation/mapping.
2. Do not bulk-populate hundreds of vehicles during Phase 0.
3. Do not bypass raw observation/provenance/conflict semantics in the physical schema.
4. Do not infer AVT or ramp semantics by convention.
5. Do not hard-couple the product to SQLite.
6. Material data-contract simplification requires explicit review.
7. Detailed ramp solver remains deferred.
8. Automated source ingestion must create reviewable observations, not self-certified engineering facts.

## Phase 0 evidence requirement

The first schema/migrations must prove, using deterministic fixtures, that:

- published and conflicting states coexist;
- unknown turning scope fails closed;
- actual wheel angle, virtual-center angle, steering-wheel turns and lock-to-lock time remain distinct;
- nominal-width AVT-track approximation fails AVT_READY;
- clearance/load/static-loaded-radius semantics remain distinct;
- rear steering is representable;
- side silhouette and lower interference envelope are separate;
- screening ramp values cannot populate physical/OEM angle codes.

A fresh-context independent semantic review is required after the first implementation.

## Residual risks

- OEM naming and Thai exact-variant resolution will remain labor intensive for some models.
- Public retail specifications are often adequate for basic dimensions but weak for true AVT steering geometry, wall-to-wall radius, overhang and underbody profiles.
- Mounted tyre outer-face position may require engineering drawings or measurement.
- Detailed ramp clearance may require lower-envelope geometry and physical measurement.
- AVT automated library-file generation remains an installed-environment experiment/research gate.

## Final scrutiny verdict for PR #1

The amended foundation candidate is **suitable to proceed to review/merge**.

The research conditions have been translated into the normative data standard, architecture, pilot acceptance gates and Phase 0 Issue #2.

No unresolved research blocker requires a re-plan before bounded Phase 0 implementation.
