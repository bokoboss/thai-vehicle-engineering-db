# Phase 1 Batch A — Research and Curation Review v1

Date: 2026-08-31  
Branch: `chatgpt/phase-1-batch-a`  
Issue: #4

## Decision

**Proceed. No schema/software remediation required from Batch A v1.**

The first six real-world targets exercise the accepted evidence model without requiring the data to be bent to fit the schema.

## Identity status

| Target | Identity state | Database ingestion |
|---|---|---|
| BYD ATTO 3 MY24 Extended (Local Production) | RESOLVED_EXACT | Eligible after curation review |
| Tesla Model Y Premium Long Range RWD, 19-inch, 2025+ | RESOLVED_EXACT | Eligible after curation review |
| Volvo EX30 Ultra Single Motor Extended Range MY2026, 19-inch | RESOLVED_EXACT | Eligible after curation review |
| Mazda MX-5 35th Anniversary Edition 2.0 RF AT | PARTIAL | Hold exact configuration until model-year policy/evidence is resolved |
| Kia EV5 Earth Long Range | PARTIAL | Hold exact configuration until explicit model-year applicability is resolved |
| MG IM6 Long Range | PARTIAL | Hold exact configuration until explicit model-year applicability is resolved |

A launch year or current-sale date is not silently converted into model year.

## Important semantic findings

### 1. Mazda is the control-quality record

Thai OEM specification directly provides:

- front/rear overhang;
- between-axles **laden** clearance;
- explicit **kerb-to-kerb** minimum turning radius;
- tread;
- tyre/rim.

It still does not provide AVT outer-face track or curb axle scope, so it must not be called AVT-ready.

### 2. BYD proves load-state preservation

The current Thai distributor page separately publishes:

- 175 mm unladen ground clearance;
- 150 mm laden ground clearance.

The 5.35 m value is explicitly called a radius, but curb/wall reference is not stated.

### 3. Tesla proves width and centerline-track semantics

The 2025+ Thailand owner material distinguishes:

- body/excluding mirrors;
- folded mirrors;
- mirrors open;
- laden/unladen clearance;
- front/rear wheel-center track.

Tesla explicitly says the track is based on wheel-center measurement. It therefore remains OEM centerline geometry, **not AVT outer-face track**.

The published 12.13 m curb-to-curb turning **circle** is stored as the raw observation; a 6.065 m radius is only a controlled diameter-to-radius derivation, with axle scope still unresolved.

### 4. Volvo gives the first real evidence conflict

For the exact/near-exact target:

- Thai technical brochure: Min. Turning Circle = 10.7 m
- 2026 Thai configurator/build output: Turning circle = 11 m

Both are official Volvo evidence.

Do not average or silently choose one. The record remains CONFLICTING pending applicability/revision analysis.

Volvo also supplies strong body/mirror width semantics and a load-qualified 171 mm clearance.

### 5. Kia gives excellent longitudinal geometry but incomplete identity/turning evidence

Thai current spec publishes direct front/rear overhang 910/955 mm, wheelbase and tyre fitment.

No exact Thai turning value was found in the current Thailand source search. Adjacent-market Kia values are treated only as leads until same-geometry applicability is proven.

### 6. MG proves rear-steering extensibility

The Thai official page states Intelligent Four-wheel Steering System with Crab Mode and 5.1 m minimum turning radius across IM6 grades.

This establishes rear/four-wheel steering presence, but not the linkage function, max rear angle, or phase/speed behavior required for a defensible AVT mapping.

## Batch A acceptance contribution

Already demonstrated:

- explicit kerb-to-kerb case: yes
- structured load/clearance cases: at least 4
- direct overhang cases: Mazda, Tesla, Kia
- multi-envelope body/mirror width: Tesla, Volvo
- rear/four-wheel steering: MG IM6
- real evidence conflict: Volvo EX30

Still needed later in the 30-vehicle pilot:

- at least 10 total useful turning observations;
- at least 3 useful geometry/drawing assets;
- more exact identity resolutions;
- enough exact records to test database ingestion at scale.

## Current action

Review/lock exact identities for the three PARTIAL records before creating final exact vehicle-configuration rows.

The complete machine-readable curation packet is:

`data/curation/phase1/batch_a_v1.json`
