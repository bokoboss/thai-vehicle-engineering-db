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


## Hyundai STARIA Premium MY25

Research state: **MANIFEST DRAFT READY**

Identity basis: `MODEL_YEAR`.

The official Hyundai Thailand brochure explicitly identifies MY25 in the source designation and provides the exact Premium engineering table.

Normalized draft values include:

- 5,253 x 1,997 x 1,990 mm;
- wheelbase 3,273 mm;
- front/rear overhang 910 / 1,070 mm;
- OEM 18-inch tread 1,721 / 1,732 mm with SAME_GEOMETRY_CONFIRMED applicability from the Thailand US4 owner manual;
- minimum ground clearance 186 mm, load/reference unspecified;
- minimum turning radius 5.97 m with OEM_UNSPECIFIED reference/axle scope;
- 18 x 7.0J wheels / 235/55 R18 tyres.

Body/mirror width, exact kerb mass and AVT outer-face tracks remain fail-closed.

Manifest:

`data/curation/manifests/wave2b/hyundai_staria_premium_my2025_v1.json`

Static registry/reference contract: **PASS — 14 values + 5 assessments**.

## Porsche 911 Carrera GTS 992 II — Thailand-delivered 2025

Research state: **MANIFEST DRAFT READY**

Identity basis: `EDITION_RELEASE`.

A bounded exact Porsche Finder Thailand vehicle from Porsche Centre Bangkok is used instead of carrying current MY2027 geometry backwards/forwards across model years.

Exact local evidence supports:

- length 4,553 mm;
- body width 1,852 mm;
- mirrors-open width 2,033 mm;
- wheelbase 2,450 mm;
- turning circle diameter 10.9 m retained as raw OEM turning text;
- curb weight 1,604 kg;
- permissible gross weight 2,045 kg;
- 20-inch front / 21-inch rear Carrera GTS wheels;
- installed rear-axle steering;
- installed front-axle lift.

The current Porsche Thailand GTS model page corroborates the lift-system behaviour: approximately +40 mm at the front, usable to approximately 35 km/h. This is retained as raw evidence only; it is not added to ground clearance and no ramp angle is derived.

No normalized turning radius is created because dividing the published 10.9 m diameter would be a derivation and the reference path remains unspecified. Exact height, base ground clearance and AVT outer-face tracks remain assessment-only.

Manifest:

`data/curation/manifests/wave2b/porsche_911_carrera_gts_992ii_delivered_2025_v1.json`

Static registry/reference contract: **PASS — 9 values + 6 assessments**.


## Toyota Yaris Cross HEV Premium Luxury — 2026 catalogue edition

Research state: **MANIFEST DRAFT READY**

Identity basis: `EDITION_RELEASE`; the 2026 catalogue year is explicitly not treated as model year.

Normalized: 4,310 x 1,770 x 1,615 mm; wheelbase 2,620 mm; OEM tread 1,525 / 1,520 mm; clearance 210 mm with unspecified load/reference; turning radius 5.2 m with OEM_UNSPECIFIED reference/axle scope; 18-inch alloy / 215/55 R18.

Body/mirror width, kerb mass and AVT outer-face tracks remain unresolved.

Static contract: **PASS — 12 values + 5 assessments**.

Manifest: `data/curation/manifests/wave2b/toyota_yaris_cross_hev_premium_luxury_catalog_2026_v1.json`

## Honda HR-V e:HEV RS — New HR-V late-2024 release

Research state: **MANIFEST DRAFT READY**

Identity basis: `EDITION_RELEASE`. Honda Thailand documents the New HR-V e:HEV RS launch/customer-delivery period from 28 November 2567 and the exact RS grade remains current.

Normalized: 4,385 x 1,790 x 1,590 mm; wheelbase 2,610 mm; OEM tread 1,542 / 1,543 mm; clearance 196 mm with unspecified load/reference; turning radius 5.5 m with OEM_UNSPECIFIED reference/axle scope; steering lock-to-lock 2.44 turns; 18 x 7.5J / 225/50 R18.

Honda publishes raw `น้ำหนักรถ / Weight = 1,404 kg`, but the label does not explicitly establish curb/kerb semantics. The value is retained as a raw observation and `kerb_mass_kg` remains UNKNOWN.

Static contract: **PASS — 13 values + 5 assessments**.

Manifest: `data/curation/manifests/wave2b/honda_hrv_ehev_rs_new_release_20241128_v1.json`

## Toyota Camry HEV Premium Luxury — new hybrid October 2567 release

Research state: **MANIFEST DRAFT READY**

Identity basis: `EDITION_RELEASE`. Toyota's own aftersales applicability language identifies `รถยนต์คัมรี ไฮบริดรุ่นใหม่ตุลาคม 2567`; the Buddhist year is retained as a release label, not model year.

Normalized: 4,920 x 1,840 x 1,445 mm; wheelbase 2,825 mm; OEM tread 1,580 / 1,590 mm; clearance 135 mm with unspecified load/reference; turning radius 5.7 m with OEM_UNSPECIFIED reference/axle scope; 18-inch alloy / 235/45 R18.

Body/mirror width, kerb mass and AVT outer-face tracks remain unresolved.

Static contract: **PASS — 12 values + 5 assessments**.

Manifest: `data/curation/manifests/wave2b/toyota_camry_hev_premium_luxury_new_release_2567_v1.json`

## Mainstream tranche status

Five of the six initial mainstream targets are manifest-draft ready:

- BYD M6 Extended 7 Seats
- Hyundai STARIA Premium MY25
- Toyota Yaris Cross HEV Premium Luxury
- Honda HR-V e:HEV RS
- Toyota Camry HEV Premium Luxury

Current mainstream draft total: **66 normalized values + 24 explicit assessments**.

DENZA D9 Performance AWD remains RESEARCH_ACTIVE because exact Thailand Performance AWD technical geometry/mass documentation has not yet been recovered from a first-party Thailand source. Global/other-market D9 dimensions are not being promoted as Thailand data without same-geometry proof.


## Lamborghini Revuelto — Thailand launch 25 July 2023

Research state: **MANIFEST DRAFT READY**

Identity basis: `EDITION_RELEASE`.

Lamborghini's official dealer locator establishes Lamborghini Bangkok / Renazzo Motor as the authorized Bangkok dealer. Reputable contemporaneous Thailand launch coverage records the exact Revuelto launch, price and local dimensions. Lamborghini's official 2024 digital brochure provides structural geometry that matches the Thailand launch dimensions.

Normalized with `SAME_GEOMETRY_CONFIRMED` applicability:

- length 4,947 mm;
- body width excluding mirrors 2,033 mm;
- width including mirrors 2,266 mm;
- height 1,160 mm;
- wheelbase 2,779 mm;
- OEM front/rear track 1,720 / 1,701 mm;
- standard front wheel/tyre 20 x 9.5J / 265/35 ZR20;
- standard rear wheel/tyre 21 x 12J / 345/30 ZR21.

Lamborghini's published 1,772 kg value is explicitly Dry Weight and is retained only as raw evidence. It is not normalized as kerb mass. Ground clearance, turning value, folded-mirror width and AVT outer-face tracks remain unresolved.

Static contract: **PASS — 11 values + 6 assessments**.

Manifest: `data/curation/manifests/wave2b/lamborghini_revuelto_th_launch_20230725_v1.json`

## Ferrari 296 GTB

Research state: **RESEARCH ACTIVE — GEOMETRY APPLICABILITY GATE**

Ferrari Approved Thailand records a 2024 296 GTB at Cavallino Motors Co. Ltd, and Ferrari's official 296 GTB technical sheet publishes model-level dimensions and track. A manifest is intentionally deferred because the exact Thailand Approved car's option/geometry relationship to the global technical sheet has not yet been established to the project's SAME_GEOMETRY_CONFIRMED standard.

Do not normalize Ferrari's 1,470 kg Dry Weight as kerb mass.

## McLaren Artura Coupe

Research state: **RESEARCH ACTIVE — GEOMETRY APPLICABILITY GATE**

McLaren's official Qualified programme exposes Thailand as a supported APAC country and lists Artura in the programme, but no exact Thailand stock/detail record with technical dimensions was recovered in this pass. Other-market McLaren Qualified Artura dimensions are therefore not promoted into a Thailand manifest.

## Wave 2B tranche 1 candidate set

Research-clean manifest drafts now available:

1. BYD M6 Extended 7 Seats
2. Hyundai STARIA Premium MY25
3. Toyota Yaris Cross HEV Premium Luxury
4. Honda HR-V e:HEV RS
5. Toyota Camry HEV Premium Luxury
6. Porsche 911 Carrera GTS 992 II — Thailand-delivered 2025
7. Lamborghini Revuelto — Thailand launch 2023

Static draft totals:

- mainstream: 66 normalized values + 24 assessments;
- supercar: 20 normalized values + 12 assessments;
- **total: 86 normalized values + 36 explicit assessments**.

DENZA D9 Performance AWD, Ferrari 296 GTB and McLaren Artura Coupe remain research-active and are not forced into tranche 1.
