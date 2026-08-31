# Phase 1 Batch E — Luxury / Long-Wheelbase / Rear-Steer Research v1

Date: 2026-08-31  
Branch: `chatgpt/phase-1-batch-e`  
Issue: #4

## Scope

Four luxury targets:

1. Mercedes-Benz E 350 e AMG Dynamic (W214)
2. Mercedes-Maybach S 580 e Premium (Z223)
3. BMW 520d M Sport Pro (G60)
4. BMW 740d M Sport (G70)

## Decision

**Proceed. No new schema gap found.**

Batch E validates three important real-world behaviours:

- long-wheelbase configuration identity;
- rear-steering equipment changing by temporal revision;
- official source-label errors/semantic inconsistencies that must be preserved rather than silently corrected.

## Mercedes-Benz E 350 e AMG Dynamic

Current Mercedes-Benz Thailand pages resolve the E 350 e / AMG Dynamic product.

Thai page raw dimensions:

- L 4,950 mm
- `Width (with mirrors) 1,880 mm`
- H 1,461 mm

The width label is suspicious.

Official W214-family Mercedes documentation gives a mirrors-open width around 2,065 mm, while approximately 1,880 mm is in body-width territory.

Therefore:

- preserve the Thailand raw label/value;
- flag it `SEMANTICALLY_SUSPECT`;
- do not normalize 1,880 mm as mirror-open width;
- do not silently “correct” the Thai page from an adjacent/global manual.

No exact Thailand turning or rear-steering configuration evidence was located in this pass.

## Mercedes-Maybach S 580 e Premium

Thailand current store/product evidence resolves:

**Mercedes-Maybach S 580 e Premium — Z223**

Thai page raw dimensions:

- L 5,469 mm
- `Width (with mirrors) 1,921 mm`
- H 1,510 mm

Again, the width label conflicts with Mercedes' own Z223 family geometry:

- 1,921 mm aligns with body width;
- mirrors-open width is approximately 2,109 mm.

The Thai raw observation is therefore retained but not promoted as a mirror-open normalized value.

Because the Thai exact configuration is explicitly Z223, OEM Z223 geometry can support a same-geometry wheelbase reference of 3,396 mm with applicability metadata.

Rear-axle-steering documentation exists for the S-Class family, but exact Thailand S 580 e Premium equipment/function was not proven here. No AVT rear-steer mapping is attempted.

## BMW 520d M Sport Pro G60

The exact BMW Thailand specification effective 24 March 2025 was visually verified.

Exact / same-configuration data:

- L 5,060 mm
- W 1,900 mm
- H 1,515 mm
- wheelbase 2,995 mm
- mirrors-open width 2,156 mm
- kerb 1,850 kg
- GVW 2,405 kg
- front 8.5J x 20 / 245/40 R20
- rear 10J x 20 / 275/35 R20

No exact Thai turning value was found.

No Integral Active Steering evidence was found for this exact 520d M Sport Pro source set; do not assume rear steering from other G60 grades.

## BMW 740d M Sport — temporal rear-steering revision

This is the strongest Batch E engineering case.

### Exact specification effective 27 February 2025

Official BMW Thailand sheet:

- 5,391 x 1,950 x 1,544 mm
- kerb 2,205 kg
- front 9J x 20 / 255/45 R20
- rear 10.5J x 20 / 285/40 R20
- Adaptive 2-axle air suspension
- reviewed equipment sheet does **not** list Integral Active Steering

### Current page available 03/2026

BMW Thailand current 740d M Sport page provides:

- L 5,391
- W 1,950
- H 1,544
- mirrors-open 2,192
- wheelbase 3,215
- kerb 2,205
- GVW 2,845
- RWD
- **Integral Active Steering / four-wheel active steering explicitly listed**

This is not treated as a conflict to be “resolved” by choosing one.

It is a **temporal equipment revision**.

Rules:

- 2026 rear-steering presence must not be copied backward into the exact 2025 record;
- current 2026 record may store rear-steering system presence;
- max rear angle, phase/speed behaviour and linkage function remain unknown;
- AVT mapping fails closed.

## Why Batch E matters

### 1. Official sources can be semantically wrong

A high-authority source can still have a bad label.

Authority is not semantic correctness.

The Mercedes width cases demonstrate why the raw observation layer must be immutable and why normalized values require semantic review.

### 2. Same grade name can change equipment

BMW 740d demonstrates that even the same G70/740d M Sport name cannot be treated as timeless.

Temporal applicability belongs in exact engineering identity.

### 3. Rear-steer presence is not rear-steer kinematics

Even when BMW explicitly publishes Integral Active Steering, the database still lacks:

- max rear angle;
- phase by speed;
- relation to front angle;
- AVT linkage function.

Thus the record remains not AVT-ready.

## Phase 1 research coverage after Batch E

Batch A–E now covers approximately the full 30-target pilot research set, with some targets refined into exact official Thailand grade names.

The combined pilot already includes:

- mainstream cars;
- pickups/PPVs;
- vans/MPVs;
- EVs;
- very long luxury sedans;
- loaded/unloaded clearance;
- component-specific clearance;
- direct overhang;
- mirror/body envelopes;
- explicit curb-to-curb turning;
- rear/four-wheel steering;
- historical configurations;
- official-source conflicts;
- temporal equipment revisions;
- ambiguous multi-column tables;
- source-label semantic errors.

No new core schema change beyond Identity Time Basis v1 has been required.

## Remaining before Phase 1 acceptance

1. complete Issue #7 physical implementation;
2. merge/review the research packets;
3. perform cross-batch identity/coverage QA;
4. obtain at least three suitable geometry/drawing assets with stored fidelity/datum metadata;
5. select ingestion-ready records;
6. create actual database ingestion records only after those gates pass.

Machine-readable packet:

`data/curation/phase1/batch_e_v1.json`
