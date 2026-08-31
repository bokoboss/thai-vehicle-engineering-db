# Curation Ingestion Contract v1

Status: control-plane candidate  
Date: 2026-08-31  
Purpose: safely convert accepted Phase 1 research evidence into production-like curated database records without bypassing the existing evidence-first service boundary.

## 1. Core decision

Use a **small create-only CLI importer** driven by explicit curation manifests.

The importer must call existing domain/service functions. It must not insert raw SQL rows or bypass validation.

Research packets are **not** ingestion manifests.

## 2. Why research packets cannot be imported directly

The Batch A–E research JSON intentionally summarizes evidence for review. It does not always contain enough one-to-one ingestion linkage.

Examples:

- one research record may cite several sources without assigning every raw observation to one exact `source_code`;
- normalization candidates often do not name the exact raw observation that supports them;
- source entries use research-friendly subtypes such as `OEM_BROCHURE_PDF_SCREENSHOT_VERIFIED` rather than a canonical persistence type;
- some grouped observations are intentionally unresolved;
- some candidate fields are HOLD/REVIEW_REQUIRED rather than approved normalized values.

Therefore direct ingestion from Batch JSON would risk fabricating provenance.

## 3. CLI shape

Target interface:

```text
python -m app.curate validate <manifest.json>
python -m app.curate import <manifest.json>
```

Optional:

```text
python -m app.curate import <manifest.json> --dry-run
```

The importer is a maintainer tool, not an end-user feature.

## 4. Database isolation

Production-like curated data should not be mixed with deterministic Phase 0 fixtures by default.

Recommended local workflow:

```powershell
$env:DATABASE_URL="sqlite:///./vehicle_engineering_curated.db"
python -m alembic upgrade head
python -m app.curate init
python -m app.curate validate data/curation/manifests/<vehicle>.json
python -m app.curate import data/curation/manifests/<vehicle>.json
```

`app.curate init` should seed the accepted parameter registry only.

It must **not** seed Phase 0 semantic fixtures.

The existing `python -m app.seed` remains a development/test fixture command.

## 5. Transaction and idempotence policy

### Vehicle records

Manifest v1 is **CREATE_ONLY**.

If `stable_vehicle_code` already exists:

- fail before writes;
- do not overwrite or merge;
- report that an explicit update workflow is required.

This avoids accidental mutation of accepted engineering evidence.

### Source documents

A source may be reused by stable `source_code`.

If the source code already exists:

- compare immutable/core metadata;
- reuse only if compatible;
- otherwise fail with a source-code conflict.

### Atomicity

A manifest import is one transaction.

If any source, observation, normalized value, scope rule, or evidence rule fails:

- roll back the whole vehicle import.

No partial vehicle record remains.

## 6. Manifest top-level structure

Each manifest contains:

```json
{
  "manifest_version": "1.0",
  "mode": "CREATE_ONLY",
  "record_id": "curation-local-stable-id",
  "vehicle": {},
  "sources": [],
  "load_conditions": [],
  "fitments": [],
  "axles": [],
  "observations": [],
  "values": [],
  "assessments": [],
  "steering_relations": [],
  "geometry_assets": [],
  "conflict_decisions": []
}
```

Sections with no records use an empty list.

## 7. Vehicle section

Required concepts:

- `stable_vehicle_code`
- manufacturer canonical/display name
- commercial model canonical/display name
- market
- generation
- body style
- exact variant/trim
- powertrain/drivetrain/body configuration as applicable
- identity verification state
- Identity Time Basis v1 fields after Issue #7:
  - `model_year_from/to` nullable
  - `identity_time_basis`
  - `identity_time_label_raw`
  - `sale_period_from/to`

The manifest must comply with accepted Identity Time Basis v1.

Do not infer model year.

## 8. Source documents

Each source entry requires:

- `source_code`
- publisher
- authority class
- canonical source type
- optional raw/research source subtype
- title
- URL
- retrieval timestamp
- page/section where useful
- publication/model year only when supported
- applicability note
- access/licensing/archive note where relevant

### Canonical source type

Use the application's simple persistence categories:

- WEB_SPECIFICATION
- OWNER_MANUAL
- SERVICE_MANUAL
- ENGINEERING_DRAWING
- HOMOLOGATION
- PHYSICAL_MEASUREMENT
- OTHER

Research subtypes such as:

- OEM_NEWS
- OEM_BROCHURE_PDF_SCREENSHOT_VERIFIED
- OFFICIAL_CAMPAIGN_TERMS
- WEB_GRADE_LIST
- CONFIGURATOR_PRINT
- OFFICIAL_STORE_CONFIGURATION

remain in a separate manifest field such as `source_subtype_raw` and/or are preserved in notes.

Do not silently discard the richer research subtype.

## 9. Raw observations

Every observation has a local stable `observation_code` and explicitly references exactly one `source_code`.

Required:

- observation_code
- source_code
- vehicle identity claim
- raw label
- raw value
- raw unit nullable
- raw qualifier nullable
- page/section locator
- reported precision where known
- extraction method
- extracted/review date
- ambiguity note if applicable

### Critical rule

Do not create one observation from a research value unless the supporting source is known.

Grouped multi-column evidence remains a raw observation and is not normalized until grade/column applicability is proven.

## 10. Load conditions

Every load condition has a manifest-local `load_condition_code`.

Examples:

- `UNLADEN_OEM`
- `LADEN_OEM`
- `KERB_PLUS_1_PERSON`
- `OEM_LOAD_STATE_UNSPECIFIED`

The code resolves to the database load-condition row created in the same transaction.

Preserve raw OEM wording.

Do not fabricate tyre pressure, axle load or occupant assumptions.

## 11. Fitments

Material wheel/equipment packages use local `fitment_code`.

A normalized value may reference a fitment only when that fitment belongs to the imported vehicle.

If the source does not prove fitment-specific applicability, leave the value configuration-level or hold it.

## 12. Normalized values

Each normalized value has a manifest-local `value_code`.

Required concepts:

- value_code
- parameter_code
- typed value
- canonical unit
- evidence method
- resolution state
- verification state
- availability state
- applicability grade
- semantic metadata
- optional load_condition_code
- optional fitment_code
- evidence_observation_codes

### Initial production-curation default

For imported source-backed values:

- evidence_method = PUBLISHED or MEASURED
- verification_state = REVIEWED by default
- not VERIFIED merely because the importer succeeded
- resolution_state = UNCONTESTED unless conflict evidence exists

### Provenance

A PUBLISHED or MEASURED available value requires at least one `evidence_observation_code`.

The importer resolves those local codes to source-observation IDs and passes them to the existing service boundary as evidence links.

No naked engineering value is allowed.

## 13. Derived / estimated values

Manifest v1 should **not** allow arbitrary user-supplied DERIVED or ESTIMATED numeric values.

Derived/estimated results must be produced by allowlisted application derivation functions after their source inputs exist.

Examples already implemented:

- nominal unloaded tyre radius from tyre notation;
- screening AVT track estimate;
- symmetric screening breakover.

A future safe turning-circle diameter-to-radius rule may be added as a separate bounded derivation.

Until such a rule exists:

- ingest the raw turning-circle observation;
- optionally preserve a text normalized claim if useful;
- do not hand-enter a derived radius as if it were source-published.

## 14. Conflicts

Multiple normalized values for the same parameter may be imported with:

`resolution_state = CONFLICTING`

They remain separate evidence-backed candidates.

Do not set a preferred value merely because one source is newer.

A `conflict_decision` is imported only when there is an explicit reviewed rationale.

If no decision exists:

- keep the conflict unresolved;
- readiness must fail closed where the conflicted parameter is required.

## 15. Parameter assessments

Use assessments for:

- UNKNOWN
- NOT_FOUND_AFTER_SEARCH
- NOT_APPLICABLE

Each assessment should preserve:

- parameter code
- reason
- source families searched
- search notes
- assessed date/reviewer
- next action

Do not create a null/zero normalized value to represent missing data.

## 16. Axle / rear-steering records

Create axle and steering-relation records only when source evidence supports them.

For rear/four-wheel steering:

- system presence may be stored structurally;
- unknown linkage/max angle/phase remains unknown;
- do not synthesize AVT rear-steer behavior.

## 17. Geometry assets

Geometry assets may be imported as:

- PARAMETRIC
- FILE_REFERENCE
- other accepted representation types

For the current pilot, OEM dimension diagrams can be represented as `AXLE_DATUM_GEOMETRY` with parametric/callout content.

Required:

- exact source document
- geometry method
- fidelity
- coordinate-system/datum description
- applicability
- uncertainty/limitations

Do not pretend a dimension diagram is an AVT plan-body polygon or longitudinal lower envelope.

## 18. Validation sequence

Before any database write:

1. parse manifest;
2. validate manifest version/mode;
3. validate all local-code uniqueness;
4. validate cross-references;
5. validate parameter codes against registry;
6. validate Identity Time Basis;
7. validate canonical source/authority values;
8. reject forbidden DERIVED/ESTIMATED direct values;
9. validate evidence requirements;
10. validate fitment/load/geometry references.

During transaction:

1. create/reuse sources;
2. create vehicle configuration;
3. create fitments/load conditions/axles;
4. create observations;
5. create normalized values through `app.services.foundation`;
6. create assessments;
7. create steering/geometry records;
8. create reviewed conflict decisions only if supplied;
9. evaluate readiness;
10. commit only if all steps pass.

## 19. Dry-run behavior

`validate` / `--dry-run` must:

- perform schema/cross-reference checks;
- verify parameter registry and identity rules;
- detect existing vehicle/source conflicts;
- perform database-backed scope validation where required;
- roll back all writes or avoid writes entirely.

Output a concise PASS/FAIL report.

## 20. Import report

Successful import should report:

- vehicle stable code
- source count
- observation count
- normalized value count
- assessment count
- load/fitment/axle/steering/geometry counts
- conflict count
- readiness statuses/blockers
- database URL/path identifier without credentials

## 21. Explicit non-goals

Do not add:

- admin UI
- browser edit forms
- public write API
- autonomous scraping
- auto-normalization from arbitrary text
- automatic conflict winner selection
- bulk web crawling
- destructive update mode

## 22. Phase 1 first proof set

After Issue #7, prove the ingestion path with three deliberately different records:

1. **BYD ATTO 3 MY24 Extended (Local Production)**  
   Explicit MODEL_YEAR identity + laden/unladen clearance.

2. **Mitsubishi Triton Double Cab ULTRA 4WD AT, 2023 release**  
   Non-MY EDITION_RELEASE exact identity + pickup geometry/turning.

3. **Volvo EX30 Ultra Single Motor Extended Range MY2026**  
   Explicit MODEL_YEAR + mirror/body widths + load-qualified clearance + unresolved turning conflict.

Only after these three pass DB-level QA should Wave 1 expand.
