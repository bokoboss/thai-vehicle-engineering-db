# Vehicle Data Standard v1.0

Status: Draft for foundation review  
Date: 2026-08-29

## 1. Purpose

Define how vehicle geometry, maneuverability, steering, tyre/wheel, vertical-clearance and provenance data are represented so the database can support engineering use without mixing source facts, interpretations and calculations.

This document is normative for data semantics.

## 2. Core data model

The standard separates five concepts:

1. **Vehicle identity** — the exact engineering configuration the data applies to.
2. **Source document** — a page, brochure, manual, dataset, drawing, regulatory record or measurement campaign.
3. **Source observation** — what the source literally states or shows.
4. **Normalized engineering value** — a value mapped to a controlled parameter definition/unit.
5. **Derived result** — a calculated value produced from approved inputs and a versioned engineering rule.

A source observation is never overwritten by normalization or derivation.

## 3. Vehicle identity

### Required identity fields
- `vehicle_id` — stable internal ID
- `manufacturer`
- `commercial_model`
- `generation_name`
- `chassis_platform_code` where known
- `market` — e.g. TH
- `body_style`
- `model_year_from`
- `model_year_to`
- `sale_period_from/to` where known
- `variant_trim`
- `powertrain`
- `drivetrain`
- `door/body configuration`
- `wheel_tyre_package` if geometry/manoeuvrability differs
- `source_identity_notes`

### Identity rule
Two records must be separate when any geometry, tyre, ride-height, steering or turning parameter relevant to engineering use can differ materially.

Do not merge records solely because the Thai commercial model name is the same.

## 4. Parameter families

### 4.1 Overall body geometry
- overall_length_mm
- overall_width_body_mm
- overall_width_including_mirrors_mm
- overall_width_mirrors_folded_mm
- overall_height_mm
- roof/antenna inclusion note
- body_outline_plan geometry when available
- body_outline_side geometry when available

### 4.2 Longitudinal axle geometry
- wheelbase_actual_mm
- front_overhang_mm
- rear_overhang_mm
- front_axle_to_datum_mm
- rear_axle_to_datum_mm
- axle_group geometry for multi-axle vehicles

### 4.3 Lateral axle / tyre geometry
Keep OEM axle-center / tread data separate from AVT outer-face track.

- oem_front_tread_or_track_mm
- oem_rear_tread_or_track_mm
- oem_track_definition
- front_tyre_size
- rear_tyre_size
- front_nominal_section_width_mm
- rear_nominal_section_width_mm
- wheel_rim_front
- wheel_rim_rear
- tyre_outer_diameter_mm where verified/derived
- avt_front_outer_face_track_mm
- avt_rear_outer_face_track_mm
- avt_track_method

### 4.4 Maneuverability
Every turning observation must record its semantics.

- turning_value_raw
- turning_unit_raw
- turning_radius_or_diameter
- turning_reference:
  - CURB_TO_CURB
  - WALL_TO_WALL
  - WHEEL_PATH_OTHER
  - BODY_PATH_OTHER
  - OEM_UNSPECIFIED
- turning_load_state
- turning_direction if asymmetric
- normalized_turning_radius_m
- source_wording

Do not convert an unspecified OEM “minimum turning radius” into AVT curb-to-curb merely because that is common industry usage.

### 4.5 Steering
- steering_system
- steering_ratio
- steering_ratio_type: FIXED / VARIABLE / UNKNOWN
- steering_wheel_lock_to_lock_turns
- maximum_inner_road_wheel_angle_deg
- maximum_outer_road_wheel_angle_deg
- equivalent_center_steering_angle_deg
- rear_wheel_steering_present
- rear_wheel_max_angle_deg
- steering_source_notes

Lock-to-lock steering-wheel turns alone are insufficient to derive maximum road-wheel angle.

### 4.6 Ground / vertical clearance
- minimum_ground_clearance_mm
- clearance_load_state:
  - UNLADEN
  - KERB
  - DESIGN_LOAD
  - GVW
  - OEM_UNSPECIFIED
- clearance_reference_point / component
- front_low_point geometry
- underbody profile geometry
- rear_low_point geometry
- suspension/ride-height mode
- air_suspension state if applicable

### 4.7 Ramp-related geometry
- approach_angle_deg
- departure_angle_deg
- breakover_angle_deg
- ramp_angle_source_or_method
- contact/reference points
- load state
- vehicle ride-height mode

A true approach/departure/breakover angle must not be labelled VERIFIED if calculated only from global minimum ground clearance and a wheelbase/overhang when the actual limiting body/underbody points are unknown.

An idealized screening angle may be stored as a separate derived parameter only if clearly named and documented as a simplified model.

### 4.8 Mass / loading (supporting)
- kerb_mass_kg
- gross_vehicle_mass_kg
- front/rear axle loads where available
- passenger/load assumption

These are supporting fields for clearance/load-state interpretation and future analysis; they are not mandatory for the initial swept-path MVP.

## 5. Source document model

Each source has:
- `source_id`
- title
- publisher/authority
- source type
- market/jurisdiction
- publication/model year
- URL
- retrieved_at
- local_snapshot_reference if legally/operationally retained
- document fingerprint/hash where retained
- page/section
- access/licensing notes
- applicability notes
- archival status

### Source authority classes
- `REGULATORY_OFFICIAL`
- `OEM_THAILAND`
- `OEM_REGIONAL_GLOBAL`
- `OEM_SERVICE_TECHNICAL`
- `OEM_HOMOLOGATION_CERTIFICATION`
- `REPUTABLE_SECONDARY`
- `OTHER_SECONDARY`
- `PHYSICAL_MEASUREMENT`

Authority class does not by itself determine confidence. Exact applicability and evidence method also matter.

## 6. Source observation model

A source observation records the source literally before interpretation:

- `observation_id`
- `vehicle_identity_claim`
- `source_id`
- `raw_label`
- `raw_value`
- `raw_unit`
- `raw_qualifier`
- `raw_text_excerpt` limited to what is necessary for audit
- page/section locator
- extraction method: MANUAL / STRUCTURED / OCR / PARSER / OTHER
- extracted_at
- extractor/reviewer
- ambiguity note

Where a source is a drawing, the observation may be a dimension annotation or controlled measurement rather than text.

## 7. Normalized engineering value model

A normalized value has:
- `parameter_code`
- canonical value
- canonical unit
- source observation(s)
- normalization rule/version
- applicability to exact vehicle identity
- status
- evidence grade
- reviewer
- reviewed_at

### Status
- VERIFIED_PUBLISHED
- VERIFIED_MEASURED
- DERIVED
- ESTIMATED
- CONFLICTING
- UNKNOWN
- NOT_APPLICABLE
- SUPERSEDED

## 8. Evidence quality model

Evidence quality is evaluated on three independent axes.

### 8.1 Authority
How authoritative is the source for the parameter?

### 8.2 Applicability
- EXACT_CONFIGURATION
- SAME_GEOMETRY_CONFIRMED
- SAME_GENERATION_UNCONFIRMED_VARIANT
- ADJACENT_MARKET_UNCONFIRMED
- UNKNOWN_APPLICABILITY

### 8.3 Evidence method
- PUBLISHED
- MEASURED
- DERIVED
- ESTIMATED

### Display evidence grade
A human-readable grade may be generated from the three axes, but the underlying axes remain stored.

Suggested display grades:
- A1 — primary/official, exact configuration, published or regulatory
- A2 — OEM/official, same geometry confirmed
- A3 — strong technical/homologation/service evidence with confirmed applicability
- B — controlled engineering derivation from A-grade inputs
- C — reputable secondary reference
- D — estimate/inference/image scaling
- M — documented physical measurement

The grade must never hide the underlying authority/applicability/method metadata.

## 9. Conflict policy

Multiple observations may map to the same parameter.

When values conflict:
1. retain all observations;
2. mark the normalized parameter CONFLICTING;
3. compare identity, market, model year, units, load state and parameter definition;
4. resolve only with documented rationale;
5. never delete the losing evidence solely because another source was selected.

A selected/preferred value must reference the decision record or rule used.

## 10. Unit policy

Canonical internal units:
- length: mm
- radius: m for user-facing turning radius; mm is permitted internally if consistent
- angle: degrees
- mass: kg

Always preserve raw units.

Conversions must be deterministic and tested.

Do not round internally merely to match display precision.

## 11. Autodesk Vehicle Tracking mapping rules

AVT fields are outputs from this database, not synonyms for OEM fields.

### 11.1 Wheel track
Autodesk Vehicle Tracking defines wheel track for tyred wheels as the distance between the outer faces of the outermost tyres on an axle.

Therefore:
- OEM tread/track-center data is stored separately.
- It must not be copied directly into `avt_*_outer_face_track_mm`.
- A derived outer-face track may be computed only under an explicit tyre-geometry rule and shall remain DERIVED.
- Nominal tyre section width is not automatically equivalent to actual mounted section width; derivation uncertainty must be documented.

### 11.2 Turning radius
AVT supports maneuverability input using curb-to-curb radius, wall-to-wall radius or steering/wheel angle.

Only map a published turning observation to AVT curb-to-curb or wall-to-wall when the source definition supports that mapping.

### 11.3 Maximum steering angle
AVT can calculate a maximum steering angle from an appropriate turning radius. If an authoritative turning radius is available and correctly classified, this is generally preferable to inventing a wheel angle from incomplete steering-wheel data.

### 11.4 Effective wheelbase / axles
For simple two-axle passenger vehicles, actual front/rear axle geometry is generally sufficient as source geometry. Multi-axle/effective-axle behavior requires explicit AVT mapping rules and is deferred until that vehicle class is implemented.

### 11.5 Body envelope
Store the real plan body outline where available. Overall width alone is a fallback envelope, not equivalent to an exact body polygon.

Mirror inclusion must be explicit. A body envelope for physical wall-clearance checks may differ from the conventional swept body used for kerb/path design.

## 12. Controlled derivations

Each derivation rule shall define:
- `derivation_rule_id`
- formula
- version
- required parameters
- prohibited/missing conditions
- units
- output parameter
- uncertainty classification
- test cases
- source/reference basis

Examples of acceptable controlled derivations:
- unit conversion;
- overall front+rear overhang check: `L - wheelbase`;
- nominal tyre diameter from standardized tyre size as a labelled nominal derived value;
- AVT outer-face track approximation from centerline tread + tyre width only if the method is explicitly labelled approximate/derived.

Examples that require special caution:
- true breakover angle from only wheelbase + minimum ground clearance;
- approach/departure angle from global clearance;
- max road-wheel angle from steering-wheel lock-to-lock;
- wall-to-wall radius from curb-to-curb without body geometry.

These shall not be promoted to verified engineering values without adequate geometry.

## 13. Quality checks

Deterministic validators should include:

### Identity
- no overlapping duplicate exact configurations without an explicit relationship;
- model-year ranges valid;
- market set.

### Geometry
- overall_length > wheelbase for normal road vehicles;
- if both overhangs are verified: front + wheelbase + rear approximately equals overall length within defined tolerance;
- positive widths/heights/tracks;
- tyre size parse validity.

### Turning
- radius/diameter semantics explicit or OEM_UNSPECIFIED;
- normalized radius > 0;
- no silent factor-of-two conversion without radius/diameter evidence.

### Evidence
- verified/derived values require provenance;
- derived values require rule version and input IDs;
- estimated values require method and limitation;
- conflicting sources cannot be presented as unqualified verified values.

### Readiness
AVT_READY and ramp-related readiness shall be computed from explicit rule sets and fail closed when required semantics are unknown.

## 14. DLT / Thailand inventory role

The Department of Land Transport / MOT Data Catalog vehicle registration datasets may be used to:
- discover commercial makes/models appearing in Thai registration data;
- prioritize common models;
- support market-presence metadata.

They shall not be treated as authoritative geometry/configuration identifiers without further resolution.

Reference:
https://datagov.mot.go.th/dataset/dataset_stat_1_001

## 15. Source snapshots and persistence

Because OEM pages and brochures change:
- record retrieval date;
- retain source title/publisher/URL/page;
- retain a local snapshot or document fingerprint where legally and operationally appropriate;
- do not rely on a bare URL as the only provenance record.

Large source archives should not be committed to Git by default. Git should contain metadata, schemas, scripts, normalized/curated small data and audit records; source storage strategy is separate.

## 16. Versioning

- Data standard uses semantic document versions.
- Schema migrations are versioned.
- Derivation rules are versioned independently.
- A normalized value must be reproducible against its source observations and rule versions.
- Changing a parameter definition is a breaking data-contract change and requires migration/review.

## 17. Authoritative AVT references used for this standard

Autodesk Vehicle Tracking:
- Vehicle Wizard: Maneuverability  
  https://help.autodesk.com/cloudhelp/2023/ENU/Autodesk-VehicleTracking-Help/files/GUID-ECD33096-4BA8-495D-BA86-A74882E63CE2.htm
- Unit Details: Front and Rear Axles  
  https://help.autodesk.com/cloudhelp/2022/ENU/Autodesk-VehicleTracking-Help/files/GUID-49418022-88CD-485E-8617-9E04E7077E83.htm
- Glossary of Terms  
  https://help.autodesk.com/cloudhelp/2023/ENU/Autodesk-VehicleTracking-Help/files/GUID-A9F46388-F8AF-4389-B5A5-BDAB6C1E49AC.htm
- Unit Details: Steering  
  https://help.autodesk.com/cloudhelp/CHS/Autodesk-VehicleTracking-Help/files/GUID-AFC8272A-98A5-4AE2-BBB3-5D3818B5F539.htm
- Unit Details: Unit  
  https://help.autodesk.com/cloudhelp/2022/ENU/Autodesk-VehicleTracking-Help/files/GUID-DB610206-15FF-4AA2-B2C5-07D4B28598ED.htm
- Vehicle Libraries  
  https://help.autodesk.com/cloudhelp/2024/ENU/Autodesk-VehicleTracking-Help/files/GUID-6F7BD13F-9363-40EC-AF22-A56D2270C410.htm

Retrieved/verified for this foundation on 2026-08-29.
