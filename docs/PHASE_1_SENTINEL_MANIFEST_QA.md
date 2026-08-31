# Phase 1 Sentinel Manifest QA v1

Date: 2026-08-31  
Branch: `chatgpt/phase-1-ingestion-contract-v1-final`  
Dependency: Identity Time Basis v1 implementation merged as `f2e311578694479a8bce52ecdcb46dc18fdc4c28`

## Verdict

**PASS — sentinel manifests are ready to be used as importer acceptance fixtures.**

This is a manifest/data-contract review only. No record has been inserted into a curated database yet.

## Sentinel set

| Manifest | Sources | Raw observations | Normalized values | Load conditions | Fitments | Assessments |
|---|---:|---:|---:|---:|---:|---:|
| BYD ATTO 3 MY24 Extended Local | 2 | 13 | 15 | 2 | 0 | 2 |
| Mitsubishi Triton ULTRA 4WD AT 2023 | 2 | 7 | 12 | 1 | 0 | 2 |
| Volvo EX30 Ultra SMER MY2026 | 3 | 14 | 15 | 1 | 1 | 3 |

## Machine-check results

All three manifests pass:

- `manifest_version == 1.0`
- `mode == CREATE_ONLY`
- unique source codes
- unique observation codes
- unique value codes
- unique load-condition codes
- unique fitment codes
- every observation references a declared source
- every source-backed load condition references a declared source
- every value uses a parameter code present in the accepted 48-parameter registry
- every PUBLISHED/MEASURED value has one or more observation references
- every evidence observation code resolves inside the same manifest
- every load-condition reference resolves
- every fitment reference resolves
- no direct DERIVED/ESTIMATED value appears in manifest v1
- exact Identity Time Basis representation is valid

## Registry/data-type QA

Every sentinel normalized candidate was checked against the parameter registry:

- NUMBER parameters use JSON numeric primitives
- TEXT parameters use JSON strings
- required semantic attributes are present
- controlled width-envelope values are valid
- controlled track-definition values are valid
- turning-radius values use explicit `RADIUS` semantics
- turning reference and axle scope use controlled values
- clearance values carry controlled `clearance_type`
- required clearance load-condition references are present

No registry/type/semantic error was found.

## BYD ATTO 3 proof purpose

Proves:

- explicit `MODEL_YEAR` exact identity;
- official-local-distributor source class;
- two source documents contributing identity and engineering observations;
- unladen and laden clearance as separate source-backed values;
- two structured load conditions;
- OEM track retained as OEM-unspecified rather than AVT track;
- unresolved AVT outer-face track represented as parameter assessments.

Expected import behavior:

- configuration identity READY;
- dimensions/client-reference may become partially/fully ready according to existing rules;
- AVT_READY remains blocked.

## Mitsubishi Triton proof purpose

Proves:

- exact non-MY `EDITION_RELEASE` identity with null model year;
- release identity source separated from engineering brochure source;
- direct pickup dimensions;
- source-qualified length including rear bumper;
- unknown load state represented structurally rather than guessed;
- minimum turning radius retained with OEM-unspecified curb/wall reference;
- OEM track remains separate from AVT outer-face track.

Expected import behavior:

- Identity Time Basis v1 is exercised in a real non-MY exact record;
- AVT_READY remains blocked.

## Volvo EX30 proof purpose

Proves:

- explicit `MODEL_YEAR` identity;
- exact 19-inch fitment;
- same-geometry-confirmed dimensional evidence;
- body / mirrors-open / mirrors-folded width separation;
- load-qualified height and clearance at kerb weight plus one person;
- two conflicting official turning-circle text claims;
- no fabricated normalized turning radius;
- explicit `turning_radius_normalized_m = UNKNOWN` assessment.

Expected import behavior:

- both turning text claims persist as separate CONFLICTING values;
- no conflict decision is created;
- turning readiness fails closed;
- fitment-specific tyre/wheel values remain scoped to WHEEL19.

## Importer implementation constraints discovered during QA

### 1. Manifest value routing

The manifest uses a curator-friendly field:

`value`

The importer must use the parameter registry `data_type` to map to exactly one existing persistence field:

- NUMBER -> `numeric_value`
- TEXT -> `text_value`
- BOOLEAN -> `boolean_value`
- ENUM -> `enum_value`
- JSON -> `json_value`

No type coercion solely to make import pass.

### 2. Research source subtype preservation

The database has canonical `source_type` but no `source_subtype_raw` column.

Importer must retain richer research subtype in the existing source notes/metadata without changing the physical schema.

### 3. Manufacturer / model reuse

Importer should:

- reuse manufacturer by exact canonical name;
- reuse vehicle model by manufacturer + exact canonical model name;
- create only when absent;
- never mutate an existing manufacturer/model merely because display wording differs in a manifest.

A material metadata mismatch should be reported, not silently overwritten.

### 4. Source reuse

Reuse existing `source_code` only when core source identity is compatible.

A conflicting existing source code must fail the vehicle transaction.

### 5. Atomicity

Each sentinel import is a single transaction.

An invalid observation/value/source reference must leave:

- no vehicle configuration;
- no partial observations;
- no partial normalized values;
- no new load/fitment/geometry rows.

Reusable pre-existing source/manufacturer/model rows must remain unchanged.

## Negative acceptance fixtures required for importer

Importer implementation must add automated tests for at least:

1. unknown parameter code -> fail before commit;
2. missing evidence observation -> fail;
3. observation references undeclared source -> fail;
4. load-condition reference missing -> fail;
5. fitment reference missing -> fail;
6. direct DERIVED value -> fail;
7. direct ESTIMATED value -> fail;
8. JSON primitive does not match registry data type -> fail;
9. duplicate `stable_vehicle_code` -> fail create-only;
10. existing `source_code` with incompatible metadata -> fail;
11. exact invalid Identity Time Basis -> fail;
12. failure in final value of manifest -> whole vehicle transaction rolls back.

## Import proof gate

Importer is not accepted after unit tests alone.

After implementation and CI:

1. create a clean curated SQLite database;
2. Alembic upgrade to head;
3. seed parameter registry only;
4. validate all three sentinel manifests;
5. import all three;
6. query source -> observation -> normalized-value lineage;
7. inspect readiness results;
8. export CSV/XLSX;
9. verify Volvo conflict remains unresolved;
10. confirm Phase 0 synthetic fixture rows are absent.

Only then may Wave 1 expansion begin.
