# Wave 2C Research QA

Status: active research / manifest preparation  
Issue: #49  
Accepted baseline: `release_2026_09_c` — 39 configurations

## Purpose

Wave 2C fills engineering-envelope gaps that remain underrepresented after Release 2026_09_c:

- luxury/VIP MPV;
- long-wheelbase executive sedan;
- full-size luxury SUV;
- very long air-suspension off-road SUV;
- low-slung high-performance EV;
- ultra-long-wheelbase chauffeur sedan.

The selection is based on engineering envelope value, not catalog popularity.

## Current source gates

### Mercedes-Benz S 350 d Exclusive

Research state: **MANIFEST DRAFT READY**

Identity basis: bounded `SALE_PERIOD` snapshot on 3 September 2026.

Official Mercedes-Benz Thailand current technical data supports:

- length 5,289 mm;
- width including mirrors 2,109 mm;
- height 1,503 mm;
- EU kerb weight 2,020 kg.

The mirrors-open width is normalized because the source explicitly labels it as including door mirrors.

Not normalized:

- body-excluding-mirrors width;
- wheelbase;
- clearance;
- turning;
- AVT outer-face tracks.

AIRMATIC presence is retained raw only and does not create a ground-clearance state.

Manifest:

`data/curation/manifests/wave2c/mercedes_s350d_exclusive_sale_snapshot_20260903_v1.json`

Static contract: **PASS — 4 values + 6 assessments**.

### BMW X7 xDrive40d M Sport

Research state: **MANIFEST DRAFT READY**

Identity basis: bounded `SALE_PERIOD` snapshot on 3 September 2026.

Official BMW Thailand current technical data supports:

- length 5,181 mm;
- reported width 2,000 mm;
- height 1,835 mm;
- wheelbase 3,105 mm.

The 2,000 mm width remains `OEM_UNSPECIFIED`; body/mirror envelope semantics are not inferred.

BMW publishes 2,565 kg with an explicit EC ready-to-drive footnote that includes 90% fuel and a 75 kg driver. The current registry has no separate EC-mass parameter, so 2,565 kg remains a raw observation and `kerb_mass_kg` remains UNKNOWN.

Manifest:

`data/curation/manifests/wave2c/bmw_x7_xdrive40d_m_sport_sale_snapshot_20260903_v1.json`

Static contract: **PASS — 4 values + 7 assessments**.

### Toyota Alphard

Research state: **RESEARCH ACTIVE — TEMPORAL / GRADE MAPPING**

The official 2025 Toyota catalogue was visually reviewed. It publishes the 2.5 HEV Luxury column with 5,010 x 1,850 x 1,950 mm, wheelbase 3,000 mm, track 1,605 / 1,625 mm, clearance 150 mm and minimum turning radius 5.9 m.

However Toyota's current online grade surfaces have changed naming across crawls/current pages. The project will not equate older `2.5 HEV Luxury` evidence with a differently named current grade until temporal/grade continuity is explicitly proven.

No manifest yet.

### Defender 130 X-Dynamic HSE

Research state: **RESEARCH ACTIVE — TECHNICAL SOURCE GAP**

Land Rover Thailand explicitly lists MY27 Defender 130 X-Dynamic HSE and electronic air suspension.

The current page reviewed does not expose a complete dimension/clearance table in retrievable page content. No geometry is normalized yet.

### Porsche Taycan Turbo GT

Research state: **RESEARCH ACTIVE — GEOMETRY APPLICABILITY**

Porsche Thailand explicitly lists Taycan Turbo GT as MY2027. Porsche Finder Thailand identifies the current generation as J1 II since 2024.

Global Porsche Finder publishes detailed J1 II Turbo GT geometry including body/mirror/folded-mirror width, wheelbase, turning-circle diameter, air-suspension ride-height states and clearance states.

These global values are not yet normalized into a Thailand manifest until current Thailand J1 II same-geometry applicability is explicitly closed.

### Mercedes-Maybach S 580 e Premium

Research state: **RESEARCH ACTIVE — WIDTH SEMANTIC CONFLICT**

Mercedes-Benz Thailand currently publishes:

- length 5,469 mm;
- width labelled “including mirrors” 1,921 mm;
- height 1,510 mm.

The 1,921 mm value is semantically suspicious as a mirrors-included envelope. This project does not silently relabel it as body width.

No width normalization or manifest is created until the contradiction is resolved from first-party technical evidence.

## Permanent Wave 2C rules

- a current web page retrieval date is not a model year;
- a one-day sale snapshot may bound an exact current configuration without claiming launch date or continuous sale history;
- EC ready-to-drive mass is not silently converted to kerb mass;
- explicit mirrors-open width may be normalized as such;
- generic width remains OEM_UNSPECIFIED;
- air suspension does not create clearance unless the OEM publishes the actual clearance state;
- model-family/global geometry needs explicit same-geometry applicability before use for Thailand;
- suspicious OEM labels are retained as conflicts/unknowns rather than “corrected”.
