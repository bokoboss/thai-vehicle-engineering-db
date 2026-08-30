# Product Requirements v1.0

Status: Draft for foundation review  
Date: 2026-08-29

## 1. Product objective

Build a browser-based Thailand Vehicle Engineering Database that allows engineers to find, compare, verify and export vehicle geometry and maneuverability data with traceable evidence.

The product is not a generic automotive-spec catalog. Its primary purpose is engineering use in:

- swept-path and turning analysis;
- parking and access design;
- ramps and vertical-clearance assessment;
- porte-cochère / drop-off / loading-area design;
- design-vehicle selection;
- preparation of custom Autodesk Vehicle Tracking (AVT) vehicle definitions;
- client-facing engineering responses where source traceability matters.

## 2. Primary users

### Traffic / transport engineer
Needs reliable dimensions, turning behavior and vehicle comparison for design and review.

### Architect / parking / infrastructure designer
Needs rapid answers about clearance, ramp suitability and spatial implications.

### Engineering reviewer / QA
Needs to see exactly where each value came from, whether it is published/derived/measured/estimated, and whether the exact vehicle configuration matches the source.

### Data curator
Needs to add/repair records without corrupting existing evidence or losing provenance.

## 3. Core user journeys

### Search and inspect
1. Search by manufacturer, model, generation/chassis, year, variant or vehicle class.
2. Open a vehicle engineering sheet.
3. See geometry, wheel/tyre, steering, turning and vertical-clearance data.
4. See readiness and confidence state for each engineering use case.
5. Drill into parameter-level sources.

### Compare vehicles
Compare two or more vehicle configurations on:
- length / width / height;
- wheelbase and overhang;
- front/rear track;
- turning circle;
- tyre/wheel geometry;
- ground clearance and ramp-related geometry;
- AVT readiness.

### Answer an engineering question
Examples:
- Can this vehicle physically negotiate a proposed ramp?
- Which of these vehicles is more demanding for a porte-cochère?
- Which common Thai-market MPV should be used as a design check?
- Is the OEM “turning radius” definition good enough to use as AVT curb-to-curb input?

The system must make limitations explicit rather than return false certainty.

### Prepare for Autodesk Vehicle Tracking
For an AVT-ready record:
1. Show the normalized AVT input set.
2. Show which fields are directly published vs derived.
3. Show any unresolved assumptions.
4. Export an AVT preparation sheet initially.
5. Later support automated ATL/ATX or other AVT-compatible workflow only after format/API feasibility is verified.

## 4. Product principles

### P1 — Provenance before completeness
A blank field with a reason is preferable to a plausible unsupported value.

### P2 — Exact configuration identity
Commercial model name alone is never the record identity.

### P3 — Raw evidence is immutable
Normalization or correction never overwrites the original source observation.

### P4 — Definitions matter as much as values
A “5.5 m turning radius” is not engineering-ready unless radius/diameter, reference envelope and source semantics are known or explicitly classified as unknown.

### P5 — Engineering derivation is controlled
Derived values must have a formula/version, input provenance, validity domain and tests.

### P6 — Readiness is use-case specific
A vehicle can be:
- adequate for basic dimensional comparison;
- not ready for AVT;
- ready for swept-path work but not ramp analysis;
- ready for ramp screening but not detailed vertical-clearance analysis.

### P7 — Conflicts are data
Conflicting authoritative sources are retained and surfaced, not silently resolved.

## 5. MVP scope

The first useful release shall support:

- vehicle identity and Thai-market applicability;
- parameter-level source observations;
- normalized SI engineering values;
- overall dimensions;
- wheelbase;
- front/rear overhang where known;
- front/rear tread/track observations;
- tyre and wheel sizes;
- ground-clearance observations with load state where known;
- published turning radius/circle observations with preserved wording;
- steering information where available;
- AVT-normalized mapping state;
- parameter evidence/confidence;
- search/filter;
- vehicle detail page;
- compare page;
- source/evidence page;
- data-quality/issues dashboard;
- Excel/CSV export;
- a pilot set of real Thai-market vehicles.

## 6. Deferred scope

Not required for the first implementation:

- automatic bulk web scraping without human/QA controls;
- automatic claim that all vehicles sold/registered in Thailand are complete;
- precise suspension kinematics;
- tyre deformation modelling;
- 3D underbody collision simulation;
- production ATL/ATX writer before format reliability is proven;
- mobile-native application;
- public write access;
- crowdsourced edits without moderation.

## 7. Vehicle population strategy

### Wave 0 — Schema proof
A small cross-category set sufficient to test identity, geometry, source and AVT semantics.

### Wave 1 — Engineering benchmark set
Approximately 20–30 current/recent Thai-market vehicle configurations covering:
- sedan/hatchback;
- SUV/crossover;
- pickup;
- MPV/van;
- EV;
- luxury large car;
- vehicles with different tyre sizes or steering specs across variants.

### Wave 2 — Common Thai fleet
Expand by market relevance and design usefulness, not alphabetical completeness.

### Wave 3 — Historical / specialist
Older generations still common in Thailand plus minibuses, coaches, rigid trucks, articulated vehicles, emergency/service vehicles as separate workstreams.

The Department of Land Transport / MOT open-data model list can be used as a Thailand inventory/reference input, but DLT commercial model labels are not assumed to uniquely resolve generation or engineering configuration.

## 8. Readiness states

Each vehicle shall expose at least:

- `IDENTITY_RESOLVED`
- `DIMENSION_READY`
- `SWEPT_PATH_PARTIAL`
- `AVT_READY`
- `RAMP_SCREENING_READY`
- `VERTICAL_CLEARANCE_READY`
- `CLIENT_REFERENCE_READY`

Readiness is derived from explicit required-field/evidence rules, not a subjective badge.

## 9. Data-quality dashboard

The application shall be able to report:
- unresolved vehicle identities;
- missing high-value parameters;
- conflicting evidence;
- stale sources;
- derived values whose inputs changed;
- records failing schema or unit validation;
- records that lost readiness after a source or rule update.

## 10. Non-functional requirements

### Auditability
Every publishable value must be traceable to one or more source observations or controlled derivation inputs.

### Determinism
The same approved inputs and formula version must produce the same derived value.

### Versionability
Schema, derivation rules and normalized records must be versioned.

### Maintainability
Vehicle data ingestion must not require hand-editing application source code.

### Shareability
The product must run as a web application accessible to authorized users without local Autodesk installation.

### Portability
The domain/data layer must not depend irreversibly on one hosting provider or database engine.

## 11. Acceptance criteria for moving to implementation

Codex implementation should not start until foundation review confirms:

1. Vehicle identity model is sufficient.
2. Parameter/evidence model preserves raw observations.
3. AVT terminology mappings are explicit.
4. Source/derivation/conflict rules are accepted.
5. MVP UI journeys are bounded.
6. Pilot dataset selection rules are accepted.
7. Architecture permits a later shared deployment.

## 12. Authoritative external references consulted for v1 foundation

- Autodesk Vehicle Tracking Help — Vehicle Wizard: Maneuverability  
  https://help.autodesk.com/cloudhelp/2023/ENU/Autodesk-VehicleTracking-Help/files/GUID-ECD33096-4BA8-495D-BA86-A74882E63CE2.htm
- Autodesk Vehicle Tracking Help — Unit Details: Front and Rear Axles  
  https://help.autodesk.com/cloudhelp/2022/ENU/Autodesk-VehicleTracking-Help/files/GUID-49418022-88CD-485E-8617-9E04E7077E83.htm
- Autodesk Vehicle Tracking Help — Glossary of Terms  
  https://help.autodesk.com/cloudhelp/2023/ENU/Autodesk-VehicleTracking-Help/files/GUID-A9F46388-F8AF-4389-B5A5-BDAB6C1E49AC.htm
- Autodesk Vehicle Tracking Help — Unit Details: Steering  
  https://help.autodesk.com/cloudhelp/CHS/Autodesk-VehicleTracking-Help/files/GUID-AFC8272A-98A5-4AE2-BBB3-5D3818B5F539.htm
- MOT Data Catalog / Department of Land Transport — first registrations by make/model  
  https://datagov.mot.go.th/dataset/dataset_stat_1_001

Retrieved/verified for this foundation on 2026-08-29.
