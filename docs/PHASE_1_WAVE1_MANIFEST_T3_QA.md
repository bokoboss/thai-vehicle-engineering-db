# Phase 1 Wave 1 Manifest Tranche 3 QA

Date: 2026-08-31

## Verdict

**PASS — final six Wave 1 manifests pass pre-import curation QA.**

Included:
- Ford Ranger Wildtrak 2.0L Bi-Turbo 4x4 10AT — historical Next-Generation configuration
- Tesla Model 3 Premium Long Range RWD — 2024+
- New BYD DOLPHIN Extended Range (Local Production)
- Honda Civic e:HEV RS — 23 Jul 2026 release
- Honda Accord e:HEV RS — 22 Aug 2025 release
- MG IM6 Long Range — 22 Aug 2025 release

## Machine QA

- 6 unique record IDs and stable vehicle codes
- no incompatible source-code reuse
- all local source/observation/value/load/fitment references resolve
- all parameter codes exist in registry
- primitive types match registry data types
- required semantic attributes are present
- every PUBLISHED value has explicit observation evidence
- no direct DERIVED/ESTIMATED value appears
- exact Identity Time Basis rules pass
- Tesla Model 3 longitudinal geometry delta = 0 mm
- Honda authority-B values are backed only by REPUTABLE_SECONDARY observations

## Important decisions

### Ford Ranger
The Bi-Turbo Wildtrak is retained as a historical exact configuration. Current 2026 single-turbo Wildtrak evidence is comparison-only and does not overwrite historical geometry.

### Tesla Model 3
11.7 m curb-to-curb turning circle remains source text. The 5.85 m radius is not hand-entered because it is a derived value and manifest v1 forbids direct derivations.

### BYD DOLPHIN
Uses bounded SALE_PERIOD 1 Mar–5 Apr 2026 from official RÊVER campaign terms for the exact Extended Range Local Production configuration.

### Honda Civic e:HEV RS
Honda Thailand provides exact identity and shared A1 values. ZigWheels exact-grade evidence resolves selected RS grouped values and remains authority grade B. Steering lock-to-lock remains UNKNOWN because exact RS mapping is not independently resolved.

### Honda Accord e:HEV RS
Honda Thailand provides release/current continuity and shared A1 values. Selected grouped RS values from ZigWheels remain authority grade B. The wheel value is stored only as `18-inch`; rim width is not inferred.

### MG IM6 Long Range
Engineering values and four-wheel-steering presence are OEM Thailand. Dated 22 Aug 2025 release evidence remains REPUTABLE_SECONDARY. Promotional alias `Premium Long Range` is retained as alias evidence and does not silently rename the engineering grade.

MG wheel values now have their own raw OEM wheel observation; they are not supported by tyre-only observations.

## Gate

These manifests must not be physically imported until Issue #15 passes the three-sentinel clean-database proof.
