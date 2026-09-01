# Wave 2B tranche 1 import qualification

Status: **PASS — Issue #40 qualification completed**

Date: 2026-09-01

PR: #39 — Wave 2B tranche 1: add mainstream and supercar engineering manifests

Branch: `chatgpt/wave2b-data-expansion`

## Revision qualified

- Accepted `main` base SHA: `7a0b527a858e63c9e8baa082f984a82986009079`.
- Starting PR HEAD: `861d943fec61b138c7a9f069329f1295079aea21` (`docs: define Wave 2B tranche 1 with two supercars`).
- The remote branch was fetched before qualification and the starting tip was confirmed from `origin/chatgpt/wave2b-data-expansion`.
- Final PR HEAD is the branch tip containing this qualification record; its exact SHA is returned with the completion result. The SHA cannot be embedded in its own commit without changing that commit.
- No merge was performed.

The qualification treated Issue #40 as the authoritative contract. This was a data qualification run against the existing create-only importer, not new automotive research.

## Mechanical importer-neutral correction

The first validation pass found one schema-only issue in the Lamborghini manifest: its two OEM source records used the non-canonical authority label `OEM_GLOBAL`. Both were changed to the existing canonical enum `OEM_REGIONAL_GLOBAL` in:

`data/curation/manifests/wave2b/lamborghini_revuelto_th_launch_20230725_v1.json`

No source URL, publisher, raw subtype, source wording, applicability note, value, unit, evidence link, identity basis, or engineering interpretation changed. The correction only made the already-intended global OEM authority class consumable by the accepted schema. The subsequent validation and import passed.

## Staging procedure

The accepted `release_2026_09_a` definition was rebuilt into the disposable database `vehicle_engineering_wave2b_t1_baseline.staging.db` with the generic Data Release Pipeline v1 builder and `--no-promote`. The build performed Alembic upgrade, registry-only `app.curate init`, validation/import of all 27 accepted manifests, database QA, and CSV/XLSX export proof.

The baseline database was copied to `vehicle_engineering_wave2b_t1.staging.db`. The seven Wave 2B manifests were then each validated and imported with:

```powershell
$env:DATABASE_URL = "sqlite:///D:/R&D/thai-vehicle-engineering-db/vehicle_engineering_wave2b_t1.staging.db"
python -m app.curate validate <manifest.json>
python -m app.curate import <manifest.json>
```

Every manifest import committed atomically. The normal `vehicle_engineering_curated.db` was never an import target, was not overwritten, and was not promoted.

## Baseline and final inventory

Registry-only initialization was **PASS**: 48 parameter definitions and 0 vehicle rows before the accepted release build.

| Record | Accepted 27 baseline | Final 34 staging | Delta |
|---|---:|---:|---:|
| Vehicle configurations | 27 | 34 | +7 |
| Parameter definitions | 48 | 48 | 0 |
| Manufacturers | 15 | 17 | +2 |
| Vehicle models | 27 | 34 | +7 |
| Source documents | 74 | 91 | +17 |
| Source observations | 268 | 317 | +49 |
| Normalized values | 319 | 405 | +86 |
| Parameter assessments | 80 | 116 | +36 |
| Load conditions | 26 | 32 | +6 |
| Fitments | 14 | 14 | 0 |
| Axles | 0 | 0 | 0 |
| Steering relations | 0 | 0 | 0 |
| Geometry assets | 0 | 0 | 0 |
| Conflict decisions | 0 | 0 | 0 |
| Persisted readiness results | 164 | 192 | +28 |

Baseline release proofs:

- Exactly 27 configurations were present.
- Stable-code inventory matched the accepted release; stable-code digest: `0b644d3f10fd7f70a631612c87ecfc03e94a4ab59a37d5fd51278b1f6e560446`.
- No `HOLD` identity, no `FIXTURE-` configuration, and no direct `DERIVED` / `ESTIMATED` value were present.
- Two conflicting normalized values and zero conflict decisions were retained.
- The baseline staging database SHA-256 was `188C8587A84D77B0D7D97C4ED9B3DDDD0FF66CBDE013063C95AB561AF10564AD` (876,544 bytes).

Final staging proofs:

- Exactly 34 configurations were present.
- All original 27 stable codes remained, and all seven new stable codes existed exactly once:
  - `th-byd-m6-extended-7seat-release-2024-11-28`
  - `th-hyundai-staria-premium-my2025`
  - `th-toyota-yaris-cross-hev-premium-luxury-catalog-2026`
  - `th-honda-hrv-ehev-rs-new-release-2024-11-28`
  - `th-toyota-camry-hev-premium-luxury-new-release-2567`
  - `th-porsche-911-carrera-gts-992ii-delivered-2025`
  - `th-lamborghini-revuelto-launch-2023-07-25`
- No `HOLD` identity, `FIXTURE-` configuration, direct `DERIVED` / `ESTIMATED` value, or duplicate stable code was present.
- Conflict semantics remained two conflicting normalized values and zero conflict decisions.
- Final staging database SHA-256 was `2AAE860ED8BA0762A4217C13944EF241564EC5FACE951B16BBF3E3B6B3A007F3` (1,019,904 bytes).

## Manifest validation and import

All seven final manifests returned **PASS** from `python -m app.curate validate`. All seven create-only imports returned **PASS** with zero source reuse and zero conflicts.

| Manifest | Stable vehicle code | Validate | Import | Sources created | Observations | Values | Assessments | Loads | Fitments | Conflicts |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `byd_m6_extended_7seat_release_20241128_v1.json` | `th-byd-m6-extended-7seat-release-2024-11-28` | PASS | PASS | 2 | 10 | 15 | 4 | 2 | 0 | 0 |
| `hyundai_staria_premium_my2025_v1.json` | `th-hyundai-staria-premium-my2025` | PASS | PASS | 2 | 7 | 14 | 5 | 1 | 0 | 0 |
| `toyota_yaris_cross_hev_premium_luxury_catalog_2026_v1.json` | `th-toyota-yaris-cross-hev-premium-luxury-catalog-2026` | PASS | PASS | 2 | 7 | 12 | 5 | 1 | 0 | 0 |
| `honda_hrv_ehev_rs_new_release_20241128_v1.json` | `th-honda-hrv-ehev-rs-new-release-2024-11-28` | PASS | PASS | 3 | 6 | 13 | 5 | 1 | 0 | 0 |
| `toyota_camry_hev_premium_luxury_new_release_2567_v1.json` | `th-toyota-camry-hev-premium-luxury-new-release-2567` | PASS | PASS | 3 | 6 | 12 | 5 | 1 | 0 | 0 |
| `porsche_911_carrera_gts_992ii_delivered_2025_v1.json` | `th-porsche-911-carrera-gts-992ii-delivered-2025` | PASS | PASS | 2 | 7 | 9 | 6 | 0 | 0 | 0 |
| `lamborghini_revuelto_th_launch_20230725_v1.json` | `th-lamborghini-revuelto-launch-2023-07-25` | PASS | PASS | 3 | 6 | 11 | 6 | 0 | 0 | 0 |
| **Total** | **7 configurations** | **7/7 PASS** | **7/7 PASS** | **17** | **49** | **86** | **36** | **6** | **0** | **0** |

## Mandatory semantic assertions

### BYD M6 Extended 7 Seats

- Minimum turning radius remains exactly `8.5 m`, published as `RADIUS`, with `turning_reference=OEM_UNSPECIFIED` and `turning_axle_scope=OEM_UNSPECIFIED`; it was not halved or corrected.
- Clearances remain separate: `170 mm` on `OEM unladen` and `140 mm` on `OEM maximum loaded`.
- Reported width remains `OEM_UNSPECIFIED`.
- OEM front/rear track remains non-AVT (`track_definition=OEM_UNSPECIFIED`); no AVT outer-face track exists.

### Hyundai STARIA Premium MY25

- Identity remains `MODEL_YEAR` with MY25 evidence from the official Hyundai Thailand brochure.
- Reported width remains `OEM_UNSPECIFIED`.
- The 18-inch tread values `1721 / 1732 mm` remain `SAME_GEOMETRY_CONFIRMED`, with OEM-unspecified tread definition.
- Clearance `186 mm` retains the OEM-unspecified load/reference condition.
- Turning `5.97 m` retains OEM-unspecified reference and axle scope.

### Toyota Yaris Cross HEV Premium Luxury

- The `2026` catalogue label remains `EDITION_RELEASE`; `model_year_from` and `model_year_to` remain null.
- Reported width remains `OEM_UNSPECIFIED`.
- OEM tread `1525 / 1520 mm` remains non-AVT.
- Clearance `210 mm` retains unspecified load/reference; turning `5.2 m` remains OEM-unspecified.

### Honda HR-V e:HEV RS

- Identity remains non-MY `EDITION_RELEASE`.
- Raw `Weight / น้ำหนักรถ = 1404 kg` remains a source observation only; no `kerb_mass_kg=1404` exists.
- OEM tread `1542 / 1543 mm` remains non-AVT.
- Turning `5.5 m` remains OEM-unspecified; steering-wheel lock-to-lock remains published as `2.44 turns`.

### Toyota Camry HEV Premium Luxury

- October `2567` remains `EDITION_RELEASE`, not `MODEL_YEAR`.
- Reported width `1840 mm` remains OEM-unspecified.
- OEM tread `1580 / 1590 mm` remains non-AVT.
- Clearance `135 mm` and turning `5.7 m` retain unspecified load/reference and turning semantics.

### Porsche 911 Carrera GTS 992 II — Thailand-delivered 2025

- Bounded Thailand-delivered 2025 identity remains `EDITION_RELEASE`.
- Body width `1852 mm` and mirrors-open width `2033 mm` remain distinct semantic parameters.
- `10.9 m turning circle diameter` remains `oem_turning_value_text`; no normalized `5.45 m` radius was created.
- Curb weight `1604 kg` and GVW `2045 kg` remain explicitly sourced.
- Front-lift `+40 mm` remains raw observation evidence only; no ground clearance or ramp angle was inferred.
- Rear-axle steering presence does not create unsupported axle/steering angle or relation data; no axle or steering relation was imported.

### Lamborghini Revuelto — Thailand launch 2023

- Thailand launch identity remains `EDITION_RELEASE`.
- Global OEM structural geometry remains `SAME_GEOMETRY_CONFIRMED`, not `EXACT_CONFIGURATION`.
- Body width is `2033 mm`; mirrors-open width is `2266 mm`.
- Dry weight `1772 kg` remains raw evidence only; no `kerb_mass_kg=1772` exists.
- Standard staggered fitment remains front/rear `20 / 21 inch`; OEM tread remains non-AVT.
- Turning and ground clearance remain unavailable; the clearance assessment is `NOT_FOUND_AFTER_SEARCH`.

## Existing-data preservation

The untouched 27-vehicle baseline and final 34-vehicle staging database were compared by stable vehicle code using semantic fingerprints. Generated UUIDs and generated timestamps were excluded where appropriate; identity, source-document metadata, observations, normalized values, assessments, load conditions, fitments, axle/steering/geometry records, conflict decisions, evidence links, and readiness status/blocker semantics were included.

- 27 of 27 original vehicle semantic fingerprints matched.
- Baseline semantic fingerprint digest: `f543eaea0efcb0c64e1f3f13207c8beec54be622b7f283725d54a9e510d72ab8`.
- Final semantic fingerprint digest for the same original 27: `f543eaea0efcb0c64e1f3f13207c8beec54be622b7f283725d54a9e510d72ab8`.
- Existing source documents, observations, normalized values, assessments, load conditions, fitments, conflict states/decisions, and readiness semantics matched.
- The normal accepted `vehicle_engineering_curated.db` remained 27 vehicles and retained SHA-256 `CFD5F71B5790CCEE6AB76B530C1E2CD09A2721A27001E0E895C20A4B52FA28B0` (880,640 bytes) before and after qualification.
- `data/curation/releases/current_release.json` was not changed. No 34-vehicle accepted release was created or published.

## Application smoke with the 34-vehicle staging database

HTTP/TestClient smoke used only `vehicle_engineering_wave2b_t1.staging.db`.

| Surface | Result |
|---|---|
| `/` | 307 redirect to `/vehicles` |
| `/vehicles` | 200 |
| `/api/vehicles` | 200; count `34`; all seven new codes present |
| Seven new detail APIs and pages | 200 for all 14 requests |
| `/compare` | 200; old BYD ATTO 3, new BYD M6, Porsche, and Lamborghini rendered together |
| `/design-check` | 200; M6 width and turning checks rendered `INDETERMINATE` |
| `/issues` | 200; new unknown/readiness issues visible |
| `/api/issues` | 200; count `107`; all seven new codes represented |
| CSV export | 200; 521 rows, 257,717 bytes; evidence/state headers present |
| XLSX export | 200; 521 rows, 96,381 bytes; readable `Engineering Data` sheet |

Direct application-domain assertions also passed:

- OEM-unspecified reported width was not substituted for body width; the BYD M6 body-width check was `INDETERMINATE`.
- Turning-envelope screening was `INDETERMINATE` for all seven new configurations because references/shape/value semantics were unresolved as required.
- Porsche raw turning diameter was not parsed or halved by Design Check v1.
- Lamborghini ground clearance remained unavailable/indeterminate and visible through its assessment/readiness issues.

No application source change was needed for the 27-to-34 catalogue growth.

## Tests and CI

- Accepted 27-manifest Data Release Pipeline v1 baseline build, QA, and export proof: **PASS**.
- Wave 2B CLI validation: **7/7 PASS**.
- Wave 2B create-only imports: **7/7 PASS**.
- Focused curation/import, release-builder, Design Check, release-contract, and current-pointer tests: **85 passed**, one existing Starlette/httpx deprecation warning.
- Full `python -m pytest`: **190 passed**, one existing Starlette/httpx deprecation warning.
- GitHub Actions CI: **pending for the final pushed qualification commit**; no CI failure was observed locally.

## Limitations and release boundary

- The seven records are qualified for controlled local create-only ingestion into the disposable 27-vehicle staging database. They are not yet members of an accepted 34-vehicle release.
- None of the seven records is AVT-ready or ramp-screening-ready. Missing AVT outer-face tracks, unresolved turning-envelope semantics, missing explicit AVT steering inputs, and absent approved ramp-screening angles remain intentional blockers.
- Generic OEM width and tread/track values were not promoted to body/mirror width or AVT outer-face track.
- Unknown load, ground-clearance, mass, turning, and folded-mirror values remain assessments or raw observations as specified.
- This qualification does not add missing supercar geometry, infer ramp angles, convert dry/raw mass, reinterpret turning data, or change identity-time meaning.
- The normal accepted database was not overwritten, the current release pointer was not updated, and PR #39 was not merged.
