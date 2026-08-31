# Phase 1 Pilot Cross-Batch Coverage QA v1

Date: 2026-08-31  
Scope: Batch A–E research packets  
Issue: #4

## Verdict

**RESEARCH COVERAGE: PASS WITH INGESTION CONDITIONS**

The first pilot research pass covers exactly **30 target records** across Batch A–E.

No new core geometry/evidence/AVT/ramp schema gap was found after Identity Time Basis v1.

The remaining software dependency is Issue #7, which implements the accepted non-MY temporal identity contract.

## Coverage summary

| Pilot gate | Required | Research result | Status |
|---|---:|---:|---|
| Target configurations researched | ~30 | 30 | PASS |
| Useful turning-observation cases | >=10 | 21 records contain usable or intentionally held turning evidence | PASS |
| Front/rear overhang / strong longitudinal geometry | >=5 | 5 records with normalized front/rear overhang candidates, plus additional technical longitudinal references | PASS |
| Structured clearance/load-state evidence | >=5 | >=6 records with source-explicit load states | PASS |
| Useful geometry/drawing assets | >=3 | 3 accepted candidates | PASS |
| Rear/four-wheel-steering case | >=1 | MG IM6 + current BMW 740d | PASS |
| Explicit curb/kerb-to-curb turning | >=1 | Mazda MX-5 + Tesla Model Y/Model 3 circle evidence | PASS |
| Real evidence conflict | >=1 | Volvo EX30 + Alphard + Mercedes/BMW semantic/temporal conflicts | PASS |
| Multi-envelope mirror/body width | >=1 | Tesla Model Y, Tesla Model 3, Volvo EX30, BMW/Mercedes source cases | PASS |

## Important counting note

The physical Phase 0 schema requires a load-condition record for clearance values, including an explicit UNKNOWN/OTHER state when a source does not state load.

That does **not** mean every clearance record is a source-supported load-state case.

For pilot acceptance, count only records where the source itself states load applicability.

Source-explicit examples include:

- Mazda MX-5: between axles, laden;
- BYD ATTO 3: unladen / laden;
- Tesla Model Y: unladen / laden;
- Volvo EX30: kerb weight plus one person;
- BYD DOLPHIN: unladen / laden;
- BYD SEAL MY24 AWD Performance: unladen.

This distinction prevents a structured database placeholder from being misreported as source evidence.

## Geometry/drawing asset gate

### G1 — Hyundai IONIQ 6 Exclusive Thailand

Source:
official Hyundai Thailand technical leaflet, October 2025.

Role candidate:
`AXLE_DATUM_GEOMETRY`

Useful callouts:
- overall L/W/H;
- wheelbase;
- front/rear overhang;
- front/rear track;
- ground clearance.

Applicability:
exact Thailand grade.

### G2 — Tesla Model Y Premium 5-Seater Thailand

Source:
Tesla Thailand 2025+ owner's-manual Dimensions page.

Role candidate:
`AXLE_DATUM_GEOMETRY`

The official page includes a front/side dimension image with A–H callouts and exact Thailand Premium 5-Seater values:
- L/W/H;
- wheelbase;
- front/rear overhang;
- ground clearance loaded/unloaded;
- track.

Track is explicitly wheel-center based.

### G3 — Tesla Model 3 2024+ RWD / Long Range geometry family

Source:
official Tesla 2024+ Model 3 owner's-manual dimension diagram.

Role candidate:
`AXLE_DATUM_GEOMETRY`

The diagram provides:
- L/W/H;
- wheelbase;
- front/rear overhang;
- clearance;
- front/rear track.

The same RWD/Long Range dimensions are already observed in the Thailand 2024+ owner-manual source set.

Applicability must be retained as exact/same-geometry evidence according to the final source record used during ingestion.

### Not counted — Ford Ranger BEMM

An official Ford Ranger P703 Body and Equipment Mounting Manual was located and contains valuable dimension/wheelhouse/frame geometry.

However, the web PDF was too large for the required screenshot verification path in this research pass.

Therefore it remains a **future high-value geometry-source lead** and is not needed to make the >=3 pilot gate pass.

## Identity state after research

The research packets intentionally use intermediate labels because Issue #7 physical support is still pending.

At cross-batch level:

- 30 records researched;
- 23 records are already exact or credible exact-temporal candidates;
- 7 remain HOLD / PARTIAL / same-geometry candidates.

The 7 holds are not schema failures:

1. Mazda MX-5 35th Anniversary Edition — becomes a strong EDITION_RELEASE exact candidate under Identity Time Basis v1, but packet has not yet been reclassified after Issue #7.
2. Kia EV5 Earth Long Range — current grade/fitment resolved; temporal applicability still needs stronger public evidence.
3. MG IM6 Long Range — grade resolved; temporal basis and rear-steer linkage details remain incomplete.
4. Toyota Yaris ATIV Premium Luxury — current grade resolved; temporal revision needs stronger evidence.
5. Toyota Alphard 2.5 HEV — official current-vs-2025 geometry conflict requires temporal split/resolution.
6. Suzuki Swift GLX — current and 2021 same-name evidence exists; same-geometry continuity must be proven before exact promotion.
7. GWM ORA 07 PERFORMANCE — historical exact Thailand sales geometry was not recovered from primary sources in this pass.

## Turning evidence

At least 21 records exercise turning semantics.

The important point is not that all 21 are normalized-ready.

The set deliberately includes:

- explicit kerb-to-kerb radius;
- curb-to-curb turning circle requiring controlled diameter-to-radius conversion;
- OEM minimum turning radius with unknown curb/wall reference;
- multi-column turning values whose exact grade association is held;
- official-source turning conflict.

This satisfies the pilot's semantic stress objective.

## Conflict coverage

### Volvo EX30
Official turning circle 10.7 vs 11.0 m.

### Toyota Alphard
Same grade name across temporal official sources:
- height 1,945 vs 1,950 mm;
- ground clearance 150 vs 161 mm.

### Mercedes E-Class / Maybach
Thai OEM raw labels claim `Width (with mirrors)` for values that conflict with OEM family mirror-open dimensions.

Preserve the raw Thailand observation; do not silently correct it.

### BMW 740d
2025 exact equipment sheet does not list Integral Active Steering; current 03/2026 page explicitly does.

Treat as temporal equipment revision, not timeless equipment truth.

## AVT readiness conclusion

**No pilot record should be expected to become AVT_READY merely from retail/OEM dimensions.**

Recurring blockers remain:

- OEM tread/track is undefined or wheel-center based rather than outer tyre faces;
- curb/wall turning semantics unresolved;
- curb axle scope unresolved;
- actual/virtual AVT steering angle unavailable;
- AVT lock-to-lock time unavailable;
- rear-steering linkage incomplete;
- exact AVT plan profile unavailable.

This is expected and validates the fail-closed model.

## Ramp conclusion

Pilot clearance data is useful for engineering reference and future screening.

It is not enough for physical geometry-derived ramp angles because public sources rarely provide:

- static-loaded tyre radius;
- limiting front/rear contact point;
- lower underbody envelope;
- battery-pack lower envelope;
- suspension/load behavior.

No physical ramp-angle value should be produced in Phase 1.

## Research quality findings

The pilot confirms five important operating rules:

1. **Historical configurations are first-class records.**  
   Example: Ranger Wildtrak 2.0L Bi-Turbo 4x4 must not be overwritten by the current single-turbo Wildtrak.

2. **The same grade name can change geometry/equipment.**  
   Example: Alphard geometry and BMW 740d steering equipment.

3. **Primary sources can contain bad labels.**  
   Example: Mercedes mirror-width wording.

4. **Parser output is not grade association evidence.**  
   Honda multi-column tables stay grouped when column mapping is not proven.

5. **A missing primary source is a result.**  
   ORA 07 PERFORMANCE remains incomplete rather than being filled from secondary specifications.

## Phase 1 research gate

**PASS WITH CONDITIONS**

Conditions before production ingestion:

1. Issue #7 identity-time migration/domain support must pass and merge.
2. Consolidated research PR must be accepted.
3. Ingestion wave must use only source/parameter candidates that have passed identity and semantic QA.
4. Held multi-column values remain raw observations until second review.
5. Conflict records must be ingested as conflicts, not collapsed preferred values.
6. Geometry assets must retain source/applicability/fidelity metadata.
