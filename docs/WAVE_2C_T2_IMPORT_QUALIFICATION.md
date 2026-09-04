# Wave 2C tranche 2 importer qualification

Status: **BLOCKED — Issue #58 importer qualification gate**

Date: 2026-09-04

Issue: [#58](https://github.com/bokoboss/thai-vehicle-engineering-db/issues/58)

PR: [#57](https://github.com/bokoboss/thai-vehicle-engineering-db/pull/57)

Branch: `chatgpt/wave2c-tranche2-data-expansion`

## Qualification scope

Issue #58 is the authoritative execution contract. The requested scope was a
create-only qualification of exactly three existing Wave 2C manifests against
the accepted `release_2026_09_d` 41-configuration baseline, using a disposable
44-configuration staging database. Defender 130 was explicitly excluded.

No new automotive research was performed. No research manifest was modified,
no importer or application semantics were changed, no accepted release or
database was promoted or overwritten, and PR #57 was not merged.

The qualification stopped at the mandatory validation gate when the third
manifest exposed an existing-manufacturer display-metadata conflict. The
failure is recorded here rather than repaired by changing data identity,
mutating accepted metadata, or weakening the importer contract.

## Revision and preflight gate

- Accepted `main` SHA: `357474a7193f0a6d9b50aa7148c6dd5012548a28`.
- Pre-sync PR #57 HEAD: `aa0a36c284cbf8427071bec1a4b615e84930317f`.
- Merge base before synchronization:
  `6776f703e9b181cfda4745503b0d236f642a1929`.
- The branch was rebased cleanly onto the exact accepted `main` SHA.
- Post-sync starting HEAD: `5631ec08ff2319362f7f41fc47c03cd773608e7d`.
- The worktree was clean before qualification.
- The branch was force-updated with `--force-with-lease` from the recorded
  pre-sync PR HEAD. No merge was performed.
- `data/curation/releases/current_release.json` was unchanged. Its SHA-256
  remained `9d0c9904b4a6a868be8ab61c023ff24cc45cb12750402260728bb1108cdb1cc7`
  and it continues to point to `release_2026_09_d.json`.

The three in-scope manifests were byte-for-byte unchanged by synchronization:

| Manifest | SHA-256 before sync | SHA-256 after sync |
|---|---|---|
| `toyota_alphard_hev_premium_luxury_sale_snapshot_20260903_v1.json` | `99bcbfc00eb144209c2c6cbd4cb2d24d5e1431a1606920bb3b93a52e1ff10576` | same |
| `porsche_taycan_turbo_gt_my2027_v1.json` | `9e9edd98c6ec1c30e458edfc2a2f384b1c641c9e6a7ea1b2365def910384ad56` | same |
| `mercedes_maybach_s580e_premium_sale_snapshot_20260903_v1.json` | `00393b19d3a2974162a0c3790913862d06736112364cf6c5e94ad85377ccf23b` | same |

## Staging procedure

The accepted Release D definition was built into a disposable baseline staging
database with the existing builder and `--no-promote`:

```text
.venv\\Scripts\\python.exe scripts/build_curated_db.py --release data\\curation\\releases\\release_2026_09_d.json --staging <qualification-temp>\\release_d_41.staging.db --final <qualification-temp>\\unused_final.db --csv <qualification-temp>\\release_d_41.csv --xlsx <qualification-temp>\\release_d_41.xlsx --qualification <qualification-temp>\\release_d_41.qualification.json --no-promote
```

The baseline build returned **PASS**. Its staging database was
`C:\\Users\\kittipat_t\\AppData\\Local\\Temp\\tve-db-wave2c-t2-4094ffc8c31b44adbea7b5c81d84ce4d\\release_d_41.staging.db`.
The requested three manifests were then passed to the existing no-write
validation command with `DATABASE_URL` pointed only at that disposable
staging database.

The static candidate manifest totals were:

| Manifest | Stable vehicle code | Sources / entries | Observations | Values | Assessments | Loads |
|---|---|---:|---:|---:|---:|---:|
| `toyota_alphard_hev_premium_luxury_sale_snapshot_20260903_v1.json` | `th-toyota-alphard-hev-premium-luxury-sale-snapshot-2026-09-03` | 2 | 6 | 12 | 7 | 1 |
| `porsche_taycan_turbo_gt_my2027_v1.json` | `th-porsche-taycan-turbo-gt-my2027` | 4 | 7 | 17 | 5 | 3 |
| `mercedes_maybach_s580e_premium_sale_snapshot_20260903_v1.json` | `th-mercedes-maybach-s580e-premium-sale-snapshot-2026-09-03` | 3 | 4 | 4 | 7 | 0 |
| **Total** | **3 configurations** | **9** | **17** | **33** | **19** | **4** |

The nine candidate source codes were unique. These are candidate manifest
counts only; none were persisted because the gate stopped before import.

## Baseline database contract and actual deltas

The clean staging baseline matched the accepted 41-configuration contract and
the required stable-code digest:

`923c5607f4789a44368172cfe88c9fe1c6190ab2e895e61476430c1546258306`

| Record | Release D baseline | Staging after stopped gate | Actual delta |
|---|---:|---:|---:|
| Vehicle configurations | 41 | 41 | 0 |
| Parameter definitions | 48 | 48 | 0 |
| Manufacturers | 21 | 21 | 0 |
| Vehicle models | 41 | 41 | 0 |
| Source documents | 107 | 107 | 0 |
| Source entries in manifests | 108 | 108 | 0 |
| Source observations | 354 | 354 | 0 |
| Normalized values | 466 | 466 | 0 |
| Parameter assessments | 158 | 158 | 0 |
| Load conditions | 34 | 34 | 0 |
| Fitments | 14 | 14 | 0 |
| Axles | 0 | 0 | 0 |
| Steering relations | 0 | 0 | 0 |
| Geometry assets | 0 | 0 | 0 |
| Conflict decisions | 0 | 0 | 0 |
| Conflicting normalized values | 2 | 2 | 0 |
| Readiness results | 220 | 220 | 0 |
| Evidence links | 470 | 470 | 0 |

Actual unique source-document delta: **0**. Actual source-entry delta:
**0**. The expected successful-import deltas were +9 source entries, +17
observations, +33 values, +19 assessments and +4 loads, but none were applied.

## Importer gate result

| Manifest | Validate | Import | Result |
|---|---|---|---|
| Toyota Alphard HEV Premium Luxury sale snapshot | PASS | not attempted | gate stopped later |
| Porsche Taycan Turbo GT MY2027 | PASS | not attempted | gate stopped later |
| Mercedes-Maybach S 580e Premium sale snapshot | **FAIL** | not attempted | blocking error |
| **Total** | **2/3 PASS** | **0/3 attempted** | **BLOCKED** |

Exact failure:

```text
manufacturer Mercedes-Benz has incompatible display metadata; refusing to mutate it
```

The Maybach manifest declares `manufacturer_name` `Mercedes-Benz` with
`manufacturer_display_name` `Mercedes-Maybach`. The clean accepted baseline
already contains canonical manufacturer `Mercedes-Benz` with display name
`Mercedes-Benz`. The existing importer correctly refuses to mutate the
existing manufacturer display metadata.

This is a substantive identity-metadata issue. Changing the manifest display
name, adding a second manufacturer, changing accepted manufacturer metadata,
or relaxing the importer would each change data or importer semantics. None was
done. Validation is no-write, and because validation was stopped before the
import loop, the disposable staging database remained at 41 configurations.

## Existing-data preservation

No import transaction was started, so no final 44-configuration database exists
for the requested 41/41 post-import fingerprint comparison. The baseline
staging database remained the exact clean Release D build, and no original
record was written by the failed validation path.

Accordingly:

- Original-41 semantic fingerprint comparison: **not run; no mutation path was
  reached**.
- Final original-41 fingerprint digest: **not applicable; no final 44-record
  database was produced**.
- Stable-code baseline digest remains
  `923c5607f4789a44368172cfe88c9fe1c6190ab2e895e61476430c1546258306`.

The intended fingerprint scope remains identity and temporal basis,
manufacturer/model, sources and raw observations, normalized values, evidence
links, assessments/readiness, loads/fitments, axles/steering/geometry,
conflicts/decisions, derivation, QA and AVT records. No comparison result is
claimed for a nonexistent final staging database.

## Semantic sentinel status

The requested Alphard, Taycan and Maybach sentinel assertions were not
reported as final-database PASS results because the importer gate stopped
before any candidate was persisted. The manifest validation results above are
the only candidate-level importer results claimed here.

The three requested manifests were the only candidates considered. Defender
130 was not validated or imported, and no fourth vehicle was introduced. The
research applicability registry was not changed and remains
`RESEARCH_ACTIVE_MY27_GEOMETRY_APPLICABILITY_HOLD` for the excluded Defender
work.

## Application, API and export smoke

The required 44-configuration application/API/export smoke was **not run**:
there was no qualified 44-record staging database to exercise. The baseline
builder's Release D database-QA and CSV/XLSX export proof passed before the
candidate validation gate; those baseline results do not substitute for the
requested 44-record application smoke.

## Tests and CI

The focused local importer, release, builder, Design Check, application,
API/export and launcher suites and the full `python -m pytest` suite were not
run after the blocker. Running them cannot qualify the missing import and
would not resolve the identity-metadata conflict.

The exact-head GitHub Actions check for post-sync HEAD
`5631ec08ff2319362f7f41fc47c03cd773608e7d` completed with **success**:
[run 33832218942](https://github.com/bokoboss/thai-vehicle-engineering-db/actions/runs/33832218942).
This CI result covers the rebased pre-document branch head; the docs-only
qualification record commit has its own check reported with the completion
result.

## Release and repository boundaries

- `data/curation/releases/current_release.json` was not changed.
- The accepted database was not used as an import target, overwritten or
  promoted. The builder's `--final` path was a separate nonexistent disposable
  path.
- No source, manifest, importer, builder, application, launcher or test source
  was modified to force a 41-to-44 result.
- No Defender manifest, fourth vehicle, Release E, release promotion or merge
  was performed.
- This qualification document is the only requested artifact added after the
  gate stopped.

## Unresolved questions and next required action

- Resolve whether this manifest should use the existing canonical manufacturer
  display metadata or whether the product schema intentionally requires a
  distinct Mercedes-Maybach manufacturer identity. That is a data-contract
  decision, not an importer workaround.
- Until that decision is made and reviewed, the Maybach manifest remains
  unqualified and the 44-configuration catalog cannot be accepted.
- The Maybach mirror-open conflict (1921 mm exact configuration versus 2109 mm
  same-geometry-confirmed), its unresolved body width, and its unresolved
  wheelbase/turning/clearance/mass remain untouched. No conflict decision was
  created.
- The Alphard and Taycan manifests have passed no-write validation, but their
  requested semantic sentinels and final database effects remain unqualified
  because the all-three gate is atomic for this task.

Qualification result: **BLOCKED at the existing-manufacturer display-metadata
gate; stop condition satisfied; no candidate data imported.**
