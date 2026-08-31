# Phase 1 Wave 1 Manifest Tranche 1 QA

Date: 2026-08-31
Branch: `chatgpt/phase-1-wave1-manifests-t1`

## Verdict

**PASS — six Wave 1 manifests are ready as importer inputs after Issue #15 sentinel proof.**

Included:
- Tesla Model Y Premium Long Range RWD, 19-inch, 2025+
- Toyota Commuter 2.8 AT high-roof / 15 seats
- Isuzu V-CROSS 2.2 Ddi Z 4-door A/T 4x4
- Nissan Navara PRO-4X 7AT
- BYD SEAL MY24 AWD Performance
- Hyundai IONIQ 6 Exclusive

## Machine QA

- 6/6 unique manifest record IDs
- 6/6 unique stable vehicle codes
- no incompatible source-code reuse
- all observation -> source references resolve
- all load/fitment references resolve
- all normalized parameter codes exist in the accepted registry
- all NUMBER/TEXT primitives match registry data type
- all required semantic attributes are present
- every PUBLISHED value has explicit observation evidence
- no direct DERIVED or ESTIMATED value appears
- exact Identity Time Basis rules pass
- Tesla Model Y longitudinal geometry: delta 0 mm
- Hyundai IONIQ 6 longitudinal geometry: delta 0 mm

## Important curation decisions

### Tesla Model Y
Tesla publishes 12.13 m curb-to-curb turning circle. Manifest v1 does not hand-enter the 6.065 m radius because that would be a DERIVED value. The raw circle is stored as `oem_turning_value_text` and normalized radius remains an UNKNOWN assessment until a registered derivation exists.

### Hyundai IONIQ 6
The official Thailand site labels the product `2024 IONIQ 6`, but does not explicitly say Model Year. The manifest therefore uses `OEM_REVISION_LABEL`, not `MODEL_YEAR`. The exact `Exclusive` engineering specification comes from the official leaflet printed Oct 2025, whose specification/dimension page was visually verified.

### BYD SEAL
RÊVER official campaign terms explicitly say `BYD SEAL MY 24 AWD Performance`, so `MODEL_YEAR=2024` is evidence-supported rather than inferred.

### Toyota Commuter
The raw Thai wording `ไฮเอซและคอมมิวเตอร์หลังคาสูง รุ่นปรับปรุง ปี 2568` is retained as `OEM_REVISION_LABEL`; it is not converted to MY2025.

## Gate

These manifests must not be physically imported until Issue #15 passes the three-sentinel clean-database proof.
