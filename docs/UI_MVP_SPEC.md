# Web UI MVP Specification

Status: Accepted control-plane specification  
Date: 2026-08-30

## Product rule

The UI exists to make engineering data easy to find, compare and audit.

It is not intended to be visually elaborate.

## Navigation

Keep primary navigation to:

1. **Vehicles**
2. **Compare**
3. **Data Issues**

Source/evidence detail is reached from vehicle pages rather than requiring a major top-level module.

## 1. Vehicles / Search

### Required
- search text box;
- manufacturer filter;
- model/body-type filter where available;
- readiness filter;
- compact result list/table.

### Result row
Show only useful identity fields:
- Make
- Model
- Generation / chassis where known
- Variant
- Model-year range
- body type
- compact readiness/status indicators

Do not show dozens of dimensions in search results.

## 2. Vehicle Detail

Header:
- Make / Model
- generation/chassis
- exact variant/configuration
- model-year / Thailand applicability
- readiness summary

Sections:

### Dimensions
- L / W / H
- width semantics
- wheelbase
- front/rear overhang
- track/tread fields
- wheel/tyre

### Turning & Steering
- OEM turning value + exact semantics
- curb/wall mapping if defensible
- actual wheel angle if known
- virtual-center/AVT steering value if known
- steering-wheel turns
- rear/secondary steering

### Clearance & Ramp
- clearance values grouped by clearance type
- load/ride-height condition
- OEM published ramp angles
- geometry-derived physical angles
- screening values clearly labelled as screening

### AVT
- readiness
- required AVT preparation fields
- missing semantic blockers
- adapter/mapping version

### Sources & Evidence
For each displayed engineering parameter allow expansion to:
- source
- raw label/value/unit
- evidence method
- applicability
- verification
- conflict state
- retrieval date
- decision/derivation lineage

Unknown is displayed explicitly, not as zero or blank ambiguity.

## 3. Compare

Compare 2–4 exact configurations.

Rows grouped by:
- overall geometry;
- axle/tyre;
- turning/steering;
- clearance/ramp;
- readiness.

Use:
- value;
- unit;
- concise status/source indicator.

Do not create charts in MVP.

## 4. Data Issues

Simple filters/table for:
- unresolved identity;
- missing high-value parameter;
- conflicting evidence;
- unknown turning semantics;
- AVT readiness blocker;
- stale/unverified source;
- failed validation.

This is primarily a maintainer/data-curation work queue.

## Status display

Use plain text/badges with unambiguous labels:
- Verified
- Published
- Measured
- Derived
- Estimated
- Conflict
- Unknown
- Not found
- Not applicable

Do not represent confidence using colour alone.

## Not required

- dashboard landing page;
- KPI charts;
- map;
- 3D model;
- interactive swept-path drawing;
- AI chatbot;
- user profiles;
- animations;
- dark-mode-specific design work;
- complex responsive mobile optimization.

Basic responsive usability is sufficient.

## Acceptance

A first-time engineer should be able to:
1. find a vehicle;
2. understand the exact configuration;
3. find a requested dimension/turning/clearance parameter;
4. determine whether it is verified, derived, conflicting or unknown;
5. inspect its evidence;
6. compare it with another vehicle;
7. export the evidence-aware data.

If those tasks are easy, the MVP UI is successful.
