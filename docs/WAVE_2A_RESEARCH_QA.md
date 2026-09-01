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

Research state: **ACTIVE — GRADE MAPPING REQUIRED**

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

The current specification page publishes:

- turning radius 5.5 m;
- steering-wheel lock-to-lock 2.4 turns;
- length 4,691 mm;
- width 1,866 mm;
- height values 1,681 / 1,691 mm;
- wheelbase 2,700 mm;
- multiple front/rear tread values;
- ground-clearance values 198 / 208 mm;
- multiple masses;
- 18- and 19-inch wheel/tyre packages.

However, the flattened HTML contains grouped multi-grade values. Exact e:HEV RS 4WD column mapping must be independently verified before normalization. This target must not repeat the previous Honda City grade-column failure mode.

## 5. Active research targets

### Lexus LM 350h Executive 7-Seater

Official Thailand page provides strong exact-grade geometry:

- length 5,125 mm;
- width 1,890 mm;
- height 1,940 mm;
- wheelbase 3,000 mm;
- front/rear tread 1,615 / 1,620 mm;
- body/vehicle mass values published.

Source:
https://www.lexus.co.th/th/models/lm/lm-350h-7-seater.html

A 2024 official brochure identifies LM 350h Executive 7-Seater:
https://www.lexus.co.th/content/dam/thailand/website-v3/borchures/catalog/2024/2024_LM.pdf

Remaining gate: exact Thailand temporal identity/continuity for the current geometry package must be locked before manifest promotion.

### Toyota Innova Zenix HEV Premium

Official 2025 Toyota Thailand catalogue publishes:

- length 4,799 mm for HEV Premium;
- width 1,850 mm;
- height 1,790 mm;
- wheelbase 2,850 mm;
- front/rear tread 1,550 / 1,571 mm;
- minimum ground clearance 160 mm;
- minimum turning radius 5.7 m.

Source:
https://www.toyota.co.th/media/product/series/download/INNOVA_ZENIX_CATALOG2025.pdf

Remaining gate: establish a supported identity-time basis rather than treating the brochure filename/year as model year.

### Toyota Corolla Cross HEV Premium Luxury

Current Toyota Thailand grade page explicitly lists HEV Premium Luxury.

Current 2026 official catalogue provides a dimension drawing including:

- length/overall geometry to be extracted from the technical page;
- overall width 1,825 mm;
- overall height 1,620 mm;
- wheelbase 2,640 mm;
- front/rear tread 1,559 / 1,571 mm.

Sources:

https://www.toyota.co.th/model/corollacross/grade

https://www.toyota.co.th/media/product/series/download/Corolla_Cross_Catalog_2026.pdf

Remaining gates:

- exact temporal identity basis;
- full grade-specific technical table extraction;
- do not assume generic overall width is body width.

## 6. Current Wave 2A partition

### Manifest draft ready

- Kia Carnival HEV 7-seat Luxury
- Nissan Serena e-POWER Highway Star

### Research active

- Honda CR-V e:HEV RS 4WD
- Lexus LM 350h Executive 7-Seater
- Toyota Innova Zenix HEV Premium
- Toyota Corolla Cross HEV Premium Luxury

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
