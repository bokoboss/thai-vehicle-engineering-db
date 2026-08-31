# Phase 1 Wave 2 Second Review v1

Date: 2026-08-31
Branch: `chatgpt/phase-1-wave2-second-review-v1`

## Verdict

**3 records promoted to Wave 1. 8 remain in Wave 2. HOLD remains 5.**

New research/ingestion-readiness partition:

- Wave 1 clean candidates: **17**
- Wave 2 second review: **8**
- HOLD: **5**

Wave 1 still means research/identity/semantic readiness only. It does not mean AVT_READY or physical ramp readiness.

Physical import remains blocked until Issue #15 passes the three-sentinel clean-DB proof.

## Promoted

### Mazda MX-5 35th Anniversary Edition 2.0 RF AT

Decision: **PROMOTE TO WAVE 1**

Identity Time Basis: `EDITION_RELEASE`

Raw identity label: `New Mazda MX-5 35th Anniversary Edition`

Why:
- Mazda Thailand officially launched the uniquely named limited 35th Anniversary Edition on 17 March 2025;
- the official exact product/specification page identifies the edition and engineering specification;
- model year does not need to be invented.

### Toyota Fortuner 2.4 Leader V 4WD

Decision: **PROMOTE TO WAVE 1**

Identity Time Basis: `OEM_REVISION_LABEL`

Raw identity label: `FORTUNER รุ่นปรับปรุงปี 2568`

Why:
- Toyota's official accessory/download index explicitly uses that revision label;
- the exact 2.4 Leader V 4WD grade is present in the current five-grade line-up;
- the previously reviewed official 2025 Fortuner Leader technical catalog supports the engineering geometry;
- the Thai revision label remains raw and is not converted to MY2025.

### New BYD DOLPHIN Extended Range (Local Production)

Decision: **PROMOTE TO WAVE 1**

Identity Time Basis: `SALE_PERIOD`

Bounded proof interval: `2026-03-01` to `2026-04-05`

Why:
- official REVER campaign terms explicitly identify New BYD DOLPHIN Extended Range (Local Production);
- the campaign provides a bounded applicability interval;
- official technical page supplies the exact Extended Range engineering data;
- no model-year inference is required.

## Remain Wave 2

### MG IM6 Long Range

Official current source ecosystem now also uses `Premium Long Range`.

The relationship between the research target `Long Range` and current `Premium Long Range` terminology must be reconciled before exact promotion.

### Honda City e:HEV RS

Identity/release is strong, but extracted multi-valued dimension/fitment rows still do not preserve exact RS column association.

### Honda Civic e:HEV RS

Official current page confirms e:HEV RS and publishes the multi-valued steering/turning/tread/wheel rows, but exact RS assignment remains insufficiently preserved in machine-readable extraction.

Do not infer the column from row order.

### Honda Accord e:HEV RS

Exact release identity is strong; wheelbase/tread/wheel multi-column association remains unresolved.

### Isuzu MU-X 2.2 Ddi ULTIMATE 4WD

Identity is now strong:

- official 27 February 2026 launch;
- explicit 2.2 Ddi MAXFORCE 4WD in ULTIMATE;
- official 2026 brochure visually reviewed.

However, the technical page's exact grade-column geometry/clearance/wheel association is not yet recorded with sufficient confidence for clean ingestion. Keep fail-closed.

### Ford Everest Platinum 3.0 V6 4WD

Official June 2025 PDF parsed text clearly exposes the exact model column and technical values.

However, screenshot verification repeatedly failed with a PDF cache miss during this review pass.

The established decisive-PDF visual-verification rule is therefore preserved.

### Mercedes-Benz E 350 e AMG Dynamic

The Thailand raw width label remains semantically suspect against Mercedes' own W214 family mirror-envelope semantics.

Keep for dedicated applicability review.

### Mercedes-Maybach S 580 e Premium

The Thailand raw width label remains semantically suspect; same-geometry Z223 cross-market dimensional applicability still requires explicit review.

## Research rules reaffirmed

1. Identity-time evidence can resolve a record without model year.
2. Grade-name changes are not silently treated as synonyms.
3. Parsed tables do not prove grade-column association.
4. Failed visual verification is a real blocker when PDF visual review is part of the acceptance rule.
5. High-authority source labels can still be semantically suspicious.
