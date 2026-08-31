# Phase 1 Wave 1 Manifest Tranche 2 QA

Date: 2026-08-31

## Verdict

**PASS — six additional Wave 1 manifests pass pre-import curation QA.**

Included:
- Mazda MX-5 35th Anniversary Edition 2.0 RF AT
- Toyota Fortuner 2.4 Leader V 4WD
- Toyota bZ4X FWD
- BMW 520d M Sport Pro G60
- BMW 740d M Sport G70 current 03/2026
- Isuzu MU-X 2.2 Ddi ULTIMATE A/T 4WD

## Machine QA

- 6 unique manifest record IDs and stable vehicle codes
- no incompatible source-code metadata reuse
- all source/observation/value/load/fitment references resolve
- all parameter codes exist in the accepted registry
- all NUMBER/TEXT primitives match registry types
- all required semantic attributes present
- no direct DERIVED/ESTIMATED values
- exact Identity Time Basis validation passes
- Mazda longitudinal geometry delta = 0 mm

## Important conservative decisions

### Mazda
Uses EDITION_RELEASE from Mazda Thailand's uniquely named 35th Anniversary launch. No MY2025 is inferred.

### Toyota Fortuner / bZ4X
Uses exact Thai OEM revision labels from Toyota Accessories. Buddhist-calendar revision year is not converted to model year.

### BMW 520d
Uses OEM_REVISION_LABEL based on the exact BMW Thailand specification effective 24 March 2025. Exact BMW PDF page was visually verified.

### BMW 740d current 03/2026
The current source version label is the identity discriminator. 2025 wheel/tyre fitment is deliberately not copied to the current 2026 revision because unchanged applicability is unproven.

Current Integral Active Steering is preserved as a raw source observation. A structured steering-relation row is deferred until the importer manifest implementation shape has passed Issue #15 sentinel proof; no kinematics are guessed.

### Isuzu MU-X
Uses the original official 2026 brochure table after visual re-review of the exact 2.2 Ultimate A/T 4x4 column.

## Gate

These manifests remain blocked from physical import until Issue #15 sentinel proof passes.
