# Codex Prompt — Issue #7 Identity Time Basis v1

Repository:
https://github.com/bokoboss/thai-vehicle-engineering-db

Local working directory:
D:\R&D\thai-vehicle-engineering-db

Issue:
https://github.com/bokoboss/thai-vehicle-engineering-db/issues/7

Accepted contract merge:
`112dd67deab4c4832a4645d5127ebfe7165213ed`

## Model / effort / context

- Model: **GPT-5.6 Luna**
- Reasoning effort: **Max**
- Start a **new Codex chat**

## Mission

Implement only the bounded Identity Time Basis v1 schema/domain remediation defined in Issue #7.

Do not widen scope into pilot data ingestion, AVT/ramp changes, UI redesign, scraping, or other Phase 1 work.

## Preflight

Work in:

`D:\R&D\thai-vehicle-engineering-db`

Before changing anything:

1. `git status`
2. confirm current branch / HEAD / remotes
3. `git fetch origin`
4. confirm local `main` can be safely fast-forwarded to `origin/main`
5. confirm accepted identity contract PR #6 is present on `main`
6. if working tree is dirty or local history conflicts, stop and report before changing anything

Read:

- `PROJECT_PROFILE.md`
- `AGENTS.md`
- `docs/VEHICLE_DATA_STANDARD.md`
- `docs/LOGICAL_SCHEMA.md`
- `docs/SOURCE_CURATION_PROTOCOL.md`
- `docs/PILOT_AND_ACCEPTANCE.md`
- `docs/SCRUTINY_IDENTITY_TIME_BASIS_V1.md`
- Issue #7
- existing `0001_phase0_foundation`
- existing Phase 0 identity/readiness/export tests

## Branch

Create:

`codex/identity-time-basis-v1`

Do not modify or merge `main` directly.

## Required implementation

### Migration 0002

Create:

`0002_identity_time_basis`

after frozen:

`0001_phase0_foundation`

Do **not** rewrite 0001.

For `vehicle_configuration`:

- make `model_year_from` nullable
- keep `model_year_to` nullable
- add non-null `identity_time_basis`
- add nullable `identity_time_label_raw`

Controlled values:

- MODEL_YEAR
- OEM_REVISION_LABEL
- EDITION_RELEASE
- SALE_PERIOD
- MULTIPLE
- UNKNOWN

### Backfill

Existing rows with a model year must migrate to:

`identity_time_basis = MODEL_YEAR`

No existing model-year value may be lost or changed.

Never fabricate a model year.

### Downgrade

Downgrade must be explicit.

If non-MY rows exist and the old NOT NULL `model_year_from` contract cannot be restored safely, the downgrade must fail with a clear controlled message/precondition.

Do not invent placeholder years to make downgrade pass.

## Domain contract

Update:

- SQLAlchemy model
- Pydantic create/read schemas
- enums
- identity validation
- readiness
- search/detail/export surfaces where identity is emitted

### RESOLVED_EXACT validation

#### MODEL_YEAR
Requires:
- `model_year_from`

#### OEM_REVISION_LABEL
Requires:
- `identity_time_label_raw`

Do not parse the raw revision label into a model year unless a later explicit evidence rule authorizes it.

#### EDITION_RELEASE
Requires:
- `identity_time_label_raw`

Model year may remain null.

#### SALE_PERIOD
Requires at minimum:
- `sale_period_from`

Do not treat a retrieval date or generic “currently sold” state as a bounded sale period.

#### MULTIPLE
Requires a consistent supported combination of temporal evidence.

Do not accept an empty MULTIPLE state.

#### UNKNOWN
Must not be allowed for `RESOLVED_EXACT`.

It may remain valid for PARTIAL / UNRESOLVED identity states.

## Critical anti-inference rules

Do not infer:

- launch year -> model year
- brochure year -> model year
- retrieval year -> model year
- registration year -> model year
- Thai Buddhist calendar revision year -> model year

unless source semantics explicitly establish model year.

Examples:

- `MY24` may support MODEL_YEAR
- `รุ่นปรับปรุงปี 2568` is not silently MY2025
- `35th Anniversary Edition` may support EDITION_RELEASE if exact applicability evidence is present

## Required tests

At minimum:

1. existing exact MODEL_YEAR fixture remains valid
2. RESOLVED_EXACT + MODEL_YEAR + null model_year_from -> reject
3. RESOLVED_EXACT + EDITION_RELEASE + null model year + raw label -> accept
4. RESOLVED_EXACT + OEM_REVISION_LABEL + null model year + raw label -> accept
5. RESOLVED_EXACT + UNKNOWN -> reject
6. PARTIAL + UNKNOWN -> accept
7. SALE_PERIOD without usable start/applicability -> reject exact
8. MULTIPLE with no actual supported basis -> reject
9. current Phase 0 DB upgrade -> data preserved
10. existing model-year rows -> MODEL_YEAR backfill
11. new non-MY exact record -> database roundtrip
12. new non-MY exact record -> search/detail output
13. new non-MY exact record -> CSV/XLSX export
14. downgrade never fabricates year
15. all existing Phase 0 tests remain passing

## Qualification

Run at minimum:

```text
python -m pytest
python -m alembic upgrade head
python -m alembic downgrade 0001_phase0_foundation
python -m alembic upgrade head
python -m alembic current
```

Also validate:

- upgrade from an existing seeded 0001 database
- fresh database upgrade 0001 -> 0002
- SQLite migration behavior
- PostgreSQL offline DDL
- existing 21-table foundation remains intact
- search/detail/export regression
- CI

## Stop conditions

Stop and report rather than broadening scope if:

- accepted PR #6 contract is not on main
- implementation needs a broader identity-table redesign
- migration would require a fabricated year
- evidence provenance semantics need to change
- the work starts touching AVT/ramp/source-crawling or production vehicle curation

## PR

Push branch and open one PR against `main`.

Do not merge.

## Final report

Return:

1. branch
2. previous main HEAD
3. final branch HEAD
4. PR number/link
5. migration summary
6. domain/API/readiness/export changes
7. required regression matrix PASS/FAIL
8. total test count/result
9. upgrade/downgrade qualification
10. PostgreSQL offline DDL result
11. CI run/link/status
12. protected-contract deviations — expected none
13. residual limitations
14. explicit confirmation PR remains open and unmerged
