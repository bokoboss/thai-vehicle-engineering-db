# Vehicle Data Standard v1.0

Status: Foundation candidate after Deep Research amendment  
Date: 2026-08-30

## 1. Purpose

Define how vehicle identity, geometry, maneuverability, steering, tyre/wheel, vertical-clearance and provenance data are represented so the database can support engineering use without mixing source facts, interpretations, calculations or unresolved evidence.

This document is normative for data semantics.

## 2. Core data model

The standard separates:

1. **Vehicle identity** — the exact engineering configuration the data applies to.
2. **Source document** — a page, brochure, manual, dataset, drawing, regulatory record or measurement campaign.
3. **Source observation** — what the source literally states or shows.
4. **Normalized engineering value** — a value mapped to a controlled parameter definition/unit.
5. **Derived result** — a calculated value produced from approved inputs and a versioned engineering rule.
6. **Parameter assessment** — availability/research assessment when no defensible normalized value exists.
7. **Conflict/preference decision** — an auditable resolution layer that never deletes conflicting evidence.
8. **Geometry asset** — point/polyline/polygon/profile geometry with datum, role, fidelity and uncertainty.
9. **Readiness result** — use-case-specific determination such as AVT-ready or ramp-screening-ready.

A source observation is never overwritten by normalization, derivation or conflict resolution.

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
- `door/body_configuration`
- `wheel_tyre_package` where engineering geometry/manoeuvrability differs
- `equipment_package` where option-dependent geometry/steering differs
- `source_identity_notes`

### Identity rule

Two records must be separate when geometry, tyre fitment, ride height, steering, turning behaviour or body configuration relevant to engineering use differs materially.

Commercial model name alone is never a sufficient engineering identity.

Shared platform/family evidence may be referenced through explicit relationships; it must not be copied as if it were exact-configuration evidence unless equivalence is demonstrated.

## 4. Parameter families

### 4.1 Overall body geometry and width semantics

Store the source-reported value before assigning a normalized envelope.

- `overall_length_mm`
- `overall_height_mm`
- `overall_width_reported_mm`
- `width_envelope_definition`:
  - BODY_EXCLUDING_MIRRORS
  - INCLUDING_MIRRORS_OPEN
  - INCLUDING_MIRRORS_FOLDED
  - BODY_AND_FIXED_APPENDAGES
  - OEM_UNSPECIFIED
  - OTHER
- `overall_width_body_mm` only when body-only semantics are established
- `overall_width_including_mirrors_mm` only when mirror-open semantics are established
- `overall_width_mirrors_folded_mm` only when folded semantics are established
- roof/antenna inclusion note

An OEM field labelled only “width” must not silently become body width.

### 4.2 Longitudinal axle geometry

- `wheelbase_actual_mm`
- `front_overhang_mm`
- `rear_overhang_mm`
- `front_axle_to_datum_mm`
- `rear_axle_to_datum_mm`
- axle-group geometry for multi-axle vehicles
- effective axle/wheelbase values only through an explicit AVT-specific mapping or other controlled engineering model

### 4.3 Lateral axle / tyre geometry

OEM “tread/track” semantics and AVT track semantics are separate.

- `oem_front_tread_or_track_mm`
- `oem_rear_tread_or_track_mm`
- `oem_track_definition`:
  - TYRE_CENTERLINE
  - WHEEL_CENTERLINE
  - OUTER_TYRE_FACES
  - INNER_TYRE_FACES
  - OEM_UNSPECIFIED
  - OTHER
- `front_tyre_size`
- `rear_tyre_size`
- `front_nominal_section_width_mm`
- `rear_nominal_section_width_mm`
- `wheel_rim_front`
- `wheel_rim_rear`
- `nominal_unloaded_tyre_radius_mm` where derived/verified
- `static_loaded_tyre_radius_front_mm`
- `static_loaded_tyre_radius_rear_mm`
- load/pressure applicability for static-loaded radius
- `avt_front_outer_face_track_mm`
- `avt_rear_outer_face_track_mm`
- `avt_track_method`

Nominal tyre section width alone is not sufficient to establish mounted outer-face track for `AVT_READY`.

### 4.4 Maneuverability / turning

Every turning observation must preserve radius/diameter and reference-envelope semantics.

- `turning_value_raw`
- `turning_unit_raw`
- `turning_radius_or_diameter`:
  - RADIUS
  - DIAMETER
  - OEM_UNSPECIFIED
- `turning_reference`:
  - CURB_TO_CURB
  - WALL_TO_WALL
  - WHEEL_PATH_OTHER
  - BODY_PATH_OTHER
  - OEM_UNSPECIFIED
- `turning_axle_scope`:
  - ALL_AXLES
  - ACTIVE_AXLES
  - OEM_UNSPECIFIED
  - OTHER
- `turning_wall_envelope_scope`:
  - BODY_ONLY
  - BODY_AND_LOADS
  - OEM_UNSPECIFIED
  - NOT_APPLICABLE
- `turning_load_condition_id`
- `turning_test_speed` if stated
- `turning_direction` if asymmetric
- `normalized_turning_radius_m`
- source wording

An OEM “minimum turning radius” with no envelope definition remains `OEM_UNSPECIFIED`.

### 4.5 Steering

Vehicle steering facts and AVT steering-model inputs remain distinct.

- `steering_system`
- `steering_ratio`
- `steering_ratio_type`: FIXED / VARIABLE / UNKNOWN
- `steering_wheel_lock_to_lock_turns`
- `maximum_inner_road_wheel_angle_deg`
- `maximum_outer_road_wheel_angle_deg`
- `virtual_center_steering_angle_deg`
- AVT adapter output: `avt_maximum_steering_angle_deg`
- `avt_lock_to_lock_time_forward_s` where known/selected
- `avt_lock_to_lock_time_reverse_s` where known/selected
- `lock_to_lock_time_method_or_assumption`
- steering source notes

Steering-wheel turns lock-to-lock cannot be used to infer maximum road-wheel angle or AVT lock-to-lock time without additional evidence/assumptions.

#### Rear / secondary steering

Represent rear steering by axle and linkage behaviour, not only a boolean:

- `steered_axle_id`
- `steering_role`: PRIMARY / SECONDARY / LINKED
- `linkage_type`: FIXED_RATIO / VARIABLE_RATIO / FUNCTION / MODE_DEPENDENT / UNKNOWN
- `max_steering_angle_deg`
- `phase_behavior`: OPPOSITE_PHASE / SAME_PHASE / MODE_OR_SPEED_DEPENDENT / UNKNOWN
- `angle_ratio_or_function`
- speed/mode applicability
- evidence/source

### 4.6 Clearance taxonomy

Do not collapse genuinely different clearance concepts into one generic minimum.

- `clearance_value_mm`
- `clearance_type`:
  - OEM_MINIMUM_UNSPECIFIED
  - RUNNING_CLEARANCE
  - BETWEEN_AXLES
  - FRONT_AXLE
  - REAR_AXLE
  - DIFFERENTIAL
  - BATTERY_PACK
  - COMPONENT_SPECIFIC
  - OTHER
- `clearance_component_or_reference`
- `load_condition_id`
- suspension/ride-height applicability
- air-suspension state where applicable

### 4.7 Structured load condition

A reusable load-condition record may include:

- mass basis: UNLADEN / KERB / OEM_LADEN / DESIGN_LOAD / GVW / OTHER
- total mass where known
- occupants/payload assumption
- axle loads where known
- tyre pressure where relevant
- suspension / ride-height mode
- OEM raw wording
- source/evidence

### 4.8 Ramp-related angles

Separate result classes by semantics.

#### OEM published
- `oem_published_approach_angle_deg`
- `oem_published_departure_angle_deg`
- `oem_published_breakover_angle_deg`

#### Geometry-derived physical
- `geometry_derived_approach_angle_deg`
- `geometry_derived_departure_angle_deg`
- `geometry_derived_breakover_angle_deg`

These require actual relevant lower-envelope/contact geometry, axle/tyre geometry, static-loaded tyre radius and load/ride-height state sufficient for the chosen definition.

#### Engineering screening
- `screening_front_contact_angle_deg`
- `screening_rear_contact_angle_deg`
- `screening_breakover_angle_deg`
- `screening_breakover_symmetric_angle_deg`

Screening outputs must never populate OEM-published or geometry-derived parameter codes.

### 4.9 Mass / loading

- kerb mass
- gross vehicle mass
- axle loads where available
- passenger/payload assumptions
- source/load-state semantics

## 5. Geometry assets

Every point/polyline/polygon/profile must declare a role.

### Geometry roles

- `PLAN_BODY_ENVELOPE`
- `AVT_PLAN_PROFILE`
- `SIDE_SILHOUETTE`
- `LONGITUDINAL_LOWER_ENVELOPE`
- `UNDERBODY_LOW_POINTS`
- `TIRE_CIRCLE`
- `AXLE_DATUM_GEOMETRY`
- `OTHER`

A side silhouette is not equivalent to a longitudinal lower interference envelope.

### Coordinate convention

Default v1 vehicle-fixed reference frame for simple vehicles:

- origin: ground-plane projection of the front axle centerline at the vehicle longitudinal centerline
- +X: rearward along the vehicle
- +Y: vehicle left when viewed in the forward travel direction
- +Z: upward
- units: mm

If a source uses another datum, preserve the source convention and store the transformation used to normalize it.

### Geometry metadata

Each asset must state:

- datum/reference frame
- scale/unit
- load/ride-height state
- body/mirror inclusion
- geometry role
- `geometry_method`: OEM_CAD / OEM_DIMENSION_DRAWING / SCALED_DRAWING / PHYSICAL_SURVEY / DERIVED / OTHER
- `geometry_fidelity` or equivalent quality classification
- source/derivation method
- uncertainty/drawing-scale limitation

## 6. Source document model

Each source has:

- `source_id`
- title
- publisher/authority
- source type
- market/jurisdiction
- publication/model year
- URL
- retrieved_at
- local snapshot reference where legally/operationally retained
- document fingerprint/hash where retained
- page/section
- access/licensing notes
- applicability notes
- archival status

### Source authority classes

- REGULATORY_OFFICIAL
- OEM_THAILAND
- OFFICIAL_LOCAL_DISTRIBUTOR_IMPORTER
- OEM_REGIONAL_GLOBAL
- OEM_SERVICE_TECHNICAL
- OEM_HOMOLOGATION_CERTIFICATION
- REPUTABLE_SECONDARY
- OTHER_SECONDARY
- PHYSICAL_MEASUREMENT

Authority class alone never determines engineering confidence.

## 7. Source observation model

A source observation records the source literally before interpretation:

- `observation_id`
- `vehicle_identity_claim`
- `source_id`
- `raw_label`
- `raw_value`
- `raw_unit`
- `raw_qualifier`
- minimal audit excerpt where needed
- source-reported precision/significant digits
- measurement/extraction uncertainty where known
- page/section locator
- extraction method: MANUAL / STRUCTURED / OCR / PARSER / OTHER
- extracted_at
- extractor/reviewer
- ambiguity note

## 8. Orthogonal value/evidence state

Do not use one mutually exclusive `status` enum to represent method, conflict, review and availability.

A normalized/assessed parameter shall be able to express independent dimensions such as:

### Evidence method
- PUBLISHED
- MEASURED
- DERIVED
- ESTIMATED
- NONE

### Resolution state
- UNCONTESTED
- CONFLICTING
- PREFERRED_WITH_CONFLICT
- SUPERSEDED
- NOT_APPLICABLE

### Verification state
- UNREVIEWED
- REVIEWED
- VERIFIED
- REJECTED

### Availability state
- AVAILABLE
- UNKNOWN
- NOT_FOUND_AFTER_SEARCH
- NOT_APPLICABLE

This allows, for example:

> PUBLISHED + CONFLICTING + REVIEWED + AVAILABLE

without erasing any dimension of the evidence state.

A separate `parameter_assessment` may record unknown reason, source families searched and review date when no normalized numeric value exists.

## 9. Evidence quality model

Evaluate at least three independent axes:

### Authority
How authoritative is the source for this parameter?

### Applicability
- EXACT_CONFIGURATION
- SAME_GEOMETRY_CONFIRMED
- SAME_GENERATION_UNCONFIRMED_VARIANT
- ADJACENT_MARKET_UNCONFIRMED
- UNKNOWN_APPLICABILITY

### Evidence method
PUBLISHED / MEASURED / DERIVED / ESTIMATED

A human-readable grade may be generated, but underlying dimensions must remain stored.

Suggested display grades:

- A1 — primary/official, exact configuration, published/regulatory (including an official local importer/distributor where it is the authoritative Thai-market publisher)
- A2 — OEM/official, same geometry confirmed
- A3 — strong technical/homologation/service evidence with confirmed applicability
- B — controlled engineering derivation from A-grade inputs
- C — reputable secondary reference
- D — estimate/inference/image scaling
- M — documented physical measurement

## 10. Conflict policy

Multiple observations may map to the same parameter.

When values conflict:

1. retain all observations;
2. retain evidence method for each observation/value;
3. mark the resolution state as conflicting;
4. compare identity, market, model year, units, load condition and parameter definition;
5. resolve only with documented rationale;
6. never delete losing evidence solely because another source becomes preferred.

A preferred value must reference the decision record or rule used.

## 11. Unit and precision policy

Canonical internal units:

- length: mm
- turning radius: m user-facing; a consistent internal unit may be used
- angle: degrees
- mass: kg

Always preserve raw units and reported precision.

Conversions must be deterministic and tested.

Do not round internally merely to match display precision.

Measured/scaled/derived values must carry uncertainty/precision metadata where reasonably determinable.

## 12. Autodesk Vehicle Tracking mapping rules

AVT fields are adapter outputs, not synonyms for OEM fields.

### 12.1 Wheel track

AVT wheel track for a tyred axle is based on the outer faces of the outermost tyres.

Therefore:

- OEM tread/centerline track remains separate.
- Direct AVT track requires source evidence explicitly matching outer-face semantics.
- A valid derived AVT track requires explicit mounted wheel/tyre geometry sufficient to establish outer-face position.
- OEM centreline track + nominal tyre section width may be retained only as an estimated/screening derivation.
- That nominal-width derivation alone must fail `AVT_READY`.

### 12.2 Turning radius

Only map to AVT curb-to-curb when curb semantics and required axle scope are established.

Only map to AVT wall-to-wall when wall semantics and required body/body+loads envelope scope are established.

Unknown scope fails closed.

### 12.3 Steering angle

Keep distinct:

- actual inner/outer road-wheel angles
- virtual center steering angle
- AVT Maximum Steering Angle adapter output
- steering-wheel turns

No implicit conversion between them.

### 12.4 Lock-to-lock time

AVT lock-to-lock time is a steering-transition/driver characteristic in seconds, distinct from steering-wheel revolutions.

If no defensible time exists, retain unknown. A project/simulation assumption is stored as an AVT scenario/model setting, not as an OEM fact.

### 12.5 Rear steering

AVT mapping for linked/secondary steering must be based on explicit axle/linkage behaviour. A simple `rear_steering_present=true` is insufficient for an AVT-ready multi-steer record.

### 12.6 Effective wheelbase / axles

For simple two-axle vehicles, actual front/rear axle geometry is generally the source basis.

Multi-axle/effective-axle behaviour requires an explicit AVT mapping rule and is deferred until those classes are implemented.

### 12.7 Body envelope

Store real plan geometry where available.

Overall width alone is a fallback envelope, not an exact body polygon.

Mirror inclusion must be explicit.

### 12.8 AVT integration levels

- Level 0 — evidence-backed engineering data sheet: supported
- Level 1 — AVT input preparation sheet: supported
- Level 2 — assisted/manual Vehicle Wizard/library workflow: supported
- Level 3 — automated ATL/ATX or equivalent exchange: research/installed-environment experiment gate
- Level 4 — company library management: manual/shared workflow plausible; automation unproven

Do not claim an open ATL/ATX serialization format or supported external writer until verified.

## 13. Controlled derivations

Each rule shall define:

- `derivation_rule_id`
- formula
- version
- required parameter IDs
- prohibited/missing conditions
- units
- output parameter code
- uncertainty classification
- test cases
- source/reference basis
- validity domain

Examples acceptable in principle:

- unit conversion
- front + wheelbase + rear overhang consistency check
- nominal unloaded tyre radius from standard tyre-size notation, explicitly labelled nominal
- screening ramp angles under explicit simplified geometry
- AVT outer-face track only where actual mounted geometry is sufficiently defined

Examples that must fail closed without adequate geometry:

- true breakover angle from wheelbase + generic ground clearance
- true approach/departure angle from generic clearance + overhang
- maximum road-wheel angle from steering-wheel turns
- wall-to-wall radius from curb-to-curb without body geometry
- AVT-ready outer-face track from undefined OEM tread + nominal tyre section width

## 14. Ramp / vertical-clearance methodology boundary

### Evidence levels

- **Level A — OEM published:** preserve the exact OEM physical-angle claim and applicability.
- **Level B — Geometry-derived physical:** requires actual relevant lower-envelope/contact geometry, axle/tyre geometry, static-loaded tyre radius and load/ride-height state.
- **Level C — Engineering screening:** simplified calculation with explicit assumptions and screening-specific parameter names.
- **Level D — Insufficient evidence:** no defensible numeric result.

### Future detailed ramp check

A routine future 2D longitudinal check may use:

- axle centers
- static-loaded tyre radius
- wheelbase/axle positions
- front lower envelope
- between-axle lower envelope
- rear lower envelope
- explicit datum
- road/ramp vertical-alignment profile
- load/ride-height state
- geometry uncertainty

It may report CLEAR / INTERFERENCE / INDETERMINATE_WITH_UNCERTAINTY.

A 2D model is not proof where crossfall, diagonal approach, articulation, suspension dynamics, lateral underbody variation or 3D obstructions control.

No ramp solver is part of Phase 0.

## 15. Deterministic quality checks

### Identity
- no unresolved duplicate exact configurations
- valid model-year ranges
- market set
- option/wheel-package differences preserved where material

### Geometry
- positive physical dimensions
- wheelbase less than overall length for normal passenger vehicles
- verified front + wheelbase + rear approximately equals overall length within declared tolerance
- geometry asset role/datum/fidelity present

### Width
- OEM-unspecified width cannot populate a body-only or mirror-specific field silently

### Turning
- radius/diameter semantics explicit or unknown
- curb axle scope preserved
- wall envelope scope preserved
- no factor-of-two conversion without radius/diameter evidence

### Steering
- steering-wheel turns, actual wheel angle and virtual-center angle remain separate
- rear-steer linkage required before AVT-ready rear-steer mapping

### Clearance
- clearance type and load applicability preserved
- between-axles/axle/battery/running clearances remain distinct

### Evidence
- published/derived/measured/estimated method independent from conflict/review/availability
- derived values require rule version + input lineage
- measured/scaled values carry uncertainty where reasonably determinable
- conflicting evidence cannot be presented as unqualified uncontested fact

### AVT readiness
Fail closed if required track, turning-envelope, steering or body semantics are unresolved.

### Ramp readiness
Fail closed if a geometry-derived physical angle lacks static-loaded tyre/contact/lower-envelope evidence required by its rule.

## 16. Thailand inventory / DLT role

DLT/MOT registration data may support:

- discovery of makes/models appearing in Thailand
- market-presence metadata
- commercial-model prioritization

It is not an exact geometry/configuration identifier.

Generation, chassis, trim, powertrain, wheel package and engineering applicability require separate resolution.

## 17. Source snapshots and persistence

Because OEM pages and brochures change:

- record retrieval date
- retain source title/publisher/URL/page
- retain local snapshot or document fingerprint where legally/operationally appropriate
- do not rely on a bare URL as the only provenance

Large source archives should not be committed to Git by default.

## 18. Versioning

- data standard is versioned
- schema migrations are versioned
- derivation rules are independently versioned
- AVT adapter/mapping rules are independently versioned
- changing a parameter definition is a breaking contract change requiring migration/review
- normalized/derived results must remain reproducible from evidence and rule versions

## 19. Foundation research outcome incorporated

Deep Research completed 2026-08-30 returned **GO WITH CONDITIONS** and required amendment of the foundation before schema implementation.

The must-fix semantic conditions incorporated here are:

1. orthogonal evidence/value state
2. exact AVT curb/wall turning scope
3. distinct AVT Maximum Steering Angle vs actual wheel angle
4. stricter AVT outer-face-track readiness rule
5. structured clearance taxonomy
6. structured load condition + static-loaded tyre radius
7. explicit lower-envelope geometry roles and screening-angle parameter names
8. richer rear-steering/linkage semantics
9. structured width/mirror semantics

## 20. Key external reference families

Authoritative implementation/research records should cite the exact version/page used. Foundation research relied principally on:

- Autodesk Vehicle Tracking official Help: maneuverability, axle/track, steering, path transitions and vehicle-library workflows
- Thailand DLT/MOT open-data catalog
- Thai/global OEM primary specifications and owner/technical documentation
- rigorous geometric definitions of approach/departure/breakover/static-loaded-radius from U.S. regulatory material as an engineering-definition reference, **not as Thai parking-design law**

The repository must preserve exact source citations at the observation/decision level rather than treating this summary list as parameter evidence.
