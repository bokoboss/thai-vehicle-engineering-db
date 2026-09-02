# Wave 2B tranche 2 import qualification

Status: **PASS — Issue #46 qualification completed**  
Date: 2026-09-02  
PR: #45 — Wave 2B tranche 2: add premium MPV and supercar engineering manifests  
Branch: `chatgpt/wave2b-tranche2-data-expansion`

## Qualification scope

Issue #46 was the authoritative qualification contract. This was a data-only
qualification of the existing create-only curation importer. No new automotive
research was performed, no accepted release was changed, and PR #45 was not
merged.

The five manifests qualified were:

1. DENZA D9 Performance AWD
2. Ferrari 296 GTB
3. McLaren Artura Coupe
4. Lamborghini Urus SE
5. Ferrari Purosangue

## Revision qualified

- Accepted `main` base SHA: `185bb0daffd10409c74033ed9f5715da20c1015c`.
- Starting PR #45 HEAD: `e4efd15a1592a7ff9b2fc8ac16734aab47863890`.
- The required remote fetch and clean-worktree gate passed before qualification.
- `origin/main`, `origin/chatgpt/wave2b-tranche2-data-expansion`, and
  `refs/pull/45/head` were verified at the expected SHAs before staging.
- Final branch HEAD is the tip containing this qualification record; its exact
  SHA is returned with the completion result because a commit cannot embed its
  own final hash. No merge was performed.

## Accepted 34-configuration baseline

The explicit accepted release definition
`data/curation/releases/release_2026_09_b.json` was rebuilt with the generic
release builder into a disposable staging database using `--no-promote`.
The accepted database was not an import target.

Registry-only initialization passed with 48 parameter definitions and zero
vehicle rows before release ingestion. The accepted release build then passed
validation, create-only import, database QA, readiness re-evaluation, and CSV/
XLSX export proof.

| Record | Baseline |
|---|---:|
| Vehicle configurations | 34 |
| Parameter definitions | 48 |
| Manufacturers | 17 |
| Vehicle models | 34 |
| Source documents | 91 |
| Source entries in manifests | 92 |
| Source observations | 317 |
| Normalized values | 405 |
| Parameter assessments | 116 |
| Load conditions | 32 |
| Fitments | 14 |
| Axles | 0 |
| Steering relations | 0 |
| Geometry assets | 0 |
| Conflict decisions | 0 |
| Conflicting normalized values | 2 |
| Persisted readiness results | 192 |

Baseline stable-code inventory matched the 34 manifests in
`release_2026_09_b`:

- stable-code digest: `5f374d05e282e71c335250e487014bbf9eb6d514ba685177c4b486b3842cf09a`
- no `HOLD` identity;
- no `FIXTURE-` / Phase 0 fixture configuration;
- no direct `DERIVED` or `ESTIMATED` normalized value;
- two existing conflicting normalized values and zero conflict decisions were
  retained.

The clean baseline staging database was 1,028,096 bytes with SHA-256
`6B15090D93A6077DE69D2A0D17D86BE952CA337D2BB2F2C4DDB5F9446CE4DD6E`.

## Manifest validation and create-only import

All five manifests returned **PASS** from
`python -m app.curate validate <manifest>` against the clean accepted-34
staging database. All five create-only imports committed atomically into the
same disposable staging database.

| Manifest | Stable vehicle code | Validate | Import | Sources created | Sources reused | Observations | Values | Assessments | Loads |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| `denza_d9_performance_awd_launch_20241101_v1.json` | `th-denza-d9-performance-awd-launch-2024-11-01` | PASS | PASS | 2 | 0 | 8 | 15 | 4 | 2 |
| `ferrari_296_gtb_thailand_premiere_202204_v1.json` | `th-ferrari-296-gtb-thailand-premiere-2022-04` | PASS | PASS | 3 | 0 | 6 | 10 | 7 | 0 |
| `mclaren_artura_coupe_launch_20221219_v1.json` | `th-mclaren-artura-coupe-launch-2022-12-19` | PASS | PASS | 3 | 0 | 4 | 5 | 6 | 0 |
| `lamborghini_urus_se_th_launch_20240522_v1.json` | `th-lamborghini-urus-se-launch-2024-05-22` | PASS | PASS | 3 | 0 | 6 | 13 | 5 | 0 |
| `ferrari_purosangue_th_premiere_20230407_v1.json` | `th-ferrari-purosangue-thailand-premiere-2023-04-07` | PASS | PASS | 3 | 0 | 6 | 10 | 7 | 0 |
| **Total** | **5 configurations** | **5/5 PASS** | **5/5 PASS** | **14** | **0** | **30** | **53** | **29** | **2** |

The final disposable staging inventory was **39 configurations**. The new
manifest/source/observation deltas were:

| Record | Baseline | Final staging | Delta |
|---|---:|---:|---:|
| Vehicle configurations | 34 | 39 | +5 |
| Source documents | 91 | 105 | +14 |
| Source entries in manifests | 92 | 106 | +14 |
| Source observations | 317 | 347 | +30 |
| Normalized values | 405 | 458 | **+53** |
| Parameter assessments | 116 | 145 | **+29** |
| Load conditions | 32 | 34 | **+2** |

All 34 original stable codes remained present exactly once. Each of the five
new stable codes appeared exactly once. The combined 39-code inventory digest
was `569f171065c44e9aec610d5a59657e7cb54d093479e5c44a72ac1cb99970c460`.
The final staging database had 105 unique source codes from 106 manifest source
entries.

Final database QA passed with these counts:

| Record | Final staging |
|---|---:|
| Vehicle configurations | 39 |
| Parameter definitions | 48 |
| Manufacturers | 20 |
| Vehicle models | 39 |
| Source documents | 105 |
| Source observations | 347 |
| Normalized values | 458 |
| Parameter assessments | 145 |
| Load conditions | 34 |
| Fitments | 14 |
| Axles | 0 |
| Steering relations | 0 |
| Geometry assets | 0 |
| Conflict decisions | 0 |
| Conflicting normalized values | 2 |
| Evidence links | 462 |
| Persisted readiness results | 212 |

The final staging QA found zero `HOLD` identities, zero `FIXTURE-` identities,
zero direct `DERIVED`/`ESTIMATED` normalized values, and preserved the two
pre-existing conflicting values with zero decisions. Full final export proof
passed with 603 rows, 297,779 CSV bytes, and 109,464 readable XLSX bytes.
The final staging database was 1,138,688 bytes with SHA-256
`962C4DC082E41961AE24220498DCE9DE1314B6A17AAC0899B57DDAD3EA2B99B5`.

## Existing-data preservation

The clean accepted-34 baseline and final-39 staging databases were compared by
stable vehicle code. The semantic fingerprint is a SHA-256 of canonical JSON
including identity/temporal basis, source documents, observations, evidence
links, normalized values, assessments, load conditions, fitments, axles,
steering relations, geometry assets, conflict/decision rows, and readiness
status/blocker semantics. Generated UUIDs and generated timestamps were
excluded where appropriate; stable source/value/parameter semantics were
retained.

- **34/34 original semantic fingerprints unchanged.**
- Baseline original-34 fingerprint digest:
  `e826d27d4830cb945fed1ac69a4ef3846ddf00c10fa445970a242a8ef0f63712`.
- Final original-34 fingerprint digest:
  `e826d27d4830cb945fed1ac69a4ef3846ddf00c10fa445970a242a8ef0f63712`.
- Missing original stable codes: none.
- Unexpected final codes relative to the baseline: exactly the five intended
  tranche-2 additions.

## Mandatory semantic sentinels

All five sentinel suites returned **PASS**.

### DENZA D9 Performance AWD

- `EDITION_RELEASE`; exact Thailand `Performance AWD` identity.
- Length/width/height/wheelbase: `5250 / 1960 / 1920 / 3110 mm`.
- Reported width remains `OEM_UNSPECIFIED`; no body or mirrors-open width was
  inferred.
- OEM front/rear track remains `1675 / 1675 mm` with
  `track_definition=OEM_UNSPECIFIED`; no AVT track was created.
- Kerb mass/GVW: `2865 / 3439 kg`.
- Clearance remains `155 mm` on `OEM unladen` and `140 mm` on
  `OEM maximum loaded`, with OEM-minimum-unspecified clearance type.
- Turning remains `5.95 m`, `RADIUS`, with
  `turning_reference=OEM_UNSPECIFIED` and
  `turning_axle_scope=OEM_UNSPECIFIED`.
- Front/rear wheels remain `18-inch low-wind-resistance alloy`; tyres remain
  `235/60 R18`.

### Ferrari 296 GTB

- `EDITION_RELEASE`; Thailand Premiere April 2022.
- Ferrari global structural and fitment values remain
  `SAME_GEOMETRY_CONFIRMED`, not `EXACT_CONFIGURATION`.
- Length/width/height/wheelbase: `4565 / 1958 / 1187 / 2600 mm`.
- Reported width remains `OEM_UNSPECIFIED`; OEM track remains non-AVT at
  `1665 / 1632 mm`.
- Front/rear fitment remains `245/35 ZR20 / J9.0 x 20` and
  `305/35 ZR20 / J11.0 x 20`.
- Raw `Dry Weight = 1470 kg` remains observation-only. No
  `kerb_mass_kg=1470`, body width, mirrors-open width, clearance, or turning
  value exists.

### McLaren Artura Coupe

- `EDITION_RELEASE`; Thailand launch 19 December 2022.
- Thailand local dimensions remain authority grade **B**:
  `4539 / 1913 / 1193 / 2640 mm` for length/width/height/wheelbase.
- Reported width remains `OEM_UNSPECIFIED`; neither body nor mirrors-open width
  was created.
- OEM `DIN Kerb Weight = 1498 kg` remains `SAME_GEOMETRY_CONFIRMED`.
- Separate model-family `Vehicle Width = 2080 mm` remains raw ambiguity evidence
  only; it was not normalized as body or mirrors-open width.
- No turning, clearance, AVT track, or other unsupported geometry was created.

### Lamborghini Urus SE

- `EDITION_RELEASE`; Thailand launch May 2024.
- OEM structural geometry remains `SAME_GEOMETRY_CONFIRMED`.
- Body/mirrors-open widths remain `2022 / 2181 mm` with
  `BODY_EXCLUDING_MIRRORS` / `INCLUDING_MIRRORS_OPEN` semantics.
- Height/wheelbase/front-overhang/rear-overhang remain
  `1638 / 3003 / 1067 / 1053 mm`.
- OEM front/rear track remains `1695 / 1710 mm`, non-AVT.
- Front fitment remains `9.5J x 21 ET28 / 285/45 ZR21`; rear fitment remains
  `10.5J x 21 ET18 / 315/40 ZR21`.
- Air-suspension height adjustment and rear-wheel steering remain raw
  observations only. No clearance, lift clearance, turning value, steering
  relation, or ramp angle was created.

### Ferrari Purosangue

- `EDITION_RELEASE`; Thailand / Southeast Asia Premiere April 2023.
- Ferrari OEM structural geometry remains `SAME_GEOMETRY_CONFIRMED`.
- Length/width/height/wheelbase: `4973 / 2028 / 1589 / 3018 mm`.
- Reported width remains `OEM_UNSPECIFIED`; OEM track remains non-AVT at
  `1737 / 1720 mm`.
- Front/rear fitment remains `J9.0 x 22 / 255/35 R22` and
  `J11.0 x 23 / 315/30 R23`.
- Raw `Dry Weight = 2033 kg` remains observation-only. No
  `kerb_mass_kg=2033`, body/mirrors-open width, clearance, turning value, or
  steering relation was created.

## Application smoke with final 39-vehicle staging DB

The existing application was run with `DATABASE_URL` pointing only to the
disposable 39-vehicle staging database. No application source change was
needed for the five-record growth.

| Surface | Result |
|---|---|
| `/` | 307 redirect to `/vehicles` |
| `/vehicles` | 200 |
| `/api/vehicles` | 200; count **39**; all five new codes present |
| Five new detail pages and detail APIs | 200 for all 10 requests |
| `/issues` | 200 |
| `/api/issues` | 200; 118 issue rows; all five new codes represented |
| `/design-check` | 200; fail-closed results preserved |
| CSV export | 200; 82 rows / 40,660 bytes for the five new codes |
| XLSX export | 200; 82 readable rows / 19,261 bytes for the five new codes |

The following mixed comparisons all returned 200 and rendered every selected
stable code:

- DENZA D9 vs Lexus LM vs Kia Carnival vs Hyundai STARIA;
- Ferrari 296 GTB vs Porsche 911 GTS vs Lamborghini Revuelto;
- Lamborghini Urus SE vs Ferrari Purosangue;
- old + new mixed comparison: BYD ATTO 3, DENZA D9, Ferrari 296 GTB, and
  Lamborghini Urus SE.

Direct Design Check assertions also passed:

- D9, Ferrari 296 GTB, Artura, and Purosangue generic-width body checks were
  `INDETERMINATE`; Urus used its explicitly body-scoped width.
- Curb-to-curb turning checks for all five new configurations were
  `INDETERMINATE`; D9's OEM-unspecified reference was not treated as curb to
  curb, and missing supercar/Urus turning remained unknown.
- Missing clearance remained assessment-only/indeterminate for the supercar
  records.
- Urus rear-wheel-steering observation did not create a solved steering
  relation or turning geometry.
- Ferrari generic width and Artura `2080 mm` did not become body or
  mirrors-open width.

## Tests and CI

Focused suites covering curation/importer, release/current-pointer,
release-builder, Design Check, generic application, exports, and the launcher
passed:

```text
107 passed, 1 warning in 66.36s
```

The warning is the existing Starlette/httpx TestClient deprecation warning.

Full test suite:

```text
python -m pytest
190 passed, 1 warning in 112.66s
```

The post-push GitHub Actions CI result is recorded in the completion report;
at the time this artifact was written it was **PENDING**. The qualification
was not considered a release promotion.

## Repository and release boundaries

- `vehicle_engineering_curated.db` was not overwritten, promoted, or used as an
  import target. Its SHA-256 was
  `F01101A6CA8EB6F577E8B10FA22EB1A5F30705C45EA04988D01F685304BC7574` both
  before and after qualification, with 34 configurations.
- `data/curation/releases/current_release.json` was not changed. Its SHA-256
  was `DB69AFB470FCBFC87C32D090941E8F77B5AE0A4300393715392DE687DBFA0245`
  both before and after qualification.
- No 39-vehicle release definition was created.
- No builder, launcher, application, or test source was modified.
- No mechanical importer-neutral correction was necessary. All five manifests
  passed the accepted schema and importer unchanged.
- No merge or promotion was performed.

## Limitations

- These five records are qualified for controlled local create-only ingestion
  into disposable staging only; they are not members of an accepted 39-vehicle
  release.
- None of the five new configurations is AVT-ready or ramp-screening-ready.
  OEM track is not AVT outer-face track, body geometry is unavailable, turning
  references/values are unresolved where stated, and no approved ramp-angle
  derivation was introduced.
- Generic OEM width, dry/raw mass, air-suspension adjustment, rear steering,
  and model-family width evidence remain at their recorded semantic levels.
- The normal accepted database and stable current-release pointer remain at
  the accepted 34-configuration boundary.
