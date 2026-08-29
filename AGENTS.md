# Agent Instructions

This repository contains engineering software **and engineering data**. Data integrity is a protected product behavior.

## Before changing anything
1. Read `PROJECT_PROFILE.md`.
2. Read the current Issue / execution contract.
3. Read the relevant documents under `docs/`, especially `VEHICLE_DATA_STANDARD.md`.
4. Inspect the actual repository state before editing.
5. For material schema, engineering-methodology or AVT-mapping changes, apply scrutiny before implementation.

## Non-negotiable data rules
- Never fabricate a vehicle dimension or parameter.
- Never turn an unknown value into a numeric estimate without explicitly classifying it as estimated and preserving the method.
- Never reinterpret an OEM label such as “turning radius” as curb-to-curb or wall-to-wall unless the source defines it or another authoritative source establishes the definition.
- Never assume vehicles with the same commercial model name share geometry across generations, markets, drivetrains, body styles or variants.
- Preserve raw source wording, original value/unit and provenance.
- Keep published, measured, derived and estimated values distinguishable.
- Conflicting evidence must be retained and surfaced; do not silently choose one value.
- Do not compute a “verified” approach, departure or breakover angle from global minimum ground clearance unless the required contact/clearance geometry is actually known.
- Do not infer maximum road-wheel angle from steering-wheel lock-to-lock alone.
- Autodesk Vehicle Tracking wheel-track semantics must not be populated directly from OEM tread/track-center values without an explicit mapping/derivation.

## Source policy
Prefer, in order appropriate to the parameter:
- Thai regulatory / official data where applicable;
- Thai OEM technical/specification material for the exact configuration;
- OEM regional/global technical material verified to match the same geometry;
- OEM service/body-repair/homologation material;
- reputable secondary technical sources only when primary evidence is unavailable;
- documented measurement or estimation with explicit method and limitations.

Source authority, exact vehicle applicability and evidence method are separate metadata.

## Engineering calculations
Every calculation intended for publication must have:
- formula/version identifier;
- required inputs and units;
- validity conditions;
- uncertainty/limitations;
- deterministic tests;
- provenance back to input observations.

## Completion
Implementation exists != accepted.

Report:
- exact branch/commit/PR;
- changed contracts/behavior;
- tests and evidence;
- unresolved data/methodology questions;
- any values or records that remain partial or unverified.

This project uses a lean adoption of:
https://github.com/bokoboss/engineering-development-workflow
