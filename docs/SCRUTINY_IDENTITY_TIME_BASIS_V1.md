# Scrutiny — Identity Time Basis v1

Date: 2026-08-31  
Decision: **GO WITH CONDITIONS**  
Scope: vehicle temporal identity only; no change to geometry/evidence/AVT/ramp semantics.

## 1. Decision under review

Should `model_year_from` remain mandatory for every exact Thai-market vehicle configuration?

## 2. Problem framing

The current contract assumes that an exact engineering configuration always has a source-supported model year.

Real Thai-market curation shows this is not consistently true.

OEMs may identify a configuration through:

- explicit model year, e.g. `MY24`;
- a Thai revision/year label whose semantics are not proven to mean model year;
- a uniquely named limited/special edition and release;
- a bounded product/sale-period revision;
- a current grade without any published model-year label.

The engineering requirement is **temporal/configuration disambiguation**, not mandatory completion of a field called model year.

## 3. Evidence cases from Phase 1

### BYD ATTO 3

Official RÊVER campaign material explicitly uses:

> NEW BYD ATTO 3 MY24 Extended (Local Production)

This is legitimate `MODEL_YEAR` evidence.

### Mazda MX-5 35th Anniversary Edition

Mazda Thailand identifies the exact limited `35th Anniversary Edition`, launch/release in March 2025 and extremely limited Thai allocation, but the reviewed Thai source does not explicitly call it `MY2025`.

The edition/release can distinguish the engineering configuration without inventing a model year.

### Kia EV5 Earth Long Range

The current Thai specification identifies the exact grade and fitment. Page asset names include `25my`, but user-visible source wording does not explicitly establish model-year semantics.

An implementation filename must not be silently promoted to an engineering identity fact.

### MG IM6

MG Thailand identifies the exact current grades and four-wheel-steering equipment but does not label IM6 with a model year on the reviewed product pages.

The same MG navigation explicitly labels another vehicle `NEW MG4 MY2026`, demonstrating that model-year wording is used when MG chooses to publish it. Absence of such wording for IM6 should remain absence, not inference.

### Toyota Thailand

Toyota sources commonly use wording such as `รุ่นปรับปรุงปี 2568` or `รถยนต์ ... ปี 2567`. That wording is useful temporal applicability evidence but must not automatically become `MY2025` / `MY2024` unless the OEM source establishes that equivalence.

## 4. Failure mode of the current rule

Keeping mandatory `model_year_from` creates two bad outcomes:

1. **fabricated precision** — launch/revision/publication year gets inserted as a model year merely to satisfy schema;
2. **false incompleteness** — a uniquely identifiable engineering edition/configuration cannot be represented as exact even when its temporal identity is otherwise adequate.

Both conflict with the project principle:

> Unknown is acceptable. Unsupported precision is not.

## 5. Alternatives considered

### A. Keep model year mandatory and infer from launch/revision year
**NO-GO.** Violates evidence semantics.

### B. Keep model year mandatory and hold every non-MY vehicle as partial forever
**REJECTED.** Overfits North-American-style model-year conventions and unnecessarily blocks valid Thai-market identity.

### C. Make model year nullable and introduce evidence-backed identity time basis
**SELECTED.**

This preserves explicit model-year data when available and adds a controlled representation for Thai-market identity mechanisms.

## 6. Proposed contract

Add:

- `identity_time_basis`:
  - MODEL_YEAR
  - OEM_REVISION_LABEL
  - EDITION_RELEASE
  - SALE_PERIOD
  - MULTIPLE
  - UNKNOWN
- `identity_time_label_raw` nullable
- existing `sale_period_from/to`
- nullable `model_year_from/to`

### Exact-resolution rules

`RESOLVED_EXACT` requires an evidence-backed temporal discriminator.

- MODEL_YEAR -> `model_year_from` required.
- OEM_REVISION_LABEL -> raw label required.
- EDITION_RELEASE -> raw edition/release label required; release/sale evidence retained.
- SALE_PERIOD -> sufficiently bounded sale-period applicability required.
- MULTIPLE -> at least two compatible supported bases, with raw evidence.
- UNKNOWN -> cannot support `RESOLVED_EXACT`.

A source retrieval date alone does not make a configuration exact.

## 7. Scope boundaries

This amendment does **not**:

- weaken exact market/generation/variant/fitment requirements;
- allow a generic current grade to become exact merely because it is on a current website;
- reinterpret Thai revision year as model year;
- change engineering parameter semantics;
- change source/provenance rules;
- change AVT/ramp rules.

Kia EV5 and MG IM6 may therefore remain PARTIAL until stronger temporal applicability evidence is found even after this schema change.

Mazda 35th Anniversary Edition is a candidate for exact resolution by `EDITION_RELEASE` once the edition/release evidence is linked under the amended policy.

## 8. Migration / reversibility

Required implementation:

- new Alembic revision after `0001_phase0_foundation`;
- make `vehicle_configuration.model_year_from` nullable;
- add `identity_time_basis`;
- add `identity_time_label_raw`;
- preserve all existing data;
- existing records with model years backfill `identity_time_basis=MODEL_YEAR`;
- downgrade must be explicit and must refuse/descope safely if records without model year would become invalid rather than fabricating years.

Do not rewrite historical revision 0001.

## 9. Acceptance gates

1. Existing model-year fixtures remain valid.
2. Exact MODEL_YEAR configuration without `model_year_from` is rejected.
3. Exact EDITION_RELEASE configuration can have null model year when raw edition label/evidence is present.
4. Exact OEM_REVISION_LABEL configuration can have null model year when raw revision label/evidence is present.
5. UNKNOWN time basis cannot be RESOLVED_EXACT.
6. Launch year alone is not automatically written to model year.
7. Migration from current Phase 0 DB preserves existing rows.
8. Fresh DB upgrade 0001 -> new revision passes.
9. Downgrade behavior is explicit and does not fabricate missing model years.
10. Search/detail/export surfaces preserve the new identity time basis without requiring UI redesign.

## 10. Risks

- SALE_PERIOD can be too weak if a grade name persists through geometry changes. Exact resolution under SALE_PERIOD therefore requires evidence that the product revision is sufficiently bounded.
- OEM revision labels can look like model years. The raw wording must remain preserved and semantically separate.
- Existing external consumers may assume model year is always an integer; Phase 1 has no production consumer yet, so this is the lowest-risk time to correct the contract.

## 11. Verdict

**GO WITH CONDITIONS — High confidence.**

This is a small, evidence-driven correction discovered at the correct time: before production pilot ingestion.

Proceed with the normative documentation amendment, then implement one bounded migration/domain-validation change. Do not suspend source research while the software correction is being made.
