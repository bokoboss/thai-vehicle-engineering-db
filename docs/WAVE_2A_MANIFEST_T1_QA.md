# Wave 2A Manifest Tranche 1 QA

Status: **RESEARCH / STATIC CONTRACT PASS — importer validation pending**  
Date: 2026-09-01  
Issue: #32

## Scope

This tranche contains six new exact Thai-market engineering-use vehicle manifest drafts:

1. Kia Carnival HEV 7-seat Luxury — Thailand 2025 release
2. Nissan Serena e-POWER Highway Star — Thailand 2025 release
3. Toyota Innova Zenix HEV Premium — revision label 2568
4. Lexus LM 350h Executive 7-Seater — All-New Thailand 2023 release configuration
5. Honda CR-V e:HEV RS 4WD — late-2025 minor-change release
6. Toyota Corolla Cross HEV Premium Luxury — revision label 2569

These records are not yet part of the accepted curated database. Physical ingestion remains blocked until importer validation and independent acceptance review pass.

## Research gate result

All five records satisfy the current research gate for exact identity and explicit temporal basis.

| Vehicle | Identity-time basis | Research outcome |
|---|---|---|
| Kia Carnival HEV 7-seat Luxury | EDITION_RELEASE | PASS |
| Nissan Serena e-POWER Highway Star | EDITION_RELEASE | PASS |
| Toyota Innova Zenix HEV Premium | OEM_REVISION_LABEL | PASS |
| Lexus LM 350h Executive 7-Seater | EDITION_RELEASE | PASS |
| Honda CR-V e:HEV RS 4WD | EDITION_RELEASE | PASS with explicit unresolved height/mass assessments |
| Toyota Corolla Cross HEV Premium Luxury | OEM_REVISION_LABEL | PASS |

No model year was invented from publication, launch, brochure, retrieval or Buddhist-calendar revision year.

## Static manifest contract check

A registry/reference check was run across all five JSON manifests.

Checks:

- JSON parses successfully;
- unique local value identifiers;
- every parameter code exists in `data/reference/parameter_registry_v1.json`;
- canonical units match the registry;
- all registry-required semantic attributes are present;
- all required load-condition references resolve;
- all fitment references resolve;
- all evidence observation references resolve;
- all assessment parameter codes exist.

Result:

| Vehicle | Normalized values | Assessments | Static result |
|---|---:|---:|---|
| Kia Carnival HEV 7-seat Luxury | 13 | 5 | PASS |
| Nissan Serena e-POWER Highway Star | 10 | 7 | PASS |
| Toyota Innova Zenix HEV Premium | 12 | 5 | PASS |
| Lexus LM 350h Executive 7-Seater | 13 | 5 | PASS |
| Honda CR-V e:HEV RS 4WD | 12 | 6 | PASS |
| Toyota Corolla Cross HEV Premium Luxury | 12 | 5 | PASS |
| **Total** | **72** | **33** | **PASS** |

This static check does not replace `python -m app.curate validate`.

## Fail-closed semantic decisions

### Width

Generic OEM “overall width” values remain `overall_width_reported_mm` with:

`width_envelope_definition = OEM_UNSPECIFIED`

No generic width is promoted to body width or mirrors-open/folded width.

### OEM tread / track

Published tread/track remains:

- `oem_front_tread_or_track_mm`
- `oem_rear_tread_or_track_mm`

with `track_definition = OEM_UNSPECIFIED` unless the source establishes a stronger definition.

No value is converted to AVT outer-face track.

### Turning

- Nissan Serena: 5.7 m radius, reference/axle scope OEM_UNSPECIFIED.
- Toyota Innova Zenix: 5.7 m radius, reference/axle scope OEM_UNSPECIFIED.
- Honda CR-V: 5.5 m radius, reference/axle scope OEM_UNSPECIFIED.
- Lexus LM: source explicitly says “Minimum Turning Radius (Tire)”; stored as `WHEEL_PATH_OTHER`, not curb-to-curb/wall-to-wall.
- Kia Carnival: no defensible Thailand turning value found; assessment only.

No raw turning circle/radius wording is hand-converted beyond source-supported radius semantics.

### Ground clearance

Where a source publishes a single ground-clearance number without a load/reference definition:

- `clearance_type = OEM_MINIMUM_UNSPECIFIED`
- a structured `OEM_LOAD_STATE_UNSPECIFIED` load condition is used.

No physical approach/departure/breakover claim is derived.

### Mass

- Lexus LM has explicit OEM curb and gross vehicle weight values.
- Nissan Serena approximate vehicle weight 1,797 kg remains raw only; no kerb-mass normalization.
- Honda CR-V official 1,815 kg “น้ำหนักรถ” remains raw only in this tranche; no silent kerb-mass interpretation.

### Toyota Corolla Cross current-revision semantics

- current revision label is `OEM_REVISION_LABEL`, not model year;
- reported width remains OEM_UNSPECIFIED for body/mirror envelope;
- OEM tread remains separate from AVT outer-face track;
- ground-clearance load/reference state remains unspecified;
- turning radius 5.2 m remains OEM_UNSPECIFIED for curb/wall and axle scope.

### Honda CR-V explicit gaps

The exact RS 4WD record deliberately leaves:

- `overall_height_mm` UNKNOWN because the flattened first-party grouped table did not preserve a sufficiently robust exact member association for this curation pass;
- `kerb_mass_kg` UNKNOWN because first-party mass-basis wording is not explicit.

This is intentional and not a data-entry omission.

## Required next gate

Before merge/ingestion:

1. run `python -m app.curate validate` on all six manifests against an initialized clean database;
2. verify no source-code collision or incompatible source reuse;
3. import all five into a disposable staging database;
4. confirm transaction/rollback behavior and readiness outputs;
5. confirm existing 21 accepted configurations remain unchanged;
6. run full pytest;
7. run web smoke for Vehicles / Compare / Design Check;
8. independently review the resulting PR and qualification output.

Only after these gates pass should the production-like curated inventory increase from 21 to 27 configurations.
