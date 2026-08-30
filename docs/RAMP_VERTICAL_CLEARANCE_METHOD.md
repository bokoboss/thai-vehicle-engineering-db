# Ramp and Vertical Clearance Methodology v1

Status: Engineering methodology foundation  
Date: 2026-08-30

## 1. Purpose

Define how the vehicle database should support parking/access ramp questions without turning generic ground-clearance specifications into false physical ramp-capability claims.

This document defines data/method classes. It does not implement a ramp solver.

## 2. Central principle

A physical approach/departure/breakover limit is a **contact-geometry problem**.

A single global minimum ground-clearance number is normally insufficient.

## 3. Result classes

### Level A — OEM published

Examples:
- OEM approach angle;
- OEM departure angle;
- OEM breakover/ramp-over angle.

Store using:
- `oem_published_approach_angle_deg`
- `oem_published_departure_angle_deg`
- `oem_published_breakover_angle_deg`

Preserve OEM load-state/definition ambiguity when not stated.

### Level B — Geometry-derived physical

Calculated from geometry sufficient to reproduce the chosen physical definition.

Store using:
- `geometry_derived_approach_angle_deg`
- `geometry_derived_departure_angle_deg`
- `geometry_derived_breakover_angle_deg`

Required inputs depend on rule but normally include:
- axle/contact geometry;
- actual limiting lower-envelope point(s);
- static-loaded tyre radius;
- load/ride-height state.

### Level C — Engineering screening

Simplified idealized calculation from controlled incomplete geometry.

Store only as:
- `screening_front_contact_angle_deg`
- `screening_rear_contact_angle_deg`
- `screening_breakover_angle_deg`
- `screening_breakover_symmetric_angle_deg`

Never promote these into OEM/physical parameter codes.

### Level D — Insufficient evidence

No defensible numeric result.

Report unknown and identify required missing geometry.

## 4. Clearance taxonomy

Treat these as potentially different engineering quantities:

- OEM minimum unspecified
- running clearance
- between-axles clearance
- front axle clearance
- rear axle clearance
- differential clearance
- battery-pack clearance
- component-specific clearance

They must not be collapsed merely because all are measured in millimetres.

## 5. Load condition

Relevant geometry may depend on:

- kerb/unladen/laden/GVW state;
- occupants;
- payload;
- axle load;
- tyre pressure;
- suspension mode;
- air-suspension/ride-height setting.

Preserve source wording and structured applicability.

## 6. Static-loaded tyre radius

For physical tangent/contact geometry, static-loaded tyre radius is distinct from:
- nominal tyre outside radius;
- unloaded tyre radius derived from tyre notation.

Store front/rear loaded radius separately with:
- load;
- pressure;
- source/measurement;
- uncertainty.

## 7. Lower-envelope geometry

A normal side silhouette is not enough.

Geometry roles should distinguish:

### Front lower envelope
Potential bumper/splitter/front-body contact.

### Between-axles lower envelope
Potential:
- battery enclosure;
- exhaust;
- crossmember;
- differential;
- undertray;
- chassis component.

### Rear lower envelope
Potential rear bumper/diffuser/body contact.

### Underbody low points
Discrete engineering contact candidates when a continuous profile is unavailable.

## 8. Screening geometry

A simplified front contact screening angle may use:

```text
alpha_screen = atan(h_f / a_f)
```

where:
- `h_f` = assumed clearance at the actual assumed front limiting point;
- `a_f` = horizontal distance from front wheel/road contact reference to that same limiting point.

This is **not valid** if:
- global minimum clearance is substituted for front-point clearance without evidence;
- overall overhang is used even though the limiting low point is elsewhere.

Analogous logic applies to rear screening.

An idealized breakover screening angle for a limiting point at distance `x` over wheel-contact separation `L` and height `h` may be represented as:

```text
beta_screen = atan(h/x) + atan(h/(L-x))
```

For a deliberately symmetric midpoint assumption:

```text
beta_screen_symmetric = 2 * atan(2h/L)
```

These are screening constructions only unless the assumed geometry reproduces the actual physical limiting geometry.

## 9. Future 2D longitudinal ramp check

For ordinary straight longitudinal parking-ramp negotiation with negligible crossfall/twist, a quasi-static 2D side-profile method is a defensible routine engineering model if its assumptions are explicit.

### Minimum vehicle inputs

- front/rear axle centers;
- static-loaded tyre radii;
- wheelbase;
- front lower envelope;
- between-axle lower envelope;
- rear lower envelope;
- coordinate datum;
- load/ride-height state;
- geometry fidelity/uncertainty.

### Road input

A piecewise-linear or curved vertical alignment.

### Proposed algorithm

1. place tyre/wheel contact geometry on the road profile;
2. solve rigid vehicle pose at successive longitudinal stations;
3. transform lower-envelope geometry into road coordinates;
4. calculate intersection/minimum signed clearance;
5. identify limiting vehicle point/component;
6. identify road station/segment;
7. propagate uncertainty/tolerance.

### Output states

- CLEAR
- INTERFERENCE
- INDETERMINATE_WITH_UNCERTAINTY

## 10. When 2D is insufficient

Do not claim 2D longitudinal proof when material control comes from:

- diagonal approach;
- crossfall;
- one-wheel articulation;
- suspension compression/rebound;
- dynamic pitch;
- tyre deformation beyond model assumptions;
- lateral underbody variation;
- a localized 3D obstruction.

## 11. EV considerations

EVs do not require a different geometric theory, but the underfloor battery can be:

- large;
- flat;
- relatively low;
- safety-critical.

Therefore a generic single ground-clearance value can be particularly misleading for detailed interference checks.

## 12. Phase boundary

Phase 0:
- store the semantics and geometry roles needed later;
- no ramp solver.

Later ramp module:
- implemented only after real lower-envelope data/measurement workflows are proven;
- independently validated against known vehicle/ramp cases before client-facing use.
