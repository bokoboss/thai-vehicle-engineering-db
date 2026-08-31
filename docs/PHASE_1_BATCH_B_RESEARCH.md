# Phase 1 Batch B — Mainstream Thailand Research v1

Date: 2026-08-31  
Branch: `chatgpt/phase-1-batch-b`  
Issue: #4

## Scope

Nine high-use Thai-market targets:

1. Honda City e:HEV RS
2. Honda Civic e:HEV RS
3. Honda Accord e:HEV RS
4. Toyota Yaris ATIV Premium Luxury
5. Toyota Fortuner 2.4 Leader V 4WD
6. Toyota Alphard 2.5 HEV
7. Toyota Commuter Diesel 2.8 AT
8. Isuzu V-CROSS 2.2 Ddi Z 4-door A/T 4x4
9. Isuzu MU-X 4WD 2.2 Ddi ULTIMATE

## Decision

**Proceed with curation. No new geometry/evidence schema gap found.**

The only software-contract issue exposed by Batch B is the already-isolated identity-time problem in PR #6 / Issue #7.

## Key research discipline

### Honda multi-value tables

Honda's official HTML exposes reliable shared values, but when rows contain multiple values the extracted representation does not preserve enough grade-column structure to safely assign every value to RS.

Therefore:

- common/shared values are normalization candidates;
- multi-valued rows remain grouped raw observations;
- no visual guessing of which number belongs to RS.

Examples held:
- City length/height/rear tread/clearance/wheel/tyre;
- Civic steering lock-to-lock / turning radius / tread / wheel / tyre;
- Accord wheelbase / tread / wheel / tyre.

This is a successful evidence-model behavior, not an incomplete-data failure.

## Strong cases

### Toyota Fortuner

Official 2025 catalog, visually verified, provides common five-grade geometry:

- 4,795 x 1,855 x 1,835 mm;
- wheelbase 2,750 mm;
- tread 1,540 / 1,555 mm;
- minimum ground clearance 193 mm, explicitly measured from the vehicle's lowest point.

This is a better clearance semantic than a bare “ground clearance” label.

### Toyota Commuter

Official 2025 catalog technical page, visually verified:

- 5,915 x 1,950 x 2,280 mm;
- wheelbase 3,860 mm;
- tread 1,675 / 1,670 mm;
- minimum turning radius 6.4 m.

The current Thai grade page confirms Diesel 2.8 AT, 15 seats.

### Isuzu V-CROSS

The 2026 official brochure technical page, visually verified, gives for 2.2 Ddi Z 4-door A/T:

- 5,280 x 1,870 x 1,810 mm;
- wheelbase 3,125 mm;
- tread 1,570 / 1,570 mm;
- turning radius 6.1 m;
- ground clearance 240 mm **at the rear axle housing**;
- tyre 265/60R18.

The location qualifier is preserved rather than normalized as a generic global minimum.

### Isuzu MU-X

Official 2026 launch and brochure resolve the target as:

**MU-X “THE NEXT PEAK” 4WD 2.2 Ddi MAXFORCE ULTIMATE**

Shared table values safely captured:
- wheelbase 2,855 mm;
- tread 1,570 / 1,570 mm;
- turning radius 5.6 m.

Exact dimension/clearance/wheel column mapping remains held for second review instead of guessed.

## Important temporal/revision finding — Toyota Alphard

For `Alphard 2.5 HEV`:

Current official HTML:
- 5,010 x 1,850 x 1,950 mm
- ground clearance 161 mm
- turning radius 5.9 m

Official 2025 catalog, screenshot-verified:
- 5,010 x 1,850 x 1,945 mm
- ground clearance 150 mm
- turning radius 5.9 m

This should not be averaged or silently selected.

It demonstrates why the same commercial grade name needs an evidence-backed temporal revision discriminator.

## Identity-time contract consequence

Batch B independently confirms PR #6 is necessary.

Examples:

- Honda uses explicit “ใหม่” release events with exact launch dates but not necessarily model-year language.
- Toyota accessory/document naming often uses wording such as `รุ่นปรับปรุงปี 2568`, which should remain an OEM revision label rather than becoming MY2025 by inference.
- Isuzu's February 2026 launch cleanly defines a new product release that can be represented as `EDITION_RELEASE`.

## Pilot coverage contribution

Batch A + B now already contains many of the required semantic patterns:

- useful turning evidence: well above the initial minimum trajectory;
- direct/strong longitudinal geometry: Mazda, Tesla, Kia, Toyota/Isuzu records;
- structured clearance references: laden/unladen cases plus Fortuner lowest-point and V-CROSS rear-axle-housing cases;
- body/mirror width envelopes: Tesla and Volvo;
- rear/four-wheel steering: MG IM6;
- real official-source conflicts: Volvo EX30 and temporal Alphard geometry difference.

Still outstanding:
- at least 3 useful engineering geometry/drawing assets;
- exact identity closure for records dependent on PR #6;
- later batches for pickups/source diversity, EV stress, and luxury/long-wheelbase vehicles.

Machine-readable packet:
`data/curation/phase1/batch_b_v1.json`
