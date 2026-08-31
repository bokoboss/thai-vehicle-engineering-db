# Phase 1 Batch C — Pickup and Source-Diversity Research v1

Date: 2026-08-31  
Branch: `chatgpt/phase-1-batch-c`  
Issue: #4

## Scope

Five targets:

1. Ford Ranger Double Cab Wildtrak 2.0L Bi-Turbo 4x4 10AT
2. Ford Everest Platinum 3.0L Turbo V6 4WD 10AT
3. Mitsubishi Triton Double Cab 2.4 ULTRA 4WD AT
4. Nissan Navara PRO-4X 4WD 7AT
5. Suzuki Swift GLX CVT

## Decision

**Proceed. No additional schema gap found.**

Batch C validates historical-version handling and manufacturer-specific source patterns.

## Major finding — historical target must not be overwritten

The pilot target `Ranger Wildtrak 2.0L Bi-Turbo 4x4` is no longer the current Wildtrak 4x4 powertrain in Thailand.

Official Ford evidence shows:

- next-generation Ranger Thailand launch in March 2022 with 2.0L Bi-Turbo option;
- 2023 official Wildtrak technical table includes exact `Wildtrak 2.0L Bi-Turbo 4x4 10AT`;
- current 2026 Wildtrak 4x4 page identifies a 2.0L Turbo single-turbo 4x4 configuration instead.

Therefore the old record must remain a historical exact configuration, never be silently “updated” with current specs.

The screenshot-verified 2023 technical table gives:

- 1,918 x 5,370 x 1,884 mm (W x L x H)
- 3,270 mm wheelbase
- 235 mm ground clearance, explicitly from vehicle lowest point
- 1,420 x 1,564 x 540 mm cargo box
- 800 mm wading
- exact 4x4 Wildtrak Bi-Turbo powertrain/fitment

No exact Ford Thailand turning-radius value was found in this source pass.

## Ford Everest Platinum

Current Ford Thailand pages clearly resolve:

- Everest Platinum 3.0L V6 Turbo 4WD 10AT
- 250 PS
- 600 Nm
- 21-inch / 275/45 R21

A June 2025 official technical brochure was located with parsed dimensional data, but screenshot retrieval was unstable during this pass.

Under the project evidence rules those parsed dimensions remain **lead-only** until visual re-verification. They are not promoted merely because the parser produced numbers.

## Mitsubishi Triton ULTRA 4WD AT

This is another useful historical exact configuration.

Official Mitsubishi Thailand evidence:

- product unveiling: 10 Nov 2023
- exact name: All-New Triton Double Cab ULTRA 4WD AT
- official November 2023 brochure technical page visually verified

The technical table supports:

- 5,320 x 1,865 x 1,795 mm
- wheelbase 3,130 mm
- track 1,570 / 1,565 mm
- clearance 222 mm
- minimum turning radius 6.2 m
- 18 x 7.5J / 265/60 R18 for ULTRA 4WD AT

Turning reference remains OEM-unspecified; it is not silently promoted to curb-to-curb.

## Nissan Navara PRO-4X

Nissan provides one of the cleanest current web-specification records in this batch.

The upgraded 2024 release explicitly includes:

`PRO-4X 4WD 7AT`

Current exact-column engineering data:

- L/W/H: 5,260 x 1,875 x 1,840 mm
- wheelbase: 3,150 mm
- tread: 1,570 / 1,570 mm
- ground clearance: 225 mm
- curb weight: 2,091 kg
- 255/65R17 All-Terrain
- turning radius: 6.3 m

Again, OEM track definition and turning curb/wall reference remain unspecified.

## Suzuki Swift GLX

Current Thailand page still lists GLX, while the named `NEW SUZUKI SWIFT` GLX release is traceable to February 2021.

Shared/current geometry:

- 3,845 x 1,735 x 1,495 mm
- wheelbase 2,450 mm
- turning radius 4.8 m
- ground clearance 120 mm

The current extracted table exposes two tread/wheel sets. They are preserved as grouped evidence until exact GLX column mapping is independently verified.

## Batch C implications

### Data-model success

The evidence model handles:

- historical configuration preserved alongside current successor;
- source visual-verification status;
- exact model release vs current sale state;
- multi-grade table ambiguity;
- turning value without curb/wall semantics.

### No new software work

No geometry/evidence/AVT/ramp schema change is requested.

Only the already-approved Identity Time Basis implementation in Issue #7 remains necessary before these temporal identities can be ingested cleanly.

Machine-readable packet:

`data/curation/phase1/batch_c_v1.json`
