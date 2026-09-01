# Wave 2A tranche 1 import qualification

Status: **PASS — Issue #34 qualification completed without manifest or importer changes**  
Date: 2026-09-01  
PR: #33 — Wave 2A: add engineering-use manifest tranche 1  
Branch: `chatgpt/wave2a-data-expansion`

## Revision qualified

- Accepted `main` base SHA: `5990666ab122d0da3cb89da48b8f92a6659f8b7e` (`Phase 4: add Windows local launcher for curated app (#31)`).
- Qualified PR head SHA (manifest/data head used for qualification): `75594c19c9fe16891d7edd0e25446820e6254f45`.
- The PR branch was rebased onto the accepted `main` tip before qualification. The 18 Wave 2A commits and all six manifests were preserved; the rebase completed without conflicts.
- This record is the only post-qualification content change. The final branch HEAD after committing this record is reported with the completion results.
- No manifest correction was necessary. All six manifests passed the existing contract unchanged.

## Staging procedure

The accepted 21-configuration build was created in a separately named disposable database:

```powershell
python scripts/build_wave1_curated_db.py `
  --staging vehicle_engineering_wave2a_baseline.staging.db `
  --csv vehicle_engineering_wave2a_baseline.csv `
  --xlsx vehicle_engineering_wave2a_baseline.xlsx `
  --no-promote
```

The controlled build performed Alembic upgrade, registry-only `app.curate init`, validation and create-only import of the three sentinels plus 18 accepted Wave 1 manifests, database QA, and export proof. The staging database was then extended with the six Wave 2A manifests using:

```powershell
$env:DATABASE_URL = "sqlite:///D:/R&D/thai-vehicle-engineering-db/vehicle_engineering_wave2a_baseline.staging.db"
python -m app.curate validate <manifest.json>
python -m app.curate import <manifest.json>
```

The normal `vehicle_engineering_curated.db` was not the staging target and was not promoted or replaced.

## Accepted baseline and final inventory

The registry-only initialization proof was **PASS**: 48 parameter definitions and 0 vehicle rows before controlled ingestion.

| Record | Accepted 21 baseline | Final 27 staging | Delta |
|---|---:|---:|---:|
| Vehicle configurations | 21 | 27 | +6 |
| Parameter definitions | 48 | 48 | 0 |
| Manufacturers | 13 | 15 | +2 |
| Vehicle models | 21 | 27 | +6 |
| Source documents | 54 | 74 | +20 |
| Source observations | 211 | 268 | +57 |
| Normalized values | 247 | 319 | +72 |
| Parameter assessments | 47 | 80 | +33 |
| Load conditions | 21 | 26 | +5 |
| Fitments | 14 | 14 | 0 |
| Axles | 0 | 0 | 0 |
| Steering relations | 0 | 0 | 0 |
| Geometry assets | 0 | 0 | 0 |
| Conflict decisions | 0 | 0 | 0 |
| Persisted readiness results | 140 | 164 | +24 |

Final inventory assertions:

- Exactly 27 vehicle configurations were present.
- All six new stable vehicle codes and all original 21 stable vehicle codes were present.
- All final identity verification states were `RESOLVED_EXACT`; no `HOLD` configuration was present.
- No stable vehicle code began with `FIXTURE-`; no Phase 0 fixture was present.
- There were 2 conflicting normalized values, unchanged from the accepted baseline, and 0 conflict decisions.
- There were 0 direct `DERIVED` or `ESTIMATED` normalized values.
- The six manifests supplied 20 unique new source documents; no source-code reuse or incompatible source metadata was encountered.

## Manifest validation and import

All six `python -m app.curate validate` commands returned `PASS` against the clean 21-vehicle staging database. All six create-only imports returned `PASS` and committed atomically.

| Manifest | Stable vehicle code | Validate | New sources | Observations | Values | Assessments | Loads | Fitments | Conflicts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `data/curation/manifests/wave2a/honda_crv_ehev_rs4wd_minorchange_release_20251128_v1.json` | `th-honda-crv-ehev-rs4wd-minorchange-release-2025-11-28` | PASS | 4 | 10 | 12 | 6 | 1 | 0 | 0 |
| `data/curation/manifests/wave2a/kia_carnival_hev_7seat_luxury_release_20251003_v1.json` | `th-kia-carnival-hev-7seat-luxury-release-2025-10-03` | PASS | 3 | 11 | 13 | 5 | 1 | 0 | 0 |
| `data/curation/manifests/wave2a/lexus_lm350h_executive_7seat_allnew_2023_v1.json` | `th-lexus-lm350h-executive-7seat-allnew-2023` | PASS | 4 | 9 | 13 | 5 | 0 | 0 | 0 |
| `data/curation/manifests/wave2a/nissan_serena_epower_highway_star_release_20250324_v1.json` | `th-nissan-serena-epower-highway-star-release-2025-03-24` | PASS | 3 | 10 | 10 | 7 | 1 | 0 | 0 |
| `data/curation/manifests/wave2a/toyota_corolla_cross_hev_premium_luxury_revision_2569_v1.json` | `th-toyota-corolla-cross-hev-premium-luxury-revision-2569` | PASS | 3 | 8 | 12 | 5 | 1 | 0 | 0 |
| `data/curation/manifests/wave2a/toyota_innova_zenix_hev_premium_revision_2568_v1.json` | `th-toyota-innova-zenix-hev-premium-revision-2568` | PASS | 3 | 9 | 12 | 5 | 1 | 0 | 0 |
| **Total** | **6 configurations** | **PASS** | **20** | **57** | **72** | **33** | **5** | **0** | **0** |

The existing validation and importer gates covered manifest schema, local references, registry codes and primitive types, units, evidence links, load/fitment scope, identity-time rules, source compatibility, create-only collision behavior, and rejection of direct `DERIVED`/`ESTIMATED` values.

## Semantic sentinel assertions

The following checks were executed against the final 27-vehicle staging database.

### Kia Carnival HEV 7-seat Luxury

- No `turning_radius_normalized_m` value was imported; the parameter remains assessment-only with `NOT_FOUND_AFTER_SEARCH`.
- All attached source documents were Thai-market (`market_code=TH`); no foreign-market turning value was introduced.
- `overall_width_reported_mm=1995` retains `width_envelope_definition=OEM_UNSPECIFIED`.
- OEM tread values `1739 / 1738 mm` remain `track_definition=OEM_UNSPECIFIED`; no AVT outer-face track values exist.

### Nissan Serena e-POWER Highway Star

- The raw observation `Approximate vehicle weight = 1797 kg` remains linked to `NISSAN_TH_SERENA_EPOWER_SPEC_CURRENT_20260901`.
- There is no `kerb_mass_kg` value; `kerb_mass_kg` remains an `UNKNOWN` assessment.
- `turning_radius_normalized_m=5.7` remains `RADIUS` with `turning_reference=OEM_UNSPECIFIED` and `turning_axle_scope=OEM_UNSPECIFIED`.

### Toyota Innova Zenix HEV Premium

- `identity_time_basis=OEM_REVISION_LABEL`; model-year fields remain null; the raw revision label containing Thai year 2568 was not converted to a model year.
- `turning_radius_normalized_m=5.7` remains `RADIUS` with OEM-unspecified reference and axle scope.
- OEM tread values `1550 / 1571 mm` remain `track_definition=OEM_UNSPECIFIED`; no AVT outer-face track values exist.

### Lexus LM 350h Executive 7-Seater

- `turning_radius_normalized_m=5.9` remains linked to the raw source label `Minimum Turning Radius (Tire)` from `LEXUS_TH_LM_CATALOG_2023`.
- The normalized turning reference is `WHEEL_PATH_OTHER`, with `turning_axle_scope=OEM_UNSPECIFIED`; it is not `CURB_TO_CURB` or `WALL_TO_WALL`.
- Explicitly sourced values remain `kerb_mass_kg=2345` and `gross_vehicle_mass_kg=2880`, both linked to the grouped OEM observation `Curb Weight / Gross Vehicle Weight`.

### Honda CR-V e:HEV RS 4WD

- No `overall_height_mm` value was imported; the parameter remains an `UNKNOWN` assessment. Design Check returns `INDETERMINATE` for the missing height.
- The raw grouped mass observation containing `1815 kg` remains preserved; there is no `kerb_mass_kg` value, which remains an `UNKNOWN` assessment.
- `clearance_value_mm=208` retains `clearance_type=OEM_MINIMUM_UNSPECIFIED` and load condition `OEM load state unspecified`; no load/reference semantics were inferred.
- `turning_radius_normalized_m=5.5` retains OEM-unspecified reference and axle scope.

### Toyota Corolla Cross HEV Premium Luxury

- `identity_time_basis=OEM_REVISION_LABEL`; model-year fields remain null; the raw revision label containing Thai year 2569 was not converted to a model year.
- `overall_width_reported_mm=1825` retains `width_envelope_definition=OEM_UNSPECIFIED`.
- OEM tread values `1559 / 1571 mm` remain `track_definition=OEM_UNSPECIFIED`; no AVT outer-face track values exist.
- `turning_radius_normalized_m=5.2` retains OEM-unspecified reference and axle scope.

## Existing-data preservation

The final staging database was compared with the untouched accepted local database `vehicle_engineering_curated.db` using stable vehicle code and semantic fingerprints, excluding generated UUIDs and timestamps where appropriate.

- 21 of 21 accepted vehicle identities matched.
- Existing source-document metadata matched for the accepted records.
- Existing source observations, load conditions, fitments, normalized values, parameter assessments, and readiness status/blocker semantics matched for all 21 accepted configurations.
- Existing conflicting-value semantics matched: 2 conflicting normalized values and 0 decisions.
- The accepted local database remained at 21 vehicles and was not overwritten. Its post-run SHA-256 was `F166000F9504E1E39E0B4A2A0C189BB9B70258818DB1F0863332FA4A57BFE063` (770,048 bytes; last write remained 2026-08-31 23:09:01).

## Application smoke

HTTP/TestClient smoke was run with `DATABASE_URL` pointing only to the 27-vehicle disposable staging database.

| Surface | Result |
|---|---|
| `/` | 307 redirect to `/vehicles` |
| `/vehicles` | 200 |
| `/api/vehicles` | 200; count 27; all six new codes present |
| Six new `/vehicles/<stable_vehicle_code>` detail pages | 200 for all six |
| `/compare` | 200; old BYD ATTO 3 and new Kia Carnival cross-comparison rendered together |
| `/design-check` | 200; active height/width/turning check rendered `INDETERMINATE` results |
| `/issues` | 200; new-vehicle assessments visible |
| `/api/issues` | 200; count 91; all six new vehicle codes represented |

Direct application design-check evaluation also covered all six new configurations:

- width with `BODY_EXCLUDING_MIRRORS`: `INDETERMINATE` for all six because OEM-unspecified reported width was not substituted for body width;
- curb-to-curb turning check: `INDETERMINATE` for all six because turning is absent or its OEM reference is not an exact curb-to-curb match;
- Honda CR-V height check: `INDETERMINATE` because `overall_height_mm` remains unknown;
- the other five new vehicles evaluated their published heights without changing the missing-width/turning fail-closed outcomes.

## Tests and evidence

- Controlled accepted 21-manifest build and export proof: **PASS**.
- Six Wave 2A CLI validations: **6/6 PASS**.
- Six Wave 2A create-only imports: **6/6 PASS**.
- Focused curation/import, accepted manifest inventory, and real-data Design Check tests: **34 passed** in 28.63 seconds.
- Full `python -m pytest`: **157 passed** in 81.36 seconds.
- GitHub Actions CI run [`33493641313`](https://github.com/bokoboss/thai-vehicle-engineering-db/actions/runs/33493641313): **success** for the pushed qualification commit; local test suite is also green.

## Limitations and release boundary

- The six records are qualified for controlled local create-only ingestion into the disposable 27-vehicle staging database. The normal accepted production-like local database remains at 21.
- None of the six new records is `AVT_READY` or `RAMP_SCREENING_READY`; missing AVT outer-face tracks, unresolved turning-envelope semantics, explicit AVT steering inputs, and approved ramp-screening angles remain intentional blockers.
- Honda CR-V height and kerb mass remain unknown/assessment-only; Nissan approximate weight remains raw evidence only; Kia turning remains unavailable.
- OEM width and tread labels were not promoted to body width or AVT outer-face track.
- No PR merge was performed.
