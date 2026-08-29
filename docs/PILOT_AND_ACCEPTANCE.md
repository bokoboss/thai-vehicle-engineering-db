# Pilot Dataset and Acceptance Gates v1.0

Status: Draft  
Date: 2026-08-29

## 1. Purpose

Prove the data standard and software architecture with a deliberately difficult cross-section of Thai-market vehicles before scaling the database.

## 2. Pilot selection criteria

The pilot should contain approximately 20–30 exact configurations and collectively exercise:

- small sedan/hatchback;
- medium/large sedan;
- crossover/SUV;
- pickup;
- large MPV;
- van;
- EV with battery-underfloor clearance concerns;
- luxury long-wheelbase vehicle;
- variants with different tyre packages;
- records where turning semantics are well specified;
- records where turning semantics are ambiguous;
- records with missing overhang;
- records with loaded/unloaded clearance distinctions;
- at least one evidence conflict requiring resolution.

Model families should be drawn from vehicles relevant to Thailand (e.g. common Toyota, Honda, Isuzu, Ford, Mitsubishi, Nissan, Mazda, BYD, MG, GWM, Tesla, Mercedes-Benz, BMW), but exact configurations are selected only after source discovery.

## 3. Pilot research workflow

For each candidate:

1. Resolve exact Thai-market identity.
2. Collect Thai OEM primary source first where available.
3. Search OEM technical/service/homologation material for missing geometry.
4. Preserve every useful raw observation.
5. Normalize only when parameter semantics are adequate.
6. Run deterministic QA.
7. Record unresolved fields explicitly.
8. Determine readiness by use case.
9. Independently review a sample of high-risk fields.

## 4. Minimum evidence expectations

Every pilot vehicle:
- exact identity evidence;
- overall L/W/H;
- wheelbase;
- tyre/wheel configuration;
- at least one source document;
- parameter-level provenance.

At least 10 pilot vehicles:
- turning data sufficient to test AVT mapping logic.

At least 5:
- front/rear overhang evidence or geometry sufficient to test longitudinal body positioning.

At least 5:
- ground-clearance/load-state data sufficient to test ramp-screening semantics.

At least 3:
- body outline or dimension drawing suitable for testing richer geometry storage.

## 5. Foundation acceptance gates

### F1 — Identity contract
PASS when generation/market/variant separation rules can represent all pilot candidates without ambiguous merging.

### F2 — Evidence contract
PASS when each normalized value can trace back to raw observation(s) and source metadata.

### F3 — Conflict handling
PASS when contradictory sources can coexist and the preferred value is chosen only through an auditable decision.

### F4 — AVT semantics
PASS when OEM tread/track, AVT outer-face track, curb-to-curb, wall-to-wall and unknown turning definitions cannot be accidentally conflated by the schema/API.

### F5 — Derived engineering values
PASS when derivations carry rule versions, input evidence and deterministic tests and invalid-input cases fail closed.

### F6 — UI honesty
PASS when unknown/conflicting/estimated values are visually distinguishable from verified values.

### F7 — Export integrity
PASS when exported Excel/CSV retains value status and source identifiers rather than exporting naked numbers.

## 6. Phase 0 software acceptance gates

- schema migration up/down or reproducible initialization;
- typed validation for all v1 entities;
- deterministic fixtures demonstrating published, derived, unknown and conflicting values;
- unit/contract tests;
- basic search/detail API;
- no large source files committed accidentally;
- CI green;
- documented local startup;
- architecture review against `PROJECT_PROFILE.md`.

## 7. Pilot completion criteria

The pilot is complete when:
- 20–30 exact configurations are represented;
- every numeric value has a provenance/status chain;
- no known ambiguous turning parameter is silently labelled curb-to-curb/wall-to-wall;
- no AVT track is populated directly from OEM centerline tread without explicit mapping;
- readiness rules produce explainable results;
- at least one engineer can use the web UI to answer a vehicle comparison question and trace the result to source evidence.

## 8. Scale-up gate

Do not begin hundreds-of-model bulk population until:
- pilot schema changes have stabilized;
- recurring source patterns are identified;
- ingestion helpers can create observations without bypassing QA;
- conflict and identity workflows have been exercised;
- data quality metrics are visible.
