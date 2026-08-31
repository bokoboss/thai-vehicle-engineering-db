# Phase 1 Batch D — EV / Technology Stress Research v1

Date: 2026-08-31  
Branch: `chatgpt/phase-1-batch-d`  
Issue: #4

## Scope

Six EV targets:

1. Toyota bZ4X FWD
2. BYD DOLPHIN Extended Range
3. BYD SEAL MY24 AWD Performance
4. GWM ORA 07 PERFORMANCE
5. Tesla Model 3 Premium Long Range RWD
6. Hyundai IONIQ 6 Exclusive

## Decision

**Proceed. No new schema gap found.**

EV curation reinforces existing semantics rather than requiring an EV-specific schema branch.

The important EV differences are mainly:

- load-state-sensitive clearance;
- underfloor/battery relevance;
- rapid model/revision turnover;
- wheel-package and drivetrain identity;
- manufacturer-specific turning/track definitions.

## Toyota bZ4X FWD

The official 2026 catalog was visually verified.

FWD technical values:

- 4,690 x 1,860 x 1,650 mm
- wheelbase 2,850 mm
- front/rear track 1,600 / 1,610 mm
- minimum ground clearance 201 mm
- minimum turning radius 5.6 m

Toyota's accessory index separately calls it `bZ4X รุ่นใหม่ปี 2568`.

That raw label is preserved as `OEM_REVISION_LABEL` evidence and is **not** converted into model year.

Track definition and turning curb/wall semantics remain unspecified.

## BYD DOLPHIN Extended

RÊVER's current exact Extended Range technical page is unusually useful for clearance state:

- 4,290 x 1,770 x 1,570 mm
- wheelbase 2,700 mm
- track 1,530 / 1,530 mm
- ground clearance:
  - 155 mm unladen
  - 130 mm laden
- turning radius 5.25 m
- kerb 1,658 kg
- GVW 2,068 kg
- 205/50 R17

This is a strong EV load-state fixture.

It still does **not** establish AVT outer-face track or curb/wall turning semantics.

## BYD SEAL MY24 AWD Performance

Official Thai distributor evidence supports an explicit `MY24 AWD Performance` identity.

Exact technical data:

- 4,800 x 1,875 x 1,460 mm
- WB 2,920 mm
- track 1,620 / 1,625 mm
- turning radius 5.70 m
- ground clearance 120 mm **unladen**
- kerb 2,185 kg
- GVM 2,631 kg
- 390 kW / 670 Nm
- 82.56 kWh
- 235/45 R19

The 120 mm value is not battery-pack clearance and is not a loaded physical ramp limit.

## GWM ORA 07 PERFORMANCE

This is deliberately retained as a difficult historical-source case.

Official GWM currently provides:

- ORA 07 aftersales/manual support;
- an ORA 07 owner manual;
- model-series technical motor/battery/tyre information.

However, the owner manual explicitly states that basic overall dimensions and vehicle quality should be taken from vehicle-specific official documents.

This research pass did not recover a visually verified exact Thailand PERFORMANCE sales sheet.

Therefore:

- no secondary-source dimensions were imported;
- exact PERFORMANCE dimensions/turning/clearance remain NOT_FOUND/REVIEW_REQUIRED;
- model-series 150 kW / 340 Nm / 83.499 kWh / tyre-list information is retained only as a lead.

That is expected evidence-first behaviour.

## Tesla Model 3 — identity refinement

The original pilot target `current Long Range` is not sufficiently precise.

Tesla Thailand's current public page explicitly presents:

**Model 3 Premium — Long Range Rear-Wheel Drive**

The curated target is therefore narrowed to that exact drivetrain rather than silently treating every current Long Range as one configuration.

2024+ Thailand owner-manual geometry for RWD/Long Range:

- L 4,720 mm
- width:
  - body 1,850
  - folded mirrors 1,933
  - mirrors open 2,089
- H 1,440 mm
- WB 2,875 mm
- overhang front/rear 868 / 977 mm
- GC 138 mm
- track 1,584 / 1,584 mm, explicitly wheel-center based
- steering-wheel lock-to-lock 2.14 turns
- turning circle curb-to-curb 11.7 m

The controlled radius equivalent is 5.85 m.

As with Model Y, wheel-center track is **not AVT outer-face track**.

## Hyundai IONIQ 6 — identity refinement and geometry asset

The original target `IONIQ 6 Long Range` is refined to the official Thailand grade:

**IONIQ 6 Exclusive**

Hyundai's current highlights describes the vehicle as Long Range, while the exact technical leaflet calls the grade Exclusive.

The October 2025 official leaflet was visually verified and provides:

- 77.4 kWh
- RWD
- 225 HP / 350 Nm
- 545 km WLTP
- 4,855 x 1,880 x 1,495 mm
- WB 2,950 mm
- minimum ground clearance 141 mm
- kerb 1,986 kg
- minimum turning radius 5.91 m
- 20 x 8.5J / 245/40 R20

The dimension drawing also shows:

- front track 1,630 mm
- rear track 1,639 mm
- front overhang 850 mm
- rear overhang 1,055 mm

This is a strong candidate for the pilot's required engineering geometry/drawing assets.

## Batch D implications

### EV does not need a parallel data model

The accepted model already handles the key issues:

- load-state clearance;
- configuration/fitment;
- historical revisions;
- drivetrain identity;
- unknown track definitions;
- battery/underbody data gaps.

### AVT readiness remains deliberately difficult

None of these records becomes AVT-ready merely because it has complete retail dimensions.

Common blockers remain:

- OEM track semantics not outer-face tyre track;
- turning curb/wall reference unknown;
- turning axle scope unknown;
- road-wheel/AVT steering angle unknown;
- AVT lock-to-lock time unknown;
- exact plan profile unavailable.

### Ramp interpretation

Low EV clearance is useful screening context, but a retail `ground clearance` value does not identify the battery lower envelope or actual limiting underbody point.

No physical ramp angle is produced.

## Pilot progress after Batch D

Batch A–D now cover 26 research targets before luxury Batch E.

The pilot already demonstrates:

- explicit curb-to-curb turning;
- multiple turning values;
- loaded/unloaded clearance;
- component-specific clearance;
- direct overhang;
- mirror/body envelopes;
- rear/four-wheel steering;
- historical configurations;
- official-source conflicts;
- ambiguous multi-column tables;
- at least one strong exact-grade dimension drawing.

Remaining major work:

- Batch E luxury / long-wheelbase / rear-steer cases;
- two more useful geometry/drawing assets;
- identity-time migration Issue #7;
- curation QA and final ingestion selection.

Machine-readable packet:

`data/curation/phase1/batch_d_v1.json`
