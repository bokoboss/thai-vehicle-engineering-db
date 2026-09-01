# Curated release pipeline v1

Status: **accepted with `release_2026_09_a`**  
Date: 2026-09-01

## Release membership

`data/curation/releases/current_release.json` is the stable selector for normal updates. It currently points to the immutable versioned definition `release_2026_09_a.json`, which explicitly lists the 27 accepted manifest paths: 3 sentinel manifests, 18 Wave 1 manifests, and 6 Wave 2A manifests.

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
