# Foundation Deep Research Gate — 2026-08-30

## Decision

**GO WITH CONDITIONS — High confidence.**

The project concept, evidence-first architecture, source hierarchy and bounded Phase 0 direction remain valid. The research did **not** justify a re-plan.

Foundation PR #1 must, however, be amended before schema implementation.

## Must-fix conditions incorporated into the foundation

1. Split evidence method, conflict/resolution, verification and availability into orthogonal state dimensions.
2. Preserve AVT curb-turning axle scope and wall-turning body/body+loads envelope scope.
3. Distinguish actual wheel angles from AVT's virtual-centre Maximum Steering Angle.
4. Do not allow OEM centreline tread + nominal tyre section width alone to create an AVT-ready outer-face track.
5. Add structured clearance-type semantics.
6. Add structured load condition and static-loaded tyre radius for physical ramp geometry.
7. Distinguish side silhouette from longitudinal lower interference envelope and use explicit screening-angle parameter codes.
8. Represent rear/secondary steering with axle/linkage/mode behaviour, not only a boolean.
9. Preserve source-reported width semantics and normalize mirror/body envelopes only when known.

## Research conclusions that remain non-blocking

- AVT Level 0 engineering data sheet: feasible.
- AVT Level 1 input preparation sheet: feasible.
- AVT Level 2 assisted/manual Vehicle Wizard/library workflow: feasible.
- Automated ATL/ATX serialization: not established by the reviewed official public documentation and remains an experiment/research gate.
- Detailed ramp solver: deferred; Phase 0 only needs a schema capable of storing the required future geometry/state.
- DLT/MOT data is useful for Thailand model presence/prioritization, not exact engineering identity.

## Phase 0 consequence

The fundamental Issue #2 scope remains correct but its fixtures/gates must exercise the amended semantics, including fail-closed AVT-track, turning-scope, clearance, rear-steering, width and geometry-role cases.

## Pilot consequence

Use a mixed 30-configuration stress set spanning mainstream cars, pickups/PPVs, MPV/van, EVs, explicit kerb-to-kerb semantics, loaded/unloaded clearance, direct overhang, rear steering, mirror-width states and very long luxury vehicles.

The first curation pass should prove semantic fidelity rather than attempt AVT/ramp completeness for every vehicle.

## Central acceptance principle

Unknown is preferable to unsupported precision.
