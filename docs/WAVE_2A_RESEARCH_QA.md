# Wave 2A Research and Curation QA

Status: Active research gate  
Date: 2026-09-01  
Issue: #32 — Wave 2A engineering-use vehicle data expansion

## 1. Objective

Expand the accepted 21-vehicle curated baseline with high-value Thai-market vehicles that materially improve parking, access, porte-cochère, vehicle comparison, and Design Check coverage.

The expansion remains evidence-first. A target is not promoted merely because it is useful or popular.

## 2. Policy

Wave 2A follows the existing Vehicle Data Standard and Source Curation Protocol.

Key rules:

- exact Thai-market configuration first;
- temporal identity must be explicit;
- raw source observation before normalization;
- generic width does not become body width or mirror width;
- OEM tread/track does not become AVT outer-face track;
- OEM turning radius without curb/wall semantics remains OEM_UNSPECIFIED;
- ground-clearance load/reference state remains explicit when unstated;
- approximate or generically labelled vehicle weight is not silently promoted to kerb mass;
- grade-column mapping must be independently verified where a manufacturer table contains several values;
- unresolved targets remain HOLD.

## 3. Initial target set

1. Kia Carnival HEV 7-seat Luxury
2. Nissan Serena e-POWER Highway Star
3. Honda CR-V e:HEV RS 4WD — late-2025 minor-change
4. Lexus LM 350h Executive 7-Seater
5. Toyota Innova Zenix HEV Premium
6. Toyota Corolla Cross HEV Premium Luxury

## 4. Research-clean manifest candidates

### 4.1 Kia Carnival HEV 7-seat Luxury

Research state: **MANIFEST DRAFT READY**

Identity evidence:

- Kia Sales (Thailand) launch release states that The new Kia Carnival HEV 7-seater was officially launched in Thailand on 3 October 2025.
- The same release explicitly lists two variants: 7-seat Luxury and 7-seat Premium.
- Official August 2026 Kia promotion confirms both grades remain offered in Thailand.

Sources:

- Launch release:  
  https://www.kia.com/th/en/util/news/the-new-kia-carnival-hev-7-seater-launch.html
- Current technical specification:  
  https://www.kia.com/th/en/cars/carnival-hev/specification.html
- 2026 continuity evidence:  
  https://www.kia.com/th/en/util/promotion/thekiacarnival-hev-2026.html

Official technical values published for the HEV 7-seat Premium / Luxury table:

| Parameter | Source value | Normalization position |
|---|---:|---|
| Overall length | 5,155 mm | safe basic geometry |
| Overall width | 1,995 mm | reported width only; mirror/body semantics not stated |
| Overall height | 1,785 mm | safe basic geometry |
| Wheelbase | 3,090 mm | safe basic geometry |
| Front/rear tread | 1,739 / 1,738 mm | OEM tread/track only |
| Front/rear overhang | 935 / 1,130 mm | safe longitudinal geometry |
| Minimum ground clearance | 172 mm | OEM minimum unspecified; load state unstated |
| Tyre | 235/55 R19 | exact HEV 7-seat fitment |
| Wheel | 19-inch alloy | exact HEV 7-seat fitment |

Turning:

- No defensible turning value was located in the reviewed Kia Thailand launch/specification/continuity sources.
- Record an assessment rather than infer from another market.

AVT:

- OEM tread values are not AVT outer-face track.

### 4.2 Nissan Serena e-POWER Highway Star

Research state: **MANIFEST DRAFT READY**

Identity evidence:

- Nissan Motor Thailand launched the All-New Nissan Serena e-POWER in Thailand on 24 March 2025.
- Official launch release states that the Thailand vehicle is offered in one grade: Highway Star.
- Current Nissan Thailand specification page continues to identify Highway Star.

Sources:

- Launch release:  
  https://en.nissan.co.th/news/nissan-launches-all-new-serena-epower-mid-size-mpv.html
- Current technical specification:  
  https://www.nissan.co.th/vehicles/new-vehicles/serena-epower/specifications.html

Official technical values:

| Parameter | Source value | Normalization position |
|---|---:|---|
| Overall length | 4,765 mm | safe basic geometry |
| Overall width | 1,715 mm | reported width only; mirror/body semantics not stated |
| Overall height | 1,870 mm | safe basic geometry |
| Wheelbase | 2,870 mm | safe basic geometry |
| Ground clearance | 135 mm | OEM minimum unspecified; load state unstated |
| Minimum turning radius | 5.7 m | normalized radius with reference = OEM_UNSPECIFIED |
| Wheel | 16 x 6J alloy | exact Highway Star |
| Tyre | 205/65 R16 | exact Highway Star |
| Approximate vehicle weight | 1,797 kg | retain as raw observation; do not promote to kerb mass without definition |

Turning:

- Nissan labels the value as minimum turning radius.
- Curb/wall reference and axle scope are not stated on the reviewed Thailand specification page.
- Store radius semantics only; reference and axle scope remain OEM_UNSPECIFIED.

### 4.3 Honda CR-V e:HEV RS 4WD — late-2025 minor-change

Research state: **MANIFEST DRAFT READY WITH EXPLICIT HEIGHT / MASS GAPS**

Identity evidence is strong:

- Honda Thailand introduced the new/minor-change CR-V e:HEV line-up in November 2025.
- Official launch material explicitly retains e:HEV RS 4WD as an exact grade.

Sources:

- Pre-booking/revision release:  
  https://www.honda.co.th/news/NewCRVeHEV_Prebooking
- Official Motor Expo 2025 line-up announcement:  
  https://www.honda.co.th/en/news/Motorexpo2025
- Current specification page:  
  https://www.honda.co.th/crv/specification

The official current specification and late-2025 catalogue together provide a five-grade header: e:HEV E, e:HEV ES, e:HEV HuNT, e:HEV RS and e:HEV RS 4WD.

Rows with sufficiently explicit grouping for the exact RS 4WD configuration are normalized:

- length 4,691 mm;
- reported width 1,866 mm;
- wheelbase 2,700 mm;
- front/rear OEM tread 1,612 / 1,638 mm (last three grades);
- minimum ground clearance 208 mm (last three grades; load/reference state unstated);
- 19 x 7.5J wheels and 235/55 R19 tyres (last two RS grades);
- steering-wheel lock-to-lock 2.4 turns;
- turning radius 5.5 m with curb/wall and axle scope unresolved;
- exact RS 4WD drivetrain is Real Time AWD from the official minor-change release.

Two values remain deliberately unnormalized:

- **height**: Honda publishes 1,681 / 1,691 mm, but the flattened first-party extraction did not preserve a sufficiently robust exact member association for this pass;
- **mass**: the five-grade table places 1,815 kg in the RS 4WD column, but Honda labels the row only as “น้ำหนักรถ”; the manifest retains the raw observation but does not silently promote it to `kerb_mass_kg`.

This conservative treatment avoids repeating the previous Honda City grade-column failure mode while still adding the exact clean parameters.

## 5. Active research targets

### Lexus LM 350h Executive 7-Seater

Research state: **MANIFEST DRAFT READY**

Temporal identity and engineering continuity are now supported by multiple official Lexus Thailand sources:

- 2023 official price list is headed “THE ALL-NEW LEXUS LM”, lists exact LM 350h Executive 7-Seater, and states price/finance information as of 30 August 2566;
- 2023 official catalogue has a dedicated LM350h Executive 7-Seater specification column;
- 2025 catalogue repeats the same core geometry/mass/turning values and its specification page was visually verified;
- current Lexus Thailand model page continues to list LM 350h 7-seater and repeats the same engineering values.

Exact values:

- length 5,125 mm;
- reported width 1,890 mm;
- height 1,940 mm;
- wheelbase 3,000 mm;
- front/rear tread 1,615 / 1,620 mm;
- curb weight 2,345 kg;
- gross vehicle weight 2,880 kg;
- minimum turning radius (Tire) 5.9 m;
- E-Four;
- tyre 225/55 R19;
- 19-inch forged aluminum wheel evidence from the later same-geometry catalogue.

Identity basis: `EDITION_RELEASE`, raw label “THE ALL-NEW LEXUS LM — LM 350h Executive 7-Seater, official Thailand 2023 release configuration”.

Semantic limits: overall width remains OEM_UNSPECIFIED for mirror/body envelope; tread is not AVT outer-face track; the turning reference is retained as tire/wheel-path rather than curb-to-curb or wall-to-wall, with axle scope unresolved.

Sources:

https://www.lexus.co.th/content/dam/thailand/website-v3/price-list/Lexus%20LM_Pricelist_2023.pdf

https://www.lexus.co.th/content/dam/thailand/website-v3/borchures/catalog/2023/Catalog_2023Lexus_lm.pdf

https://www.lexus.co.th/content/dam/thailand/website-v3/borchures/catalog/2025/Lexus_LM_Catalog_Thai_2025_LM.pdf

https://www.lexus.co.th/en/models/lm/lm-350h-7-seater.html

### Toyota Innova Zenix HEV Premium

Research state: **MANIFEST DRAFT READY**

Official Toyota Thailand evidence now closes both exact grade mapping and temporal identity:

- current grade page lists exactly HEV Premium and HEV Smart and confirms current 2026 sale continuity;
- official accessories material explicitly identifies “โตโยต้า อินโนว่า ซีนิกซ์ รุ่นปรับปรุงใหม่ ปี 2568” and the HEV Premium / HEV Smart applicability columns;
- the official 2025 catalogue specification page was visually checked and clearly separates HEV Premium from HEV Smart.

HEV Premium specification:

- length 4,799 mm;
- reported width 1,850 mm;
- height 1,790 mm;
- wheelbase 2,850 mm;
- front/rear tread 1,550 / 1,571 mm;
- minimum ground clearance 160 mm;
- minimum turning radius 5.7 m;
- FWD;
- 18-inch alloy / 225/50 R18;
- seven seats.

Sources:

https://www.toyota.co.th/model/innovazenix/grade

https://www.toyota.co.th/media/accessories/files/brochure/68b95caa9a7be.pdf

https://www.toyota.co.th/media/product/series/download/INNOVA_ZENIX_CATALOG2025.pdf

Identity basis: `OEM_REVISION_LABEL`, raw label “โตโยต้า อินโนว่า ซีนิกซ์ รุ่นปรับปรุงใหม่ ปี 2568”. The Buddhist-calendar revision year is not converted to model year.

Semantic limits remain fail-closed: generic width is OEM_UNSPECIFIED, tread is not AVT outer-face track, ground-clearance load/reference state is unstated, and the 5.7 m turning radius has OEM_UNSPECIFIED curb/wall and axle scope.

### Toyota Corolla Cross HEV Premium Luxury

Research state: **MANIFEST DRAFT READY**

Official Toyota Thailand evidence closes temporal identity and exact current grade:

- accessories material identifies “โตโยต้า โคโรลล่า ครอส รุ่นปรับปรุงใหม่ ปี 2569” and includes HEV Premium Luxury applicability;
- the current grade page lists HEV Premium Luxury as an active grade;
- the current 2026 catalogue provides the four-grade engineering table and supports exact/current Premium Luxury mapping.

Normalized current values:

- length 4,460 mm;
- reported width 1,825 mm;
- height 1,620 mm;
- wheelbase 2,640 mm;
- front/rear OEM tread 1,559 / 1,571 mm;
- minimum ground clearance 161 mm;
- minimum turning radius 5.2 m;
- 18-inch alloy / 225/50 R18.

Identity basis: `OEM_REVISION_LABEL`, raw label “โตโยต้า โคโรลล่า ครอส รุ่นปรับปรุงใหม่ ปี 2569”. The Buddhist-calendar revision year is not converted to model year.

Semantic limits remain fail-closed: generic width is OEM_UNSPECIFIED, tread is not AVT outer-face track, ground-clearance load/reference state is unstated, and the 5.2 m turning radius remains OEM_UNSPECIFIED for curb/wall and axle scope.

Sources:

https://www.toyota.co.th/media/accessories/files/brochure/69a000dce2330.pdf

https://www.toyota.co.th/model/corollacross/grade

https://www.toyota.co.th/media/product/series/download/CorollaCross_Catalog_2026.pdf

## 6. Current Wave 2A partition

### Manifest draft ready

- Kia Carnival HEV 7-seat Luxury
- Nissan Serena e-POWER Highway Star
- Toyota Innova Zenix HEV Premium
- Lexus LM 350h Executive 7-Seater
- Honda CR-V e:HEV RS 4WD
- Toyota Corolla Cross HEV Premium Luxury

### Research active

- None in the initial Wave 2A six-vehicle set

### Existing HOLD records

The nine Phase 1 HOLD records remain unchanged. Wave 2A does not reinterpret or reopen them without genuinely new evidence.

## 7. Next QA gate

Before any Wave 2A physical ingestion:

1. validate each draft manifest with the existing create-only importer;
2. run independent semantic review;
3. confirm no source-code collision or incompatible reuse;
4. confirm exact identity-time basis;
5. verify Design Check-facing width/turning semantics remain fail-closed;
6. import only reviewed Wave 2A manifests into a staging database;
7. update curated inventory only after acceptance.
