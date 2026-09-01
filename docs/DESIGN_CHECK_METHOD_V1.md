# Design Check Method v1

Method identifier: `DESIGN_CHECK_V1`
Status: implementation method for Issue #27
Scope: deterministic screening of explicit user-entered scalar constraints against exact curated vehicle configurations

## 1. Purpose and boundary

Design Check v1 answers:

> Given explicit site/design limits, which exact curated vehicle configurations are within the entered limits, which exceed them, and which cannot be decided from the available evidence?

It is an evidence-aware screening workflow. It does not simulate a vehicle or certify a site. It does not perform swept-path simulation, parking-aisle maneuver solving, column/corner collision, ramp grounding/contact, vertical-alignment solving, CAD analysis, regulatory/code compliance, or parking-space compliance. It does not add a legal minimum, recommended design standard, or default client allowance.

The v1 implementation uses URL/query state only. No scenario table or migration is introduced.

## 2. Result states and aggregation

Each active constraint returns exactly one result:

- `PASS` — an eligible exact-configuration value exists, the required semantics match, and the value is within the explicit effective limit;
- `FAIL` — an eligible exact-configuration value exists, the required semantics match, and the value exceeds the explicit effective limit;
- `INDETERMINATE` — the required value or semantics are absent, conflicting, rejected, mismatched, out of scope, or otherwise not defensible for an automatic result.

Unknown is never treated as `PASS`.

For one vehicle:

1. Any active `FAIL` makes the overall result `FAIL`.
2. With no `FAIL`, any active `INDETERMINATE` makes the overall result `INDETERMINATE`.
3. Only all-active-constraint `PASS` results make the overall result `PASS`.
4. With zero active constraints, no suitability verdict is calculated.

All individual constraint results are retained even when the overall result is already `FAIL`.

## 3. Explicit inputs and units

The request model accepts these optional constraints. A non-blank limit activates its check:

| Constraint | Explicit user inputs | Internal unit |
|---|---|---|
| Clear height | minimum available clear height; vertical allowance | mm |
| Width envelope | available clear width; lateral allowance per side; requested envelope | mm |
| Overall length | maximum acceptable vehicle length | mm |
| Turning-envelope screening | maximum value; radius/diameter shape; curb-to-curb/wall-to-wall reference | m |

The vertical allowance defaults to `0 mm` only when the height check is active and the user leaves that field blank; the UI labels this as “0 = no additional allowance.” Width allowance is explicit and must be supplied when width is active, including `0` when no allowance is required. No other normative value is prefilled.

Negative, non-finite, or non-numeric inputs are invalid. A non-positive active limit is invalid. An incomplete active width or turning input is an input error, not a vehicle `PASS` or `FAIL`.

## 4. Supported checks

### 4.1 Minimum clear height

Vehicle parameter: `overall_height_mm` with canonical unit `mm`.

Formula:

```text
effective_height_limit_mm = available_clear_height_mm - vertical_allowance_mm
height_margin_mm = effective_height_limit_mm - vehicle_height_mm
```

Decision:

```text
PASS when vehicle_height_mm <= effective_height_limit_mm
FAIL when vehicle_height_mm > effective_height_limit_mm
```

The check compares the curated overall-height value with the entered minimum clear height only. It does not turn a floor-to-ceiling dimension into clear height and does not solve beams, sprinklers, signs, MEP, door equipment, slopes, or dynamic pitch. A material unresolved height definition, applicability state, scope, or evidence state returns `INDETERMINATE`.

### 4.2 Width envelope

Vehicle parameter mapping is exact:

| Requested envelope | Required parameter | Required metadata |
|---|---|---|
| Body excluding mirrors | `overall_width_body_mm` | `width_envelope_definition = BODY_EXCLUDING_MIRRORS` |
| Mirrors open | `overall_width_including_mirrors_mm` | `width_envelope_definition = INCLUDING_MIRRORS_OPEN` |
| Mirrors folded | `overall_width_mirrors_folded_mm` | `width_envelope_definition = INCLUDING_MIRRORS_FOLDED` |
| OEM-reported / unspecified screening | `overall_width_reported_mm` | source-defined metadata is displayed; unspecified semantics remain explicit |

The optional OEM-reported/unspecified choice is labelled as screening only. It does not establish mirror inclusion. A body width is never substituted for an open- or folded-mirror width, and a reported/unspecified width is never silently promoted to body width.

Formula:

```text
effective_width_limit_mm = available_clear_width_mm - 2 * lateral_allowance_each_side_mm
width_margin_mm = effective_width_limit_mm - vehicle_width_mm
```

Decision uses `vehicle_width_mm <= effective_width_limit_mm` for `PASS`; otherwise `FAIL` when the value and exact envelope are eligible. Missing or mismatched envelope data returns `INDETERMINATE` with the known mismatch where available.

### 4.3 Overall length

Vehicle parameter: `overall_length_mm` with canonical unit `mm`.

Formula:

```text
length_margin_mm = maximum_vehicle_length_mm - vehicle_length_mm
```

Decision uses `vehicle_length_mm <= maximum_vehicle_length_mm` for `PASS`; otherwise `FAIL`. The method does not derive body length from wheelbase plus overhangs.

### 4.4 Turning-envelope screening

This check is explicitly labelled **Turning-envelope screening**. It compares like-for-like normalized turning semantics; it is not a swept-path simulation and does not prove negotiation of an aisle, corner, column layout, ramp, porte-cochère, or access geometry.

User input is a maximum radius or diameter in metres and an exact reference of `CURB_TO_CURB` or `WALL_TO_WALL`.

```text
site_radius_m = maximum_turning_value_m                         when input shape = RADIUS
site_radius_m = maximum_turning_value_m / 2                     when input shape = DIAMETER
```

Vehicle parameter: `turning_radius_normalized_m` with canonical unit `m`. This parameter is already a normalized radius; Design Check does not parse `oem_turning_value_text`, halve it, or infer its shape. Its metadata must resolve `turning_radius_or_diameter` to `RADIUS`; a value marked only as `DIAMETER` is not reinterpreted here. The candidate must also exactly match the requested `turning_reference`.

Additional eligibility:

- for curb-to-curb, `turning_axle_scope` must be `ALL_AXLES` or `ACTIVE_AXLES`;
- for wall-to-wall, `turning_wall_envelope_scope` must be `BODY_ONLY` or `BODY_AND_LOADS`;
- `OEM_UNSPECIFIED` reference, shape, axle scope, or wall envelope scope is not eligible where that semantic is required;
- a raw OEM turning text value without a normalized radius remains `INDETERMINATE`;
- a curb/wall mismatch remains `INDETERMINATE`.

The normalized decision is:

```text
turning_radius_margin_m = site_radius_m - vehicle_radius_m
PASS when vehicle_radius_m <= site_radius_m
FAIL when vehicle_radius_m > site_radius_m
```

For display, a diameter input shows the equivalent vehicle diameter and diameter margin:

```text
vehicle_diameter_m = 2 * vehicle_radius_m
diameter_margin_m = maximum_turning_diameter_m - vehicle_diameter_m
```

The underlying candidate remains the curated normalized-radius value.

### 4.5 Mass limit

Mass-limit checking is explicitly deferred from v1. It is not exposed as a result and does not delay the main workflow. A future implementation must require an explicit `KERB` or `GVW` basis and must not substitute one mass basis for the other.

## 5. Evidence and candidate eligibility

The service maps only exact configuration values from the existing database into the evaluator. For each requested parameter, the evaluator requires:

- `availability_state = AVAILABLE`;
- `verification_state != REJECTED`;
- `applicability_grade` of `EXACT_CONFIGURATION` or `SAME_GEOMETRY_CONFIRMED`;
- an evidence method of `PUBLISHED`, `MEASURED`, or controlled `DERIVED`;
- at least one evidence link;
- complete derivation rule/lineage metadata when the value is `DERIVED`;
- the semantic metadata required by the check;
- a unique applicable value/scope, unless an existing explicit curation decision selects one candidate.

`ESTIMATED` values are not eligible for an automatic v1 verdict because the result must not silently promote an estimate to physical proof. `SUPERSEDED` and `NOT_APPLICABLE` values are not candidates. Rejected, unavailable, incomplete, or semantically invalid data produce `INDETERMINATE`.

An active, non-superseded curation conflict decision may select one conflicting normalized value. The result exposes “Selected conflict retained” so that the selection is not silent. If conflicting values have no active auditable selection, the result is `INDETERMINATE`. Multiple applicable values with no unique selection are also `INDETERMINATE`.

Fitment and load-condition scope are preserved in the candidate snapshot and result. A single uniquely scoped value may be evaluated with that scope displayed. Multiple competing scopes are not reduced to the most favourable value.

## 6. Explainability and controlling information

Every result cell exposes, where available:

- result state;
- parameter code and value/unit;
- requested constraint;
- allowance;
- effective limit;
- signed margin;
- semantic cue;
- fitment/load scope;
- evidence method/state;
- exact vehicle evidence/detail link;
- a precise decision reason.

For an overall `PASS`, the UI labels the highest `vehicle value / effective limit` among comparable active upper-bound constraints **Closest active limit**. This is a utilization cue, not a universal governing engineering condition.

For an overall `FAIL`, the UI retains every failed constraint and may identify the greatest positive relative exceedance as **Largest exceedance**. Raw mm, m, and kg margins are never compared directly across constraints.

For an overall `INDETERMINATE` with no `FAIL`, indeterminate constraints are labelled **Decision blocker(s)**.

## 7. Examples

### Height

```text
minimum clear height = 2100 mm
vertical allowance = 100 mm
effective limit = 2000 mm
vehicle height = 1835 mm
margin = +165 mm
result = PASS
```

A vehicle height of `2285 mm` gives a `-285 mm` margin and `FAIL`. An unavailable height gives `INDETERMINATE`.

### Width semantics

```text
available clear width = 2100 mm
lateral allowance = 50 mm each side
requested envelope = mirrors open
effective limit = 2000 mm
```

A vehicle with only body-excluding-mirrors width is `INDETERMINATE`; body width is not substituted.

### Turning

```text
maximum curb-to-curb diameter = 11.0 m
vehicle normalized curb-to-curb radius = 5.3 m
equivalent vehicle diameter = 10.6 m
margin = +0.4 m diameter
result = PASS
```

Raw OEM text such as “turning radius 5.2 m” with an unspecified reference is `INDETERMINATE`; the text is displayed as evidence but is not parsed by this method.
