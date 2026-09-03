# Wave 2C tranche 1 import qualification

Status: **PASS — Issue #52 qualification completed**

Date: 2026-09-03

Issue: [#52](https://github.com/bokoboss/thai-vehicle-engineering-db/issues/52)

PR: [#51](https://github.com/bokoboss/thai-vehicle-engineering-db/pull/51)

Branch: `chatgpt/wave2c-data-expansion`

## Qualification scope

Issue #52 was the authoritative contract. This was a data-only qualification
of the accepted create-only curation importer from the accepted
`release_2026_09_c` 39-configuration baseline to a disposable 41-configuration
staging database.

No new automotive research was performed. No accepted release, normal release
pointer, accepted database, builder, application, launcher or test source was
changed. PR #51 was not merged.

## Revision and preflight gate

- Accepted `main` SHA: `a141dd4dbb09b5fa11e681959f78d68d09c54e6a`.
- Starting PR #51 HEAD: `d5467fdb97f4e0c7cc83cdb132390ed5401ea04c`.
- `origin/main`, `origin/pr/51/head`, and
  `origin/chatgpt/wave2c-data-expansion` were fetched and verified at the
  expected SHAs.
- The worktree was clean before qualification and was at the expected
  starting HEAD.
- `data/curation/releases/current_release.json` was unchanged; its SHA-256
  was `77e16ba4cfd2b7891625b41ccc35649547afa56a4a65cc06bbc82220e757cb54`
  before qualification and remained unchanged.
- `vehicle_engineering_curated.db` was absent from this worktree before and
  after qualification. It was never used as an import target or replaced.

The final branch HEAD is the qualification commit reported with the completion
result. As with prior qualification records, this document cannot embed the
hash of the commit that contains the document itself.

## Staging procedure

The accepted release definition was built explicitly into a disposable DB with
`--no-promote`:

```text
python scripts/build_curated_db.py --release data/curation/releases/release_2026_09_c.json --staging vehicle_engineering_wave2c_t1_issue52.baseline39.staging.db --final vehicle_engineering_curated.db --csv vehicle_engineering_wave2c_t1_issue52.baseline39.csv --xlsx vehicle_engineering_wave2c_t1_issue52.baseline39.xlsx --qualification vehicle_engineering_wave2c_t1_issue52.baseline39.qualification.json --no-promote
```

The clean baseline build passed registry-only initialization (48 parameters,
zero vehicles), validation/import of all 39 listed manifests, database QA and
CSV/XLSX export proof. The two Wave 2C manifests were then validated and
imported into that disposable staging DB through `python -m app.curate`:

```text
python -m app.curate validate data/curation/manifests/wave2c/mercedes_s350d_exclusive_sale_snapshot_20260903_v1.json
python -m app.curate validate data/curation/manifests/wave2c/bmw_x7_xdrive40d_m_sport_sale_snapshot_20260903_v1.json
python -m app.curate import data/curation/manifests/wave2c/mercedes_s350d_exclusive_sale_snapshot_20260903_v1.json
python -m app.curate import data/curation/manifests/wave2c/bmw_x7_xdrive40d_m_sport_sale_snapshot_20260903_v1.json
```

Both validate commands and both create-only imports returned **PASS**. The
repository database QA was also rerun against a synthetic 41-manifest
inventory in memory; no 41-vehicle release definition was created.

## Manifest and database deltas

| Record | 39 baseline | Final staging | Delta |
|---|---:|---:|---:|
| Vehicle configurations | 39 | 41 | **+2** |
| Parameter definitions | 48 | 48 | 0 |
| Manufacturers | 20 | 21 | +1 |
| Vehicle models | 39 | 41 | +2 |
| Source documents | 105 | 107 | **+2** |
| Source entries in manifests | 106 | 108 | +2 |
| Source observations | 347 | 354 | **+7** |
| Normalized values | 458 | 466 | **+8** |
| Parameter assessments | 145 | 158 | **+13** |
| Load conditions | 34 | 34 | **+0** |
| Fitments | 14 | 14 | 0 |
| Axles | 0 | 0 | 0 |
| Steering relations | 0 | 0 | 0 |
| Geometry assets | 0 | 0 | 0 |
| Conflict decisions | 0 | 0 | 0 |
| Conflicting normalized values | 2 | 2 | 0 |
| Evidence links | 462 | 470 | +8 |
| Persisted readiness results | 212 | 220 | +8 |

| Manifest | Stable vehicle code | Validate | Import | Sources | Observations | Values | Assessments | Loads |
|---|---|---|---|---:|---:|---:|---:|---:|
| `mercedes_s350d_exclusive_sale_snapshot_20260903_v1.json` | `th-mercedes-s350d-exclusive-sale-snapshot-2026-09-03` | PASS | PASS | +1 | +4 | +4 | +6 | +0 |
| `bmw_x7_xdrive40d_m_sport_sale_snapshot_20260903_v1.json` | `th-bmw-x7-xdrive40d-m-sport-sale-snapshot-2026-09-03` | PASS | PASS | +1 | +3 | +4 | +7 | +0 |
| **Total** | **2 configurations** | **2/2 PASS** | **2/2 PASS** | **+2** | **+7** | **+8** | **+13** | **+0** |

The final staging database had 41 unique stable codes, no `HOLD` identity, no
`FIXTURE-` identity, no direct `DERIVED` or `ESTIMATED` normalized values, and
the two pre-existing conflicting normalized values remained unresolved with
zero conflict decisions.

Stable-code inventory digests:

- Baseline 39: `569f171065c44e9aec610d5a59657e7cb54d093479e5c44a72ac1cb99970c460`.
- Final 41: `923c5607f4789a44368172cfe88c9fe1c6190ab2e895e61476430c1546258306`.
- The only added codes were the two codes listed above.

## Existing-data preservation

Each vehicle was represented by a canonical JSON semantic snapshot keyed by
stable vehicle code. The snapshot covered:

- identity, temporal basis, manufacturer and model;
- source documents and raw observations;
- normalized typed values, semantic metadata and evidence links;
- parameter assessments and readiness status/blocker semantics;
- loads, fitments, axles, steering relations and geometry assets;
- conflict decisions; and
- derivation, QA and AVT records where present.

Generated database IDs and generated lifecycle timestamps were excluded from
the fingerprint. Stable source codes, raw source wording, source/observation
timestamps, typed values, evidence state, semantic metadata and readiness
semantics were retained. Per-vehicle SHA-256 fingerprints were compared across
the clean baseline DB and the final 41-record DB.

- **39/39 original semantic fingerprints unchanged.**
- Missing original stable codes: none.
- Unexpected final codes: exactly the two intended Wave 2C additions.
- Baseline original-39 fingerprint digest:
  `8c7012745d238109e63bf5cac483381373642ba4bb4389c11f00824665a59035`.
- Final original-39 fingerprint digest:
  `8c7012745d238109e63bf5cac483381373642ba4bb4389c11f00824665a59035`.
- Preservation digest: the matching digest above.

## Mandatory semantic sentinels

Both sentinel suites returned **PASS**.

### Mercedes-Benz S 350 d Exclusive

- Identity basis is `SALE_PERIOD`; sale snapshot is exactly 2026-09-03 to
  2026-09-03; model-year fields remain null and no model year was inferred.
- Published normalized values are length **5289 mm**, mirrors-open width
  **2109 mm**, height **1503 mm**, and kerb mass **2020 kg**.
- Width carries explicit `width_envelope_definition=INCLUDING_MIRRORS_OPEN`.
- The raw mass label preserves the OEM EU kerb semantics.
- The raw `AIRMATIC` observation is retained; it does not create a clearance
  value or ride-height claim.
- Body-excluding-mirrors width, wheelbase, clearance, turning, and AVT
  outer-face tracks remain absent as normalized values and are represented by
  six assessments where applicable.
- No load, fitment, axle, steering-relation or geometry record was created.

### BMW X7 xDrive40d M Sport

- Identity basis is `SALE_PERIOD`; sale snapshot is exactly 2026-09-03 to
  2026-09-03; model-year fields remain null and no model year was inferred.
- Published normalized values are length **5181 mm**, reported width **2000
  mm**, height **1835 mm**, and wheelbase **3105 mm**.
- Width carries explicit `width_envelope_definition=OEM_UNSPECIFIED`; no body
  or mirrors-open width was inferred.
- The raw **2565 kg** observation retains the OEM EC ready-to-drive wording
  (including the stated fuel/driver basis). It remains observation-only; there
  is no `kerb_mass_kg=2565` and no kerb-mass normalized value.
- Body/mirrors-open width, clearance, turning and AVT outer-face tracks remain
  absent as normalized values and are represented by seven assessments where
  applicable.
- No load, fitment, axle, steering-relation or geometry record was created.

Neither new record contains a direct derived or estimated value. Both remain
`AVT_READY=NOT_READY` and `RAMP_SCREENING_READY=NOT_READY`.

## Application and export smoke

The existing application was exercised with `DATABASE_URL` pointing only to
the disposable 41-vehicle staging DB. No application source change was made.

| Surface | Result |
|---|---|
| `/healthz` | 200 |
| `/` | 307 redirect to `/vehicles` |
| `/vehicles` | 200 |
| `/api/vehicles` | 200; count **41**; both new codes present |
| Both detail APIs | 200; S-Class 4 values/6 assessments; X7 4 values/7 assessments |
| Both detail pages | 200 |
| `/compare` | 200; both new codes rendered together |
| `/design-check` | 200 for both; width and turning checks `INDETERMINATE` |
| `/issues` | 200 |
| `/api/issues` | 200; 123 issue rows; both new codes represented |
| Full CSV export | 200; 624 rows, 41 vehicles, 308,924 bytes |
| Full XLSX export | 200; 624 readable rows, 41 vehicles, 113,238 bytes |

Direct Design Check assertions confirmed:

- the S-Class mirrors-open width is not substituted for body width;
- the X7 OEM-unspecified width is not substituted for body or mirrors width;
- missing turning remains `INDETERMINATE` for both; and
- missing clearance remains assessment-only and is not exposed as a design
  candidate.

## Tests and CI

Focused importer/release/design/application/export/launcher tests:

```text
python -m pytest tests/integration/test_curation_importer.py tests/contract/test_release_definition.py tests/contract/test_current_release_pointer.py tests/integration/test_curated_release_builder.py tests/unit/test_design_check.py tests/integration/test_design_check_real.py tests/integration/test_generic_release_application.py tests/integration/test_api_and_exports.py tests/unit/test_local_runner.py
107 passed in 65.12s
```

Full test suite:

```text
python -m pytest
190 passed in 127.56s
```

Post-push GitHub Actions CI was pending when this artifact was first authored;
the final CI run and exact URL are returned with the completion result. The
qualification is not a release promotion.

## Release and repository boundaries

- `data/curation/releases/current_release.json` was not changed.
- No 41-vehicle release definition was created.
- `vehicle_engineering_curated.db` was not created, promoted, overwritten or
  used as an import target in this worktree.
- No builder, application, launcher or test source was modified.
- Only the requested qualification artifact was added to the branch; the two
  Wave 2C manifests and research QA already existed at the expected starting
  HEAD.
- No merge or promotion was performed.

## Limitations and unresolved data/methodology questions

- The S 350 d record is qualified only as the bounded 2026-09-03 sale-period
  snapshot. It is not a model-year or continuous-sale assertion.
- The S-Class body width, wheelbase, clearance, turning value and AVT track
  remain unresolved. AIRMATIC presence does not establish clearance.
- The X7 2,000 mm width remains OEM-unspecified. Body and mirrors-open widths,
  clearance, turning value and AVT tracks remain unresolved.
- The X7 2,565 kg value is EC ready-to-drive mass only; a separate kerb-mass
  value remains unresolved.
- Neither addition is AVT-ready or ramp-screening-ready. OEM width labels are
  not body envelopes, OEM tread/track is not AVT outer-face track, and no
  steering/ramp/geometry inference was introduced.
- These records are qualified for controlled local create-only ingestion into
  disposable staging only. They are not members of the accepted release until
  a separate release qualification and explicit pointer update are approved.
