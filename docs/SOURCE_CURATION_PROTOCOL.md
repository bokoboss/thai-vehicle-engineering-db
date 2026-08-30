# Source Curation Protocol v1

Status: Accepted control-plane procedure  
Date: 2026-08-30

## 1. Objective

Create engineering-grade vehicle records from heterogeneous public/official sources without silently inventing identity, semantics or precision.

## 2. Curation unit

Curate one **exact vehicle configuration + material fitment** at a time.

Do not start by filling a spreadsheet row labelled only with a commercial model name.

## 3. Stage 1 — Identity resolution

Before normalizing engineering values, establish:

- manufacturer;
- commercial model;
- market;
- generation/chassis/platform where known;
- model-year/sale-period applicability;
- exact grade/variant;
- powertrain/drivetrain where material;
- wheel/tyre package;
- equipment package where steering/ride height/body geometry differs.

### Identity outcomes

- RESOLVED_EXACT
- RESOLVED_SAME_GEOMETRY_GROUP
- PARTIAL
- UNRESOLVED

Only the first two may support an exact engineering configuration, and SAME_GEOMETRY_GROUP requires evidence of equivalence.

## 4. Stage 2 — Source registration

For every source capture:

- publisher;
- authority class;
- title;
- market;
- source type;
- URL;
- retrieval date;
- page/section;
- publication/model year if known;
- local snapshot/hash where retained;
- access/licensing notes;
- applicability notes.

A URL alone is not sufficient provenance.

## 5. Stage 3 — Raw observation extraction

Record what the source says before interpretation:

- raw label;
- raw value;
- raw unit;
- qualifiers;
- page/table location;
- exact grade/column applicability;
- source-reported precision;
- extraction method;
- ambiguity note.

### Important rule

If table parsing loses column association, preserve the grouped values and mark the association unresolved.

Do not assign a value to a grade because it “looks obvious” unless the original table structure verifies the mapping.

## 6. Stage 4 — Semantic normalization

Normalize only when the source supports the parameter definition.

Examples:

### Safe
`Wheelbase = 2,310 mm`
-> `wheelbase_actual_mm = 2310`

provided identity and axle definition are unambiguous.

### Unsafe
`Minimum turning radius = 5.35 m`
-> `CURB_TO_CURB radius = 5.35 m`

unless the source defines curb/kerb reference.

### Unsafe
`Front track = 1575 mm`
-> `AVT front outer-face track = 1575 mm`

unless the source definition matches AVT outer tyre faces.

## 7. Stage 5 — Evidence and state assignment

Assign independently:

- evidence method;
- authority/applicability;
- resolution/conflict state;
- verification state;
- availability state;
- uncertainty/precision.

Do not encode all of these into one confidence/status field.

## 8. Stage 6 — Controlled derivations

Run only registered derivation rules.

A derivation record must identify:
- rule/version;
- input value IDs;
- formula;
- validity conditions;
- output parameter;
- uncertainty/limitations.

## 9. Stage 7 — Readiness evaluation

Evaluate readiness after curation, never as a manual badge.

Examples:
- AVT_READY
- RAMP_SCREENING_READY
- VERTICAL_CLEARANCE_READY
- CLIENT_REFERENCE_READY

A record may be dimension-ready while not AVT-ready.

## 10. Source-search order

Prefer:

1. Thai government/regulatory evidence where relevant;
2. exact Thai OEM source;
3. official Thai importer/distributor source;
4. exact OEM service/technical/homologation source;
5. same-geometry OEM source in another market with demonstrated equivalence;
6. reputable secondary technical source;
7. controlled physical measurement;
8. estimate only when explicitly useful and clearly classified.

Physical measurement is not intrinsically “lower” quality; its authority depends on procedure, calibration, configuration and measurement uncertainty.

## 11. Search for difficult parameters

### Overhang / axle datum
Look for:
- dimension drawing;
- body repair manual;
- body-builder guide;
- homologation drawing.

### Actual wheel angle / steering geometry
Look for:
- workshop alignment/steering manual;
- OEM technical manual;
- controlled measurement.

### AVT outer-face track
Look for:
- explicit outer-tyre-face drawing;
- mounted wheel/tyre geometry;
- physical survey.

Do not rely on nominal tyre section width alone.

### Lower envelope / ramp
Look for:
- OEM underbody/body repair drawing;
- homologation geometry;
- CAD;
- controlled physical profile survey.

## 12. Conflicts

When two credible sources disagree:

1. confirm exact identity;
2. confirm unit and radius/diameter semantics;
3. confirm load state;
4. confirm source date/model year;
5. retain both observations;
6. create a conflict decision only when evidence supports preference.

Never “average” conflicting dimensions.

## 13. Missing data

A missing value should become a parameter assessment containing:
- unknown reason;
- source families searched;
- search date;
- next best source;
- whether it blocks a readiness state.

## 14. Pilot QA sampling

For the first 30 vehicles:

- independent second review of all turning semantics;
- independent review of any AVT outer-face track;
- independent review of rear/four-wheel steering;
- independent review of geometry-derived ramp fields;
- random second review of at least 20% of basic dimensions.

## 15. Publication rule

A client-visible value must be able to answer:

> What exactly does this number mean, what exact vehicle does it apply to, where did it come from, and is it published, measured, derived, estimated, conflicting or unknown?

If the system cannot answer all four, it is not ready to publish as an engineering fact.
