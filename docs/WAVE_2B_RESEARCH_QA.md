# Wave 2B research / curation QA

Status: **ACTIVE**

Baseline accepted release: `release_2026_09_a` — 27 configurations.

Wave 2B is a data-only expansion under Data Release Pipeline v1. Mainstream engineering coverage is tracked in Issue #37; the dedicated supercar engineering-envelope tranche is tracked in Issue #38.

## Current result

### BYD M6 Extended 7 Seats

Research state: **MANIFEST DRAFT READY**

Identity basis: `EDITION_RELEASE`.

Raw identity label: `BYD M6 7-seat Extended sales campaign commencing 28 November 2024`.

Official Rêver Thailand evidence establishes the exact 7-seat Extended configuration and the current technical page provides a separate Extended 7 Seats column.

Normalized draft values:

- overall length: 4,710 mm;
- reported overall width: 1,810 mm, envelope definition OEM_UNSPECIFIED;
- overall height: 1,690 mm;
- wheelbase: 2,800 mm;
- OEM wheel track front/rear: 1,540 / 1,530 mm;
- kerb weight: 1,915 kg;
- gross vehicle weight: 2,489 kg;
- ground clearance: 170 mm unladen;
- ground clearance: 140 mm maximum loaded;
- minimum turning radius: 8.5 m;
- front/rear wheel: 17-inch alloy;
- front/rear tyre: 225/55 R17;
- drivetrain: FWD.

The published 8.5 m minimum turning radius is unusually large for the vehicle class. It is intentionally retained exactly as first-party evidence. No correction, halving/doubling, or conversion to a different turning reference is permitted without new first-party evidence.

Body width, mirrors-open width, and AVT outer-face tracks remain unresolved/fail-closed.

Manifest:

`data/curation/manifests/wave2b/byd_m6_extended_7seat_release_20241128_v1.json`

Static registry/reference contract: **PASS — 15 values + 4 assessments**.

Primary sources:

https://www.reverautomotive.com/news/byd-m6-7-seat-price-announcement

https://www.reverautomotive.com/en/model/m6/overview

## Supercar tranche

### Porsche 911 Carrera GTS MY2027 Thailand

Research state: **RESEARCH ACTIVE — HIGH CONFIDENCE**

Porsche Thailand explicitly lists the current 911 Carrera GTS as MY2027, RWD automatic, and provides Thailand pricing. The same official Thailand model page documents:

- standard rear-axle steering on GTS;
- PASM sports chassis;
- optional hydraulic front lift raising the front by approximately 40 mm;
- lift operation up to approximately 35 km/h.

Porsche Finder Thailand provides exact local technical-data examples including body width, mirrors-open width, wheelbase, turning-circle diameter and multiple mass definitions. Current MY2027 exact technical geometry still needs to be locked before manifest normalization; older MY24 Finder values must not be carried forward silently.

Primary sources:

https://www.porsche.com/pap/_thailand_/models/911/carrera-models/911-carrera-gts/

https://finder.porsche.com/th/en-TH/

### Lamborghini Revuelto

Research active. Official Lamborghini current model/brochure evidence is strong globally, but exact authorised Thailand applicability must be established before global geometry is used as Thailand configuration evidence.

### Ferrari 296 GTB

Research active. Ferrari identifies Cavallino Motors Co. Ltd as the authorised Thailand dealer and Ferrari Approved Thailand has documented Thailand-delivered 296 GTB inventory. Exact bounded Thailand identity and same-geometry applicability remain required.

### McLaren Artura Coupe

Research active. McLaren provides APAC/Thailand program evidence and official Artura technical/owner material, but exact Thailand-delivered/current-sales applicability must be established before manifest promotion.

## Permanent Wave 2B rules

- Unknown remains acceptable.
- Generic width is not body or mirrors-open width.
- OEM tread/track is not AVT outer-face track.
- Suspicious first-party numbers are retained and flagged, not silently repaired.
- Raw mass labels are not converted across dry / DIN / EC / curb / unladen semantics.
- Front-lift amount is not automatically added to ground clearance.
- Lift amount alone does not create approach/departure/breakover angles.
- Cross-market geometry requires evidence-backed same-geometry applicability.
- No application source change is required merely because accepted release membership grows.
