# Wave 2C Research QA

Status: active research / manifest preparation  
Issue: #49  
Accepted baseline: `release_2026_09_d` — 41 configurations

## Purpose

Wave 2C fills engineering-envelope gaps that remain underrepresented after Release 2026_09_d:

- luxury/VIP MPV;
- long-wheelbase executive sedan;
- full-size luxury SUV;
- very long air-suspension off-road SUV;
- low-slung high-performance EV;
- ultra-long-wheelbase chauffeur sedan.

The selection is based on engineering-envelope value, not catalog popularity.

## Accepted tranche 1

Release 2026_09_d already accepts:

- Mercedes-Benz S 350 d Exclusive;
- BMW X7 xDrive40d M Sport.

Their importer qualification and safe promotion are complete. Tranche 2 therefore starts from 41 accepted configurations.

## Tranche 2 research result

Three manifest drafts are research-clean enough for bounded importer qualification:

1. Toyota Alphard HEV Premium Luxury
2. Porsche Taycan Turbo GT MY2027
3. Mercedes-Maybach S 580 e Premium

Defender 130 X-Dynamic HSE MY27 remains HOLD.

### Toyota Alphard HEV Premium Luxury

Research state: **MANIFEST DRAFT READY — TRANCHE 2**

The earlier temporal/grade mapping blocker is closed without reusing the older grade name.

Toyota Thailand's current grade page explicitly identifies:

`Alphard HEV Premium Luxury`

as a current 7-seat HEV grade.

Toyota Thailand's current exact-grade specification page publishes:

- overall dimensions: 5,010 × 1,850 × 1,950 mm;
- wheelbase: 3,000 mm;
- OEM tread front/rear: 1,605 / 1,625 mm;
- minimum ground clearance: 161 mm;
- minimum turning radius: 5.9 m;
- E-Four AWD;
- 19-inch alloy wheels;
- 225/55 R19 tyres.

Important semantic treatment:

- 1,850 mm remains `OEM_UNSPECIFIED` width;
- OEM tread remains non-AVT;
- 161 mm clearance uses an explicit load-condition object whose mass basis is OTHER because Toyota does not state the vehicle load condition;
- 5.9 m remains a radius with OEM_UNSPECIFIED reference/axle scope;
- no approach/departure/breakover value is invented.

The older 2025 `2.5 HEV Luxury` catalogue published 150 mm clearance. That older value is not carried into the current exact-grade record.

Manifest:

`data/curation/manifests/wave2c/toyota_alphard_hev_premium_luxury_sale_snapshot_20260903_v1.json`

Static contract: **PASS — 12 values + 7 assessments + 1 load condition**.

### Porsche Taycan Turbo GT MY2027

Research state: **MANIFEST DRAFT READY — TRANCHE 2**

Porsche Thailand explicitly identifies:

- Taycan Turbo GT;
- model year 2027;
- all-wheel drive;
- 760 kW / 1,034 PS overboost;
- 290 km/h top speed.

Porsche OEM exact-model global technical data supports structural geometry at `SAME_GEOMETRY_CONFIRMED`:

- length 4,968 mm;
- body width 1,998 mm;
- mirrors-open width 2,144 mm;
- height 1,378 mm;
- wheelbase 2,900 mm;
- OEM track 1,690 / 1,655 mm;
- 9.5 J × 21 ET60 with 265/35 ZR21 front;
- 11.5 J × 21 ET66 with 305/30 ZR21 rear.

Porsche exact-model vehicle information/Finder data also publishes air-suspension clearance states:

- normal: 126 mm;
- low: 116 mm;
- off-road: 146 mm.

Published OEM terrain values at normal ride height:

- approach: 8.0°;
- departure: 14.4°;
- breakover: 10.5°.

Important semantic treatment:

- country-variable mass is not normalized for Thailand;
- OEM track remains non-AVT;
- ride-height state and unspecified load state are retained separately;
- no geometry-derived ramp value is created;
- two official exact-model Porsche surfaces report turning-circle diameter as 11.2 m and 11.1 m;
- both turning observations remain raw and `turning_radius_normalized_m` remains UNKNOWN;
- there is no silent diameter-to-radius conversion.

Manifest:

`data/curation/manifests/wave2c/porsche_taycan_turbo_gt_my2027_v1.json`

Static contract: **PASS — 17 values + 5 assessments + 3 load/ride-height conditions**.

### Mercedes-Maybach S 580 e Premium

Research state: **MANIFEST DRAFT READY — CONFLICT AWARE**

Mercedes-Benz Thailand's current technical table explicitly identifies the S 580 e Premium engineering grade across three paint treatments and publishes:

- length 5,469 mm;
- width labelled “including mirrors” 1,921 mm;
- height 1,510 mm;
- plug-in hybrid;
- 4 seats.

The previous width-semantic blocker is not “corrected”; it is represented as an explicit evidence conflict.

Mercedes-Maybach Z223 owner documentation reports:

- mirrors-open width 2,109 mm;
- a 2021 edition reports excluding-mirrors width 1,921 mm;
- an earlier 2020 edition reports excluding-mirrors width 1,954 mm.

Therefore:

- the Thailand 1,921 mm mirror-width claim is normalized as `CONFLICTING`, exact configuration;
- the 2,109 mm Z223 mirror-width claim is normalized as `CONFLICTING`, `SAME_GEOMETRY_CONFIRMED`;
- no conflict decision selects either value;
- body width is not normalized because first-party owner manuals themselves disagree;
- no wheelbase, turning, clearance or mass is promoted without current exact Thailand evidence.

This is intentionally a conflict sentinel: Design Check/engineering use must remain fail-closed until the width envelope is resolved.

Manifest:

`data/curation/manifests/wave2c/mercedes_maybach_s580e_premium_sale_snapshot_20260903_v1.json`

Static contract: **PASS — 4 values + 7 assessments**.

### Defender 130 X-Dynamic HSE MY27

Research state: **HOLD — MY27 GEOMETRY APPLICABILITY**

Land Rover Thailand explicitly lists Defender 130 X-Dynamic HSE in the MY27 range.

A first-party Land Rover global technical sheet for Defender 130 publishes:

- overall length 5,358 mm;
- mirrors folded/open 2,008 / 2,105 mm;
- OEM track 1,706 / 1,702 mm;
- kerb-to-kerb / wall-to-wall turning circle 12.84 / 13.1 m;
- standard / off-road obstacle clearance 218.5 / 293 mm;
- standard approach/departure/ramp angles 30.1 / 24.5 / 22.0°;
- off-road approach/departure/ramp angles 37.6 / 28.8 / 27.9°.

However the recovered technical sheet is a 2024 global document, while the exact Thailand target is MY27. The project does not silently bridge that temporal gap.

No Defender MY27 manifest is created in this tranche.

Next action: recover a current MY27 first-party technical sheet, homologation, or other explicit continuity evidence.

## Tranche 2 static total

Drafts currently proposed:

| Vehicle | Sources | Observations | Values | Assessments | Loads |
| --- | ---: | ---: | ---: | ---: | ---: |
| Alphard HEV Premium Luxury | 2 | 6 | 12 | 7 | 1 |
| Taycan Turbo GT MY2027 | 4 | 7 | 17 | 5 | 3 |
| Maybach S 580 e Premium | 3 | 4 | 4 | 7 | 0 |
| **Total** | **9** | **17** | **33** | **19** | **4** |

These are manifest-entry totals; importer qualification must report unique-source/database deltas separately.

## Permanent Wave 2C rules

- a current web retrieval date is not a model year;
- use MODEL_YEAR only when first-party evidence explicitly states it;
- a one-day sale snapshot may bound an exact current configuration without claiming continuous sale history;
- current exact-grade evidence supersedes the need to silently map an older grade label;
- generic width is not body or mirror width;
- explicit width conflicts are retained rather than “corrected” by curator intuition;
- EC/DIN/curb/kerb and country-variable mass semantics remain distinct;
- OEM tread/track is not AVT outer-face track;
- air-suspension ride-height state is not a vehicle load state;
- clearance values with unspecified load remain explicitly load-unspecified;
- model-family/global geometry requires an explicit applicability grade;
- turning diameter is not silently converted to radius;
- conflicting OEM turning values remain unresolved;
- OEM-published ramp angles remain published evidence and are not treated as derived geometry;
- unknown/HOLD is valid when evidence continuity is insufficient.
