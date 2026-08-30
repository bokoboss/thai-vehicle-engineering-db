# Autodesk Vehicle Tracking Mapping Specification v1

Status: Foundation engineering adapter contract  
Date: 2026-08-30

## 1. Purpose

Define how the project engineering database maps to Autodesk Vehicle Tracking (AVT) without treating OEM terminology as AVT terminology by default.

AVT is an external consumer. Its fields are adapter outputs, not the master source schema.

## 2. Integration levels

### Level 0 — Engineering data sheet
Evidence-backed vehicle data presented independently of AVT.

Status: supported.

### Level 1 — AVT input preparation sheet
Prepare exact AVT-relevant fields with provenance, derivation and blockers.

Status: supported.

### Level 2 — Assisted/manual Vehicle Wizard/library workflow
Engineer uses prepared data in AVT and verifies the created vehicle.

Status: supported.

### Level 3 — Automated exchange/export
Programmatic ATL/ATX or equivalent creation.

Status: research/installed-environment experiment required.

### Level 4 — Automated company library management
Automated deployment/update of company AVT vehicle libraries.

Status: manual/shared-library workflow plausible; automation unproven.

## 3. Wheel track

### AVT semantic

For a tyred axle, AVT track is the distance across the **outer faces of the outermost tyres**.

### Database mapping

Potential source values:
- OEM tread/track centerline;
- OEM undefined “track”;
- explicit outer-face dimension;
- mounted wheel/tyre geometry;
- physical measurement.

Rules:

1. OEM undefined tread/track is not AVT track.
2. Nominal tyre section width is not proof of mounted outer-face position.
3. `centerline track + nominal section width` may be retained only as ESTIMATED/SCREENING.
4. That estimate alone must fail AVT_READY.
5. AVT_READY requires:
   - direct outer-face evidence; or
   - a validated derivation from sufficiently explicit mounted geometry.

## 4. Wheelbase / axle geometry

For simple conventional two-axle passenger vehicles:
- actual front/rear axle geometry is the normal source basis.

For:
- multi-axle groups;
- retracting/self-steering axles;
- non-conventional steering;
- articulated vehicles;

effective axle/effective wheelbase must be handled by explicit AVT mapping rules.

Do not generalize a passenger-car formula to all vehicle classes.

## 5. Turning radius / circle

Raw source data must preserve:

- original label;
- value/unit;
- radius vs diameter/circle interpretation;
- curb/kerb vs wall vs other/unspecified;
- axle scope;
- wall envelope scope;
- load condition;
- direction/asymmetry where relevant.

### Curb-to-curb

AVT mapping requires curb semantics plus required axle scope.

Possible axle scope:
- ALL_AXLES
- ACTIVE_AXLES
- OEM_UNSPECIFIED
- OTHER

Unknown axle scope remains a blocker where it materially affects the mapping.

### Wall-to-wall

AVT mapping requires wall semantics plus envelope scope:
- BODY_ONLY
- BODY_AND_LOADS
- OEM_UNSPECIFIED

A body-width specification does not create a wall-to-wall turning radius.

## 6. Steering angle

Keep separate:

### Actual wheel angle
Maximum actual road-wheel angle, commonly inner wheel at full lock for conventional steering.

### Virtual-center steering angle
Equivalent steering angle at an imaginary wheel centered on the primary steering axle/reference.

### AVT Maximum Steering Angle
Adapter-specific AVT quantity derived/mapped according to AVT semantics.

These are not interchangeable fields.

## 7. Steering-wheel lock-to-lock turns

OEM value such as:
`2.4 turns lock-to-lock`

is a steering-wheel rotational specification.

It does not directly provide:
- actual road-wheel lock angle;
- AVT Maximum Steering Angle;
- AVT lock-to-lock time.

## 8. AVT lock-to-lock time

AVT lock-to-lock time is elapsed time from full steering lock in one direction to full lock in the opposite direction.

It behaves as a steering-transition/driver-model input.

Rules:
- forward and reverse times may differ;
- do not convert wheel turns to seconds without an explicit driver/steering-rate assumption;
- scenario assumptions are stored as AVT modelling assumptions, not OEM facts.

## 9. Rear / four-wheel steering

A rear-steer vehicle requires structural mapping of:

- steered axle;
- primary/secondary/linked role;
- maximum angle;
- phase behaviour;
- angle ratio/function;
- speed/mode dependence.

A simple `rear_steering=true` is insufficient for AVT readiness.

If the linkage function is unknown, fail closed rather than model it as a conventional fixed rear axle.

## 10. Body / plan envelope

Prefer engineering plan geometry where available.

Potential database roles:
- PLAN_BODY_ENVELOPE
- AVT_PLAN_PROFILE

Mirror inclusion must be explicit.

Different design checks may use different envelopes:
- conventional swept body;
- physical wall/mirror envelope.

Do not force one polygon to represent every clearance question.

## 11. Mapping result

Every AVT mapping result should carry:

- vehicle configuration/fitment;
- adapter version;
- target AVT version if relevant;
- mapped fields;
- source normalized-value IDs;
- derivation IDs where applicable;
- blockers;
- status.

Suggested status:
- READY
- PARTIAL
- BLOCKED
- NOT_APPLICABLE

## 12. Fail-closed examples

### BYD-type source
`Minimum turning radius = 5.35 m`

Without curb/wall definition:
- retain numeric turning observation;
- reference = OEM_UNSPECIFIED;
- do not populate AVT curb/wall field.

### Honda/Tesla steering turns
`2.4 turns lock-to-lock`

- valid steering-wheel-turns evidence;
- not AVT lock-to-lock seconds.

### OEM tread
`Front track = 1,575 mm`

- valid OEM observation with unresolved definition;
- not AVT outer-face track.

### Four-wheel steering
`Intelligent four-wheel steering`

- demonstrates rear steering exists;
- not enough to construct its AVT linkage unless angle/function/mode evidence is obtained.

## 13. Automated ATL/ATX boundary

Current research confirms official library/import workflows but does not establish a public supported serialization contract suitable for a production external ATL/ATX writer.

Therefore:
- no ATL/ATX reverse-engineering dependency in Phase 0;
- no claim about undocumented internal file encoding;
- test any future automation against an installed supported AVT environment behind a separate research/acceptance gate.
