# Phase 1 Wave 2 Closure v2

Date: 2026-08-31
Branch: `chatgpt/phase-1-wave2-closure-v2`

## Verdict

**Wave 2 review is complete.**

Final research-readiness partition after reviewing all eight remaining Wave 2 records:

- Wave 1 research-clean candidates: **21**
- Wave 2: **0**
- HOLD: **9**

This classification concerns identity/provenance/semantic readiness for controlled ingestion only.
It does not mean AVT_READY or physical ramp readiness.
Physical Wave 1 ingestion remains blocked until Issue #15 passes the three-sentinel clean-database proof.

## Promoted to Wave 1

### 1. Isuzu MU-X 2.2 Ddi MAXFORCE ULTIMATE A/T 4WD

Identity Time Basis: `EDITION_RELEASE`

Official Isuzu Thailand evidence:
- 27 February 2026 launch explicitly introduces MU-X 4WD with the 2.2 Ddi MAXFORCE in RS and Ultimate;
- official 2026 brochure original technical table was visually reviewed;
- the `2.2 Ultimate A/T 4x4` column is directly visible and no longer depends on parser row-order inference.

Exact target engineering observations include:
- 4,860 x 1,870 x 1,875 mm;
- wheelbase 2,855 mm;
- front/rear OEM track 1,570 / 1,570 mm;
- 235 mm clearance at the rear axle housing;
- 20 x 7.5J / 265/50R20;
- minimum turning radius 5.6 m.

Track and turning reference semantics remain OEM-unspecified where the source does not define them.

### 2. Honda Civic e:HEV RS — 23 July 2026 release

Identity Time Basis: `EDITION_RELEASE`

Evidence strategy:
- Honda Thailand launch = exact identity/release evidence;
- Honda Thailand specification table = primary OEM grouped raw engineering evidence;
- current exact RS secondary page = B-level exact-grade column-resolution evidence.

The secondary source independently identifies RS values matching one member of the OEM grouped sets, including:
- kerb mass 1,429 kg;
- front/rear tread 1,537 / 1,576 mm;
- 18-inch / 235/40 ZR18;
- turning radius 5.7 m.

These mappings remain `REPUTABLE_SECONDARY` evidence. They must not be relabelled as OEM-published exact-column observations.

The RS steering-wheel lock-to-lock value remains held because the reviewed exact-grade secondary source does not resolve the OEM 2.29 / 2.2 grouped values.

### 3. Honda Accord e:HEV RS — 22 August 2025 release

Identity Time Basis: `EDITION_RELEASE`

Evidence strategy:
- Honda Thailand 22 August 2025 launch = exact new-product identity;
- Honda Thailand 2026 campaign = current continuity evidence for New Accord e:HEV;
- Honda Thailand specification = primary grouped raw engineering evidence;
- current exact RS secondary page = B-level exact-grade mapping.

Resolved RS values include:
- kerb mass 1,606 kg;
- wheelbase 2,827 mm;
- front/rear tread 1,590 / 1,624 mm;
- 18-inch / 235/45 R18;
- turning radius 6.1 m.

Again, grade-specific mappings sourced from the secondary page remain B-level evidence.

### 4. MG IM6 Long Range — 22 August 2025 release

Identity Time Basis: `EDITION_RELEASE`

Current MG Thailand technical table directly identifies the `MG IM6 Long Range` column and supplies OEM engineering values.

No dated MG Thailand primary release page was recovered in this review. The launch date is therefore supported by multiple reputable Thai automotive publications reproducing the MG Sales Thailand announcement.

Temporal identity evidence is explicitly graded `REPUTABLE_SECONDARY`; engineering parameters remain OEM Thailand evidence.

Current OEM Long Range technical fingerprint includes:
- 4,904 x 1,988 x 1,669 mm;
- wheelbase 2,950 mm;
- ground clearance 166 mm;
- 20-inch wheels, front 235/50 R20 and rear 255/45 R20;
- minimum turning radius 5.1 m;
- Intelligent Four-wheel Steering System with Crab Mode.

Rear-steering system presence does not make the record AVT-ready because maximum rear angle, phase/speed behaviour, and front-to-rear relation remain unknown.

## Moved to HOLD after completed second review

### Honda City e:HEV RS — 2026 release

Exact release identity is strong, but the current OEM table still presents several multi-valued rows without preserved exact RS association in extracted form.

Secondary exact-grade sources reviewed during closure are inconsistent, including an overall-length disagreement, so they are not strong enough to close the mapping.

Next action:
obtain the original Honda table export/image or another reliable exact-grade technical source that preserves RS column association.

### Ford Everest Platinum 3.0L V6 4WD

Current 2026 Platinum identity and powertrain/21-inch fitment are strongly supported by Ford Thailand.

However, exact current engineering geometry is not cleanly closed:
- the June 2025 exact Platinum technical brochure provides a coherent exact 3.0L V6 table;
- another Ford Thailand Everest product source reports a 226 mm clearance while the exact brochure reports 227 mm;
- exact applicability of the 226 mm value to the same Platinum configuration is not established;
- the 2025 engineering sheet therefore must not be silently reused as current 2026 geometry.

Next action:
obtain an exact current 2026 technical sheet/drawing and resolve the official clearance applicability.

### Mercedes-Benz E 350 e AMG Dynamic W214 — current Thailand

The current exact grade is clearly present in Mercedes-Benz Thailand.

Blockers remain:
- Thailand raw width label is semantically suspect relative to OEM W214 family mirror-open geometry;
- historical Launch Edition / MY2024 secondary evidence does not establish the exact current 2026 revision;
- equipment revisions are known to occur under the same grade name.

Next action:
resolve current Thailand temporal revision and width-envelope semantics using exact OEM technical/owner documentation.

### Mercedes-Maybach S 580 e Premium Z223 — current Thailand

The current exact grade exists, but:
- the Thailand `Width (with mirrors)` label remains inconsistent with OEM Z223 family mirror/body semantics;
- MY2025 secondary evidence does not prove unchanged current 2026 applicability.

Next action:
resolve current temporal applicability and exact width-envelope semantics from OEM technical/owner documentation.

## Closure principle

Second review is not an endless queue.

If the same evidence has been reviewed and the remaining blocker requires a new source, temporal split, or semantic clarification, the record moves to HOLD rather than staying indefinitely in Wave 2.

Unknown/HOLD is an acceptable engineering result. Unsupported completion is not.
