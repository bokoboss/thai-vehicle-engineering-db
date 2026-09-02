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


# Wave 2B Tranche 2 — research / curation QA

Baseline accepted release for this tranche: `release_2026_09_b` — **34 configurations**.

Tranche 2 extends premium-MPV and supercar / high-performance engineering envelopes. This section records research-clean manifest drafts only. It does not publish a new accepted release.

## DENZA D9 Performance AWD — Thailand launch 1 November 2024

Research state: **MANIFEST DRAFT READY**

Identity basis: `EDITION_RELEASE`.

The prior source gap is resolved. DENZA Thailand / Rêver provides an official Thailand launch source and an official Thailand D9 e-catalog with an exact `Performance AWD` specification column.

Normalized draft values:

- overall length: 5,250 mm;
- reported width: 1,960 mm, `OEM_UNSPECIFIED` envelope;
- height: 1,920 mm;
- wheelbase: 3,110 mm;
- OEM front/rear wheel track: 1,675 / 1,675 mm;
- kerb mass: 2,865 kg;
- gross vehicle weight: 3,439 kg;
- clearance: 155 mm unladen;
- clearance: 140 mm maximum loaded;
- minimum turning radius: 5.95 m, reference/axle scope `OEM_UNSPECIFIED`;
- front/rear wheel: 18-inch low-wind-resistance alloy;
- front/rear tyre: 235/60 R18.

Generic width is not promoted to body or mirrors-open width. OEM track remains non-AVT.

Manifest:

`data/curation/manifests/wave2b/denza_d9_performance_awd_launch_20241101_v1.json`

Static contract: **PASS — 15 values + 4 assessments**.

## Ferrari 296 GTB — Thailand Premiere April 2022

Research state: **MANIFEST DRAFT READY**

Identity basis: `EDITION_RELEASE`.

Cavallino Motors' official Ferrari Thailand channel documents the Thailand Premiere. Ferrari's official technical sheet and the exact Thailand launch specification agree on structural geometry, track, dry-weight wording and wheel/tyre sizes.

Global OEM structural values are therefore normalized with `SAME_GEOMETRY_CONFIRMED` applicability:

- length: 4,565 mm;
- reported width: 1,958 mm, envelope `OEM_UNSPECIFIED`;
- height: 1,187 mm;
- wheelbase: 2,600 mm;
- OEM track front/rear: 1,665 / 1,632 mm;
- front wheel/tyre: J9.0 x 20 / 245/35 ZR20;
- rear wheel/tyre: J11.0 x 20 / 305/35 ZR20.

Ferrari's published 1,470 kg is explicitly **Dry Weight** with optional lightweight content. It remains raw evidence and is not normalized as kerb mass.

Body/mirror width, ground clearance, turning and AVT outer-face tracks remain unresolved.

Manifest:

`data/curation/manifests/wave2b/ferrari_296_gtb_thailand_premiere_202204_v1.json`

Static contract: **PASS — 10 values + 7 assessments**.

## McLaren Artura Coupe — Thailand launch 19 December 2022

Research state: **MANIFEST DRAFT READY — CONSERVATIVE**

Identity basis: `EDITION_RELEASE`.

Thailand launch evidence identifies a CBU Artura imported by Niche Cars Group and publishes:

- length: 4,539 mm;
- reported width: 1,913 mm;
- height: 1,193 mm;
- wheelbase: 2,640 mm;
- raw vehicle weight: 1,498 kg.

The four Thailand dimensions are normalized at authority grade B because exact local first-party technical geometry was not recovered.

McLaren OEM material explicitly identifies **DIN Kerb Weight = 1,498 kg**. Because the value matches the Thailand launch raw weight, kerb mass is normalized at A1 with `SAME_GEOMETRY_CONFIRMED` applicability.

A McLaren Qualified model-family listing also publishes `Vehicle Width = 2,080 mm`, but does not establish the envelope definition and is not exact Thailand applicability. That 2,080 mm value is retained only as a raw ambiguity observation.

Therefore:

- 1,913 mm remains `overall_width_reported_mm` with `OEM_UNSPECIFIED`;
- no body-width value is created;
- no mirrors-open value is created.

Turning, ground clearance and AVT outer-face tracks remain unresolved.

Manifest:

`data/curation/manifests/wave2b/mclaren_artura_coupe_launch_20221219_v1.json`

Static contract: **PASS — 5 values + 6 assessments**.

## Lamborghini Urus SE — Thailand launch May 2024

Research state: **MANIFEST DRAFT READY**

Identity basis: `EDITION_RELEASE`.

Thailand launch dimensions and the exact Thailand standard 21-inch wheel/tyre package match Lamborghini's official Urus SE technical brochure. Global OEM structural values are normalized with `SAME_GEOMETRY_CONFIRMED` applicability.

Normalized:

- length: 5,123 mm;
- body width excluding mirrors: 2,022 mm;
- width including mirrors: 2,181 mm;
- height: 1,638 mm;
- wheelbase: 3,003 mm;
- front/rear overhang: 1,067 / 1,053 mm;
- OEM front/rear track: 1,695 / 1,710 mm;
- front wheel/tyre: 9.5J x 21 ET28 / 285/45 ZR21;
- rear wheel/tyre: 10.5J x 21 ET18 / 315/40 ZR21.

Lamborghini documents air-suspension vehicle-height adjustment and rear-wheel steering. Those are retained as raw observations only. No ground clearance, lift amount, turning value, steering relation or ramp angle is inferred.

Manifest:

`data/curation/manifests/wave2b/lamborghini_urus_se_th_launch_20240522_v1.json`

Static contract: **PASS — 13 values + 5 assessments**.

## Ferrari Purosangue — Thailand / Southeast Asia Premiere April 2023

Research state: **MANIFEST DRAFT READY**

Identity basis: `EDITION_RELEASE`.

Cavallino Motors' Thailand/Southeast Asia premiere evidence and Thailand launch dimensions match Ferrari's official technical specification. Global OEM structural values are therefore normalized with `SAME_GEOMETRY_CONFIRMED` applicability.

Normalized:

- length: 4,973 mm;
- reported width: 2,028 mm, envelope `OEM_UNSPECIFIED`;
- height: 1,589 mm;
- wheelbase: 3,018 mm;
- OEM front/rear track: 1,737 / 1,720 mm;
- front wheel/tyre: J9.0 x 22 / 255/35 R22;
- rear wheel/tyre: J11.0 x 23 / 315/30 R23.

Ferrari's 2,033 kg value is explicitly **Dry Weight** with optional lightweight content. It remains raw evidence only and is not normalized as kerb mass.

Four-wheel-steering/model behaviour does not create a steering relation without direct geometry. Ground clearance, turning value, body/mirror width and AVT outer-face tracks remain unresolved.

Manifest:

`data/curation/manifests/wave2b/ferrari_purosangue_th_premiere_20230407_v1.json`

Static contract: **PASS — 10 values + 7 assessments**.

## Tranche 2 draft summary

Five research-clean manifest drafts:

1. DENZA D9 Performance AWD
2. Ferrari 296 GTB
3. McLaren Artura Coupe
4. Lamborghini Urus SE
5. Ferrari Purosangue

Static total:

- **53 normalized values**
- **29 explicit assessments**

Proposed controlled staging progression after importer qualification:

`34 accepted configurations -> 39 staging configurations`

No `current_release.json` change, accepted DB promotion, or application-source change is part of this research tranche.

Permanent tranche-2 invariants:

- DENZA D9 155/140 mm clearance remains load-scoped.
- Ferrari dry weights are not kerb masses.
- McLaren 1,913 vs 2,080 mm width ambiguity remains fail-closed.
- Urus SE body/mirrors widths remain distinct 2,022 / 2,181 mm.
- Air suspension and rear-wheel/four-wheel steering observations do not create unsupported clearance, ramp or steering geometry.
- OEM tread/track never becomes AVT outer-face track by implication.
