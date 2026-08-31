# Pilot Dataset and Acceptance Gates v1.0

Status: Foundation candidate after Deep Research amendment  
Date: 2026-08-30

## 1. Purpose

Prove the evidence model, vehicle-identity contract, AVT semantics and future ramp-data extensibility with a deliberately difficult cross-section of Thai-market vehicles before scaling the catalog.

The pilot is a **schema/evidence stress test**, not a completeness contest.

## 2. Pilot principle

The first curation pass must not attempt to make every vehicle AVT-ready or ramp-ready.

Success is the database being able to represent, explain and preserve why some records are ready and others are not.

## 3. Recommended pilot set

Use approximately 30 exact Thai-market configurations/targets, with exact temporal applicability (model year **or another approved OEM identity-time basis**), sales grade and material wheel package locked at ingestion:

1. Honda City e:HEV RS
2. Honda Civic e:HEV RS
3. Honda Accord e:HEV RS
4. Toyota Yaris ATIV current premium-grade target
5. Toyota Fortuner 2.4 Leader V 4WD
6. Toyota Alphard 2.5 HEV fourth-generation Thai-market target
7. Toyota Commuter 2.8 AT H300
8. Toyota bZ4X FWD
9. Isuzu D-Max V-Cross 2.2 Z 4-door AT 4x4
10. Isuzu MU-X 2.2 ULTIMATE
11. Ford Ranger Wildtrak 2.0 Bi-Turbo 4x4
12. Ford Everest Platinum 3.0 V6 4WD
13. Mitsubishi Triton Double Cab Ultra 4WD
14. Nissan Navara Double Cab PRO-4X
15. Mazda MX-5 2.0 exact transmission locked at curation
16. Suzuki Swift GLX/current equivalent
17. BYD Dolphin Extended Range
18. BYD ATTO 3 Extended
19. BYD Seal AWD Performance
20. GWM ORA 07 Performance
21. MG IM6 current Thai four-wheel-steering grade
22. Tesla Model 3 current Long Range target
23. Tesla Model Y current five-seat Long Range target
24. Kia EV5 Earth Long Range
25. Hyundai IONIQ 6 current long-range target
26. Volvo EX30 current Thai configuration
27. Mercedes-Benz E 350 e AMG Dynamic W214
28. Mercedes-Maybach S 580 e Z223
29. BMW 520d M Sport Pro G60
30. BMW 740d M Sport G70

The exact configuration is not created until the curation record resolves market, generation/chassis, material variant/wheel/equipment package and an evidence-backed temporal discriminator. Do not invent a model year when the OEM identifies the configuration through a revision label, named edition/release or bounded sale period instead.

## 4. Why this set is deliberately difficult

Collectively it exercises:

- ordinary Thai passenger-car data with incomplete semantics;
- variant-dependent track/turning values;
- body-on-frame SUV/pickup clearance semantics;
- large MPV/van body geometry;
- EV loaded/unloaded clearance;
- low-clearance EV underfloor battery relevance;
- explicit kerb-to-kerb turning data;
- option-dependent rear steering;
- four-wheel steering;
- mirror-open/folded/body width semantics;
- direct published overhang;
- unusually long wheelbase/luxury body envelopes;
- strong and weak OEM source ecosystems.

## 5. Pilot research workflow

For each candidate:

1. Resolve exact Thai-market identity.
2. Capture Thai OEM primary source first where available.
3. Search OEM technical/service/homologation/body-builder sources for missing engineering geometry.
4. Preserve every useful raw observation.
5. Normalize only when semantics are adequate.
6. Run deterministic QA.
7. Record unresolved parameters as assessments, not invented values.
8. Determine readiness by use case.
9. Independently review a sample of high-risk fields.

## 6. Minimum evidence expectations

Every pilot vehicle:

- exact identity evidence;
- overall L/W/H where published;
- wheelbase where published;
- tyre/wheel configuration where published;
- at least one primary or strongest-available source;
- parameter-level provenance;
- explicit unknown/conflict assessments for missing high-value fields.

Across the pilot:

- at least 10 vehicles with turning observations sufficient to exercise turning semantics;
- at least 5 with overhang evidence or stronger longitudinal body geometry;
- at least 5 with structured clearance/load-state evidence;
- at least 3 with useful drawing/geometry assets;
- at least 1 four-wheel/rear-steering case;
- at least 1 explicit kerb/curb-to-curb turning case;
- at least 1 conflicting evidence case;
- at least 1 body/mirror-width multi-envelope case.

## 7. Foundation acceptance gates

### F1 — Identity contract
PASS when exact market/generation/variant/wheel-package differences can be represented without ambiguous merging.

### F2 — Evidence contract
PASS when normalized/derived values trace to raw observations and sources while evidence method, conflict, verification and availability remain orthogonal.

### F3 — Conflict handling
PASS when published + conflicting can coexist and a preferred value requires an auditable decision.

### F4 — AVT turning semantics
PASS when:
- OEM-unspecified turning remains unspecified;
- curb axle scope remains explicit;
- wall body/body+loads envelope scope remains explicit;
- radius/diameter semantics cannot be silently guessed.

### F5 — Steering semantics
PASS when:
- steering-wheel turns;
- actual road-wheel angle;
- virtual-center/AVT Maximum Steering Angle;
- AVT lock-to-lock time; and
- rear/secondary steering behaviour
cannot be implicitly conflated.

### F6 — AVT track semantics
PASS when centerline/tread and outer-face track have distinct parameter codes and nominal section-width approximation alone cannot produce AVT_READY.

### F7 — Clearance/load semantics
PASS when laden between-axles clearance, running/axle/component/battery clearance and OEM-unspecified minimum remain distinguishable and retain load/ride-height applicability.

### F8 — Ramp semantics
PASS when OEM-published, geometry-derived and screening angle parameter codes are distinct and physical geometry-derived results require their declared contact/loaded-tyre/lower-envelope inputs.

### F9 — Geometry assets
PASS when plan body, side silhouette and longitudinal lower envelope are distinguishable and carry datum/fidelity/uncertainty metadata.

### F10 — UI/export honesty
PASS when unknown/conflicting/estimated values are distinguishable from verified facts and exports preserve evidence/status/source identifiers.

## 8. Required Phase 0 deterministic fixtures

1. exact primary published value;
2. OEM turning value with unknown curb/wall semantics;
3. published + conflicting observation state;
4. rejected/screening AVT-track estimate from centerline tread + nominal tyre section width that **fails AVT_READY**;
5. valid AVT outer-face-track fixture from direct evidence or sufficiently explicit mounted geometry;
6. unknown/not-found parameter assessment;
7. measured or image-scaled estimate with uncertainty;
8. steering-wheel turns separate from actual wheel angle and AVT lock-to-lock time;
9. curb-to-curb value with unresolved axle scope;
10. wall-to-wall values distinguished by body/body+loads scope;
11. laden between-axles clearance distinct from generic minimum/axle clearance;
12. structured load condition with tyre pressure/ride-height applicability where relevant;
13. static-loaded tyre radius record;
14. four-wheel/rear-steering fixture;
15. width with unknown mirror semantics that cannot silently populate body width;
16. geometry assets distinguishing side silhouette from longitudinal lower envelope;
17. screening ramp calculation that cannot populate OEM/physical angle fields.

## 9. Phase 0 software acceptance gates

- reproducible relational schema/migrations;
- typed validation for the foundation entities;
- all required deterministic fixtures represented without semantic loss;
- raw observation -> normalized/derived/decision lineage queryable;
- invalid AVT semantic conflations mechanically prevented/tested;
- derivation rules require version + input lineage + validity conditions;
- unknown/estimated/measured/published/conflicting/reviewed dimensions remain independently representable;
- CSV/Excel export preserves value state and evidence/source identifiers;
- unit/contract tests pass;
- CI green;
- local bootstrap/run documented;
- no large source archives committed accidentally;
- architecture remains persistence-portable;
- fresh-context independent semantic review of the first migrations/schema.

## 10. Explicitly deferred

- production catalog population;
- autonomous scraping;
- ramp solver;
- production ATL/ATX writer;
- 3D underbody collision;
- suspension dynamics;
- design-vehicle percentile analysis;
- polished product UI beyond the minimum needed to exercise the domain.

## 11. Pilot completion criterion

The pilot is complete when an engineer can inspect representative records and accurately state, for example:

- a published steering-wheel lock-to-lock value exists but maximum road-wheel lock is unknown;
- laden and unladen clearance exist but detailed ramp interference is unavailable without a lower envelope;
- an explicit kerb-to-kerb radius can be mapped more confidently than an unspecified “minimum turning radius”;
- a four-wheel-steering vehicle cannot be treated as a conventional fixed rear axle;
- OEM tread exists but AVT outer-face track remains unknown;
- body and mirror widths exist but do not create a wall-to-wall turning radius.

These are expected successful outcomes, not data-quality failures.

## 12. Scale-up gate

Do not begin hundreds-of-model bulk population until:

- foundation schema semantics are accepted;
- pilot schema changes stabilize;
- recurring source patterns are identified;
- ingestion helpers create raw observations without bypassing QA;
- conflict/identity/readiness workflows are exercised;
- data-quality metrics are visible.
