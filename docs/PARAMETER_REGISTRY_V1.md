# Engineering Parameter Registry v1

Status: Phase 0 seed registry  
Date: 2026-08-30

## Purpose

Provide stable semantic parameter codes for the initial database.

Parameter codes are contracts. Display labels may change; codes/definitions should not change silently.

This registry is intentionally focused on passenger cars, SUVs, pickups, MPVs and vans in the first pilot.

## Naming rules

- snake_case
- unit suffix only where it materially improves clarity
- distinguish OEM-published, physical-derived and screening outputs when semantics differ
- do not encode source grade in parameter code
- avoid generic names such as `track`, `width` or `turning_radius` where the reference is ambiguous

## A. Overall body geometry

| Code | Unit | Meaning |
|---|---|---|
| overall_length_mm | mm | Overall longitudinal vehicle length under source-defined conditions |
| overall_height_mm | mm | Overall height; roof/antenna semantics preserved separately |
| overall_width_reported_mm | mm | Width exactly as reported when envelope definition is not yet normalized |
| overall_width_body_mm | mm | Body envelope width excluding mirrors, only when established |
| overall_width_including_mirrors_mm | mm | Width with mirrors in normal/open state |
| overall_width_mirrors_folded_mm | mm | Width with mirrors folded |

## B. Longitudinal axle/body geometry

| Code | Unit | Meaning |
|---|---|---|
| wheelbase_actual_mm | mm | Actual front-to-rear axle reference distance for simple two-axle vehicle |
| front_overhang_mm | mm | Front axle reference to frontmost applicable body point |
| rear_overhang_mm | mm | Rear axle reference to rearmost applicable body point |

## C. OEM lateral axle geometry

| Code | Unit | Meaning |
|---|---|---|
| oem_front_tread_or_track_mm | mm | OEM-reported front tread/track with separate definition enum |
| oem_rear_tread_or_track_mm | mm | OEM-reported rear tread/track with separate definition enum |

These values are not AVT outer-face track unless definition proves equivalence.

## D. AVT lateral geometry

| Code | Unit | Meaning |
|---|---|---|
| avt_front_outer_face_track_mm | mm | Outer face to outer face of outermost front tyres under AVT semantics |
| avt_rear_outer_face_track_mm | mm | Outer face to outer face of outermost rear tyres under AVT semantics |

AVT readiness requires direct semantics or validated mounted geometry.

## E. Wheel / tyre

| Code | Unit | Meaning |
|---|---|---|
| front_tyre_size_text | text | OEM tyre-size notation |
| rear_tyre_size_text | text | OEM tyre-size notation |
| front_nominal_section_width_mm | mm | Nominal section width parsed/published |
| rear_nominal_section_width_mm | mm | Nominal section width parsed/published |
| nominal_unloaded_tyre_radius_front_mm | mm | Nominal unloaded radius, published/derived |
| nominal_unloaded_tyre_radius_rear_mm | mm | Nominal unloaded radius, published/derived |
| static_loaded_tyre_radius_front_mm | mm | Front static-loaded radius under stated load/pressure |
| static_loaded_tyre_radius_rear_mm | mm | Rear static-loaded radius under stated load/pressure |
| front_wheel_rim_text | text | Front rim specification |
| rear_wheel_rim_text | text | Rear rim specification |

## F. Turning observations

Use scalar value plus structured turning semantics.

| Code | Unit | Meaning |
|---|---|---|
| turning_radius_normalized_m | m | Radius after valid radius/diameter conversion, while reference semantics remain separate |
| oem_turning_value_text | text | Optional preserved display form when OEM semantics remain too ambiguous for numeric mapping |

Required associated semantics:
- radius/diameter
- curb/wall/other/unspecified reference
- curb axle scope
- wall envelope scope
- load condition
- direction if asymmetric

## G. Steering

| Code | Unit | Meaning |
|---|---|---|
| steering_ratio_value | ratio | Fixed ratio when source defines it |
| steering_wheel_lock_to_lock_turns | turns | Steering-wheel revolutions from lock to lock |
| maximum_inner_road_wheel_angle_deg | deg | Actual inner road-wheel angle at applicable full lock |
| maximum_outer_road_wheel_angle_deg | deg | Actual outer road-wheel angle |
| virtual_center_steering_angle_deg | deg | Equivalent virtual-centre steering angle under defined geometry |
| avt_maximum_steering_angle_deg | deg | AVT-adapter Maximum Steering Angle |
| avt_lock_to_lock_time_forward_s | s | AVT forward steering transition time |
| avt_lock_to_lock_time_reverse_s | s | AVT reverse steering transition time |

Do not infer one from another without a controlled rule.

Rear/secondary steering behavior is represented structurally in axle/steering tables rather than only by scalar parameters.

## H. Clearance

All clearance values require `clearance_type` and load applicability.

| Code | Unit | Meaning |
|---|---|---|
| clearance_value_mm | mm | Generic storage parameter only when accompanied by controlled clearance type |

Controlled types include:
- OEM_MINIMUM_UNSPECIFIED
- RUNNING_CLEARANCE
- BETWEEN_AXLES
- FRONT_AXLE
- REAR_AXLE
- DIFFERENTIAL
- BATTERY_PACK
- COMPONENT_SPECIFIC
- OTHER

A future physical schema may either use one typed clearance parameter plus attributes or dedicated parameter codes; it must preserve these semantics.

## I. Ramp angles — OEM published

| Code | Unit |
|---|---|
| oem_published_approach_angle_deg | deg |
| oem_published_departure_angle_deg | deg |
| oem_published_breakover_angle_deg | deg |

These preserve the OEM claim and its applicability.

## J. Ramp angles — geometry-derived physical

| Code | Unit |
|---|---|
| geometry_derived_approach_angle_deg | deg |
| geometry_derived_departure_angle_deg | deg |
| geometry_derived_breakover_angle_deg | deg |

These require the rule's actual contact/lower-envelope/static-loaded-tyre inputs.

## K. Ramp angles — engineering screening

| Code | Unit |
|---|---|
| screening_front_contact_angle_deg | deg |
| screening_rear_contact_angle_deg | deg |
| screening_breakover_angle_deg | deg |
| screening_breakover_symmetric_angle_deg | deg |

These must never be displayed as OEM or geometry-derived physical angles.

## L. Mass

| Code | Unit | Meaning |
|---|---|---|
| kerb_mass_kg | kg | Kerb mass under source definition |
| gross_vehicle_mass_kg | kg | Gross vehicle mass/maximum authorised mass as applicable |
| front_axle_load_kg | kg | Front axle load under stated condition |
| rear_axle_load_kg | kg | Rear axle load under stated condition |

## M. Supporting text / identity-sensitive fields

These may be structured columns rather than parameter rows depending on the physical schema:
- steering_system
- steering_ratio_type
- width_envelope_definition
- tyre pressure
- ride-height mode
- suspension mode
- rear-steering phase/mode/linkage
- turning semantics

## N. Explicitly forbidden ambiguous parameter codes

Do not create:
- `track_mm`
- `width_mm`
- `turning_radius_m` without reference semantics
- `ground_clearance_mm` without clearance type/load semantics
- `steering_angle_deg` without actual/virtual/AVT definition
- `breakover_angle_deg` when method class is not explicit

## O. Versioning

Adding a parameter is normally non-breaking.

Changing a parameter's semantic definition is breaking and requires:
- registry version change;
- migration/review;
- impact assessment for existing values and derivations.
