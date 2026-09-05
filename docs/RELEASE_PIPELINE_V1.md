# Curated release pipeline v1 (historical contract)

Status: **historical example accepted with `release_2026_09_a`**
Date: 2026-09-01

The v1 contract remains the historical release-membership and fail-closed QA
foundation. The current accepted pointer is now `release_2026_09_d` with 41
configurations; the v2 behavior below adds publication qualification and local
refresh without changing that release's membership or engineering semantics.

## Release membership

In the v1 example, `data/curation/releases/current_release.json` was the stable selector for normal updates and pointed to the immutable versioned definition `release_2026_09_a.json`, which explicitly listed the 27 accepted manifest paths: 3 sentinel manifests, 18 Wave 1 manifests, and 6 Wave 2A manifests. The current selector and Release D behavior are documented in the v2 section below.

Versioned release definitions such as `release_2026_08_wave1.json` and `release_2026_09_a.json` remain immutable/reproducible. The pointer accepts only a schema-1 direct `release_*.json` target in this directory and revalidates that target with the normal release contract. Publishing a later accepted release requires adding that definition and updating only `current_release.json`; the builder and Windows updater do not change because the catalog grew.

The builder does not scan manifest directories. A manifest that is present in the repository but absent from the release definition is not production input.

The release file carries its schema version, release identity/date/status, applicable standard/methodology versions, and inspectable manifest membership. Vehicle counts, stable-code inventory, source reuse, and database counts are derived from the listed manifests and validated during the build.

## Build and promotion

Run the Windows update launcher:

```text
Update Vehicle Database.cmd
```

Or run the generic builder directly:

```powershell
.venv\Scripts\python.exe scripts/build_curated_db.py `
  --replace-final
```

For historical/reproducible builds, pass a versioned definition explicitly:

```powershell
python scripts/build_curated_db.py --release data/curation/releases/release_2026_08_wave1.json
```

The builder creates a new disposable SQLite database, upgrades it with Alembic, initializes only the accepted parameter registry, validates every listed manifest, imports through `app.curate`, evaluates readiness, runs provenance/data-integrity and semantic regression QA, proves CSV/XLSX exports, and only then atomically replaces `vehicle_engineering_curated.db`. When a previous accepted database exists, a single `.previous` copy is retained after successful replacement.

The accepted database is never used as an incremental import target. A missing listed manifest, duplicate record/stable code, incompatible source-code reuse, importer failure, readiness/QA failure, export failure, or replacement failure returns non-zero while leaving the accepted database at its prior path unchanged. Failed staging files remain disposable and are named in the error for safe inspection/removal.

`python -m app.seed` is not part of this workflow. It remains only for the historical Phase 0 fixture workflow.

## Compatibility

`scripts/build_wave1_curated_db.py` is a thin wrapper over the same generic implementation and points to the explicit historical `release_2026_08_wave1` membership. It remains for historical tests and reproducibility; it is not an independent build/QA implementation.

## Qualification metadata

Each successful build writes a release qualification JSON record, including the release ID, release definition, repository SHA, manifest/stable-code inventory, deterministic stable-code digest, derived counts, readiness summary, semantic proofs, export proof, build timestamp, and promotion result. The accepted first-release record is:

`data/curation/releases/release_2026_09_a.qualification.json`

## Data-only versus software changes

For an additional research-clean vehicle using existing registered parameters:

1. research and review its manifest;
2. add its exact path to a new immutable accepted release definition;
3. update `data/curation/releases/current_release.json` to select that definition;
4. run `Update Vehicle Database.cmd`;
5. open the existing application.

This does not require vehicle-count constants, FastAPI route changes, template changes, Compare changes, or Design Check changes. Software/methodology work remains appropriate for new parameter families, constraints, AVT methods, ramp solvers, or geometry models.

## Release pipeline v2 — CI qualification and safe local refresh

Issue #63 extends the v1 contract without changing accepted Release D
membership, vehicle engineering values, Design Check semantics, or AVT/ramp
methodology.

The publication flow is:

```text
research/manifest + explicit immutable release PR
  -> path-scoped data-release CI qualification
  -> review/merge
  -> local checkout contains the accepted release
  -> Start launcher refreshes only when the content fingerprint changes
```

`build_input_digest_sha256` is a canonical SHA-256 over the selected versioned
release definition, the exact repository-relative paths and JSON content of
all manifests listed by that definition, the accepted parameter registry, and
an explicit schema/build compatibility payload. It is independent of absolute
paths, path separators, timestamps, generated IDs, and the current working
directory. `stable_vehicle_digest_sha256` remains a membership sentinel; it is
not a freshness proof by itself.

After a successful local promotion, the builder writes the ignored sidecar
`vehicle_engineering_curated.db.meta.json`. It records the metadata schema,
release identity/path, both digests, vehicle count, the promoted database
SHA-256, and UTC build/promotion timestamps. The accepted database and marker
are replaced through the same rollback-safe promotion operation. A retained
`vehicle_engineering_curated.db.previous` is accompanied by
`vehicle_engineering_curated.db.previous.meta.json` when its marker matches.
Failed staging, QA, metadata, or promotion work leaves the prior accepted DB
and marker unchanged.

On normal launch, the runner first resolves the explicit current release and
checks the accepted DB, marker, fingerprint, stable-code set, count, and file
hash. A matching pair starts immediately without invoking the builder. A
missing or stale pair invokes one generic controlled staging/QA/promotion
build. Browser startup is delayed until that decision completes. If refresh
fails, a readable accepted-path DB is opened as the **previous accepted local
database** with a prominent mismatch warning; if no usable DB exists, launch
fails with instructions. `--no-auto-refresh` disables all builder invocation
for troubleshooting or reproducibility. The runner never pulls, fetches,
resets, stashes, or checks out Git state.

Refresh and promotion of the shared accepted database are serialized by an
adjacent OS-released advisory lock. After acquiring the lock, each launcher
recomputes the current release and database match, so a waiting launcher skips
the builder when another launcher has already completed the refresh.

`Update Vehicle Database.cmd` remains the explicit manual update path and
writes qualification/export proofs under ignored `artifacts/local/`. Direct
builder invocation can still pass an explicit `--qualification` path when a
reviewed qualification artifact is required. Historical tracked qualification
JSON files are not rewritten by normal local update or launch.

The path-scoped `.github/workflows/data-release.yml` checks pull requests to
`main` when release/build inputs change. It checks out the exact PR head,
resolves the branch's current-release pointer, runs the generic builder with
`--no-promote` into runner-temporary paths, validates the staging DB and
metadata fingerprint, emits a compact job summary, and uploads qualification
evidence. It does not scan manifest directories or promote into the checkout.
