# Logical Relational Schema v1

Status: Accepted control-plane design for Phase 0 implementation  
Date: 2026-08-30

## 1. Purpose

Translate the Vehicle Data Standard into a relational model without prematurely locking database-specific implementation details.

The physical schema may refine names/types/indexes, but it must preserve these entities, relationships and invariants.

## 2. Design rules

1. Vehicle configuration is an identity record, not a bag of specifications.
2. Source observations are appendable evidence.
3. Normalized values do not overwrite observations.
4. One parameter may have multiple observations and conflicting candidate values.
5. Evidence method, conflict/resolution, verification and availability are orthogonal.
6. Derived values retain input lineage and derivation-rule version.
7. Geometry assets are separate from scalar values.
8. AVT mapping is an adapter output.
9. Unknown/not-found is represented explicitly rather than by fake numeric values.
10. Physical schema must remain practical on SQLite and PostgreSQL.

## 3. Entity relationship overview

```text
manufacturer
    |
vehicle_model
    |
vehicle_configuration ---- vehicle_fitment
    |        |                    |
    |        +---- axle ----------+
    |        |       |
    |        |       +---- steering_relation
    |        |
    |        +---- load_condition
    |
source_document
    |
source_observation
    |                 parameter_definition
    +------------------------+
                             |
                      normalized_value
                       /      |       \
            evidence_link  derivation_run  conflict_decision
                              |
                        derivation_input

vehicle_configuration ---- geometry_asset
vehicle_configuration ---- parameter_assessment
vehicle_configuration ---- readiness_result
vehicle_configuration ---- qa_finding
vehicle_configuration ---- avt_mapping_result
```

## 4. Core identity tables

### 4.1 `manufacturer`

Fields:
- id
- canonical_name
- display_name
- country_of_origin optional
- active flag optional

Constraint:
- canonical name unique.

### 4.2 `vehicle_model`

Represents the commercial model family.

Fields:
- id
- manufacturer_id
- canonical_model_name
- display_model_name

Constraint:
- manufacturer + canonical model unique.

### 4.3 `vehicle_configuration`

Represents an exact engineering configuration.

Fields:
- id
- stable_vehicle_code
- vehicle_model_id
- market_code
- generation_name
- chassis_platform_code
- body_style
- model_year_from
- model_year_to nullable
- sale_period_from/to nullable
- variant_trim
- powertrain
- drivetrain
- body_configuration
- identity_notes
- identity_verification_state
- created_at / updated_at

Rules:
- `stable_vehicle_code` unique and never recycled.
- record creation requires market + commercial model + sufficient configuration resolution.
- unresolved DLT model names do not become exact configurations.

### 4.4 `vehicle_fitment`

Represents wheel/tyre/equipment package when it materially changes geometry or steering.

Fields:
- id
- vehicle_configuration_id
- fitment_code
- description
- wheel_package
- equipment_package
- model_year applicability
- default_for_configuration flag
- notes

A configuration may have multiple fitments.

## 5. Axle / steering structure

### 5.1 `axle`

Fields:
- id
- vehicle_configuration_id
- axle_role: FRONT / REAR / INTERMEDIATE / OTHER
- axle_index
- longitudinal_position_mm relative to normalized datum
- axle_group optional
- driven flag nullable
- steered flag nullable
- retractable/self-steering flags nullable
- notes

Simple passenger vehicles normally have front and rear axle records.

### 5.2 `steering_relation`

Fields:
- id
- vehicle_configuration_id
- axle_id
- steering_role: PRIMARY / SECONDARY / LINKED
- linkage_type
- max_steering_angle_deg nullable
- phase_behavior
- angle_ratio nullable
- relation_function/text specification nullable
- speed_min/max applicability nullable
- mode applicability nullable
- source/evidence linkage
- notes

This table is intentionally capable of representing rear/four-wheel steering.

## 6. Load state

### 6.1 `load_condition`

Reusable structured applicability record.

Fields:
- id
- vehicle_configuration_id nullable when generic
- name
- mass_basis
- total_mass_kg nullable
- occupant_count nullable
- payload_kg nullable
- front_axle_load_kg nullable
- rear_axle_load_kg nullable
- front_tyre_pressure nullable
- rear_tyre_pressure nullable
- tyre_pressure_unit
- suspension_mode nullable
- ride_height_mode nullable
- raw_oem_wording nullable
- source_document_id nullable
- notes

Normalized values/geometry may reference a load condition.

## 7. Parameter dictionary

### 7.1 `parameter_definition`

Parameter semantics belong in data, not scattered application code.

Fields:
- id
- parameter_code unique
- display_name
- family
- data_type: NUMBER / TEXT / BOOLEAN / ENUM / JSON
- canonical_unit nullable
- semantic_definition
- applicability_notes
- deprecated flag
- replacement_parameter_code nullable
- created_version

Examples:
- `overall_length_mm`
- `turning_radius_m`
- `static_loaded_tyre_radius_front_mm`
- `screening_breakover_angle_deg`

## 8. Source/evidence tables

### 8.1 `source_document`

Fields:
- id
- source_code unique
- title
- publisher
- authority_class
- source_type
- market_code nullable
- publication_date/year nullable
- model_year applicability nullable
- url
- retrieved_at
- local_snapshot_reference nullable
- content_hash nullable
- page_section_default nullable
- access/licensing_notes nullable
- archival_status
- notes

### 8.2 `source_observation`

Literal observation before normalization.

Fields:
- id
- vehicle_configuration_id nullable until identity resolution
- vehicle_identity_claim text
- source_document_id
- raw_label
- raw_value
- raw_unit
- raw_qualifier
- raw_excerpt nullable
- page_section_locator
- reported_precision nullable
- uncertainty_value nullable
- uncertainty_unit nullable
- extraction_method
- extracted_at
- extracted_by/reviewer
- ambiguity_note nullable

Rules:
- raw fields are immutable except correction with audit history.
- source observation is not itself a normalized engineering claim.

## 9. Normalized values

### 9.1 `normalized_value`

Fields:
- id
- vehicle_configuration_id
- vehicle_fitment_id nullable
- parameter_definition_id
- numeric_value nullable
- text_value nullable
- boolean_value nullable
- enum_value nullable
- json_value nullable
- canonical_unit nullable
- load_condition_id nullable
- applicability_from/to nullable
- evidence_method: PUBLISHED / MEASURED / DERIVED / ESTIMATED / NONE
- resolution_state
- verification_state
- availability_state
- authority_grade/display grade nullable
- applicability_grade
- precision nullable
- uncertainty_value/unit nullable
- normalization_rule_version nullable
- preferred flag
- created_at / reviewed_at
- reviewer nullable

Rules:
- exactly one typed value field should be populated for AVAILABLE values according to parameter data type.
- no numeric value for UNKNOWN / NOT_FOUND_AFTER_SEARCH.
- `preferred=true` does not delete competing values.
- a DERIVED value requires a derivation run.
- a PUBLISHED/MEASURED value requires evidence linkage.

### 9.2 `evidence_link`

Many-to-many link between normalized value and observations.

Fields:
- normalized_value_id
- source_observation_id
- evidence_role: PRIMARY / SUPPORTING / CONFLICTING / IDENTITY / OTHER

Composite uniqueness prevents duplicate links.

## 10. Unknown / research assessment

### 10.1 `parameter_assessment`

Fields:
- id
- vehicle_configuration_id
- vehicle_fitment_id nullable
- parameter_definition_id
- availability_state
- unknown_reason
- source_families_searched nullable
- search_notes nullable
- assessed_at
- reviewer
- next_action nullable

Use when no defensible normalized value exists.

Do not create numeric zero/null placeholders pretending to be values.

## 11. Derivation lineage

### 11.1 `derivation_rule`

Fields:
- id
- rule_code
- version
- name
- output_parameter_definition_id
- formula_description
- validity_conditions
- uncertainty_method
- active flag
- reference_basis
- unique(rule_code, version)

### 11.2 `derivation_run`

Fields:
- id
- derivation_rule_id
- vehicle_configuration_id
- output_normalized_value_id unique
- executed_at
- implementation_version
- result_notes

### 11.3 `derivation_input`

Fields:
- derivation_run_id
- input_normalized_value_id
- input_role

This makes every derived value reproducible.

## 12. Conflict/preference decisions

### 12.1 `conflict_decision`

Fields:
- id
- vehicle_configuration_id
- parameter_definition_id
- selected_normalized_value_id nullable
- decision_state
- rationale
- decided_at
- reviewer
- superseded_by_decision_id nullable

Candidate values remain in `normalized_value`.

## 13. Geometry assets

### 13.1 `geometry_asset`

Fields:
- id
- vehicle_configuration_id
- vehicle_fitment_id nullable
- geometry_role
- representation_type: POINT_SET / POLYLINE / POLYGON / PARAMETRIC / FILE_REFERENCE
- geometry_data JSON/text or file reference
- unit
- coordinate_system_version
- source_coordinate_description nullable
- normalization_transform nullable
- load_condition_id nullable
- body/mirror inclusion semantics
- geometry_method
- geometry_fidelity
- uncertainty description/value
- source_document_id nullable
- derivation_run_id nullable
- notes

Rules:
- SIDE_SILHOUETTE and LONGITUDINAL_LOWER_ENVELOPE are different roles.
- normalized geometry requires the v1 datum or an explicit transform.

## 14. Readiness / QA

### 14.1 `readiness_result`

Fields:
- id
- vehicle_configuration_id
- vehicle_fitment_id nullable
- readiness_type:
  - IDENTITY_RESOLVED
  - DIMENSION_READY
  - SWEPT_PATH_PARTIAL
  - AVT_READY
  - RAMP_SCREENING_READY
  - VERTICAL_CLEARANCE_READY
  - CLIENT_REFERENCE_READY
- status: READY / NOT_READY / INDETERMINATE
- rule_version
- evaluated_at
- blocking_reasons JSON/list
- supporting_value_ids optional

Readiness is rule-derived, not manually decorated.

### 14.2 `qa_finding`

Fields:
- id
- vehicle_configuration_id nullable
- source_document_id nullable
- normalized_value_id nullable
- finding_code
- severity
- status
- message
- created_at
- resolved_at
- resolution_note

## 15. AVT adapter

### 15.1 `avt_mapping_result`

Fields:
- id
- vehicle_configuration_id
- vehicle_fitment_id nullable
- adapter_version
- target_avt_version nullable
- mapping_status
- generated_at
- mapping_payload JSON
- blocker_list JSON
- source_value_ids JSON/reference table

Rules:
- adapter never becomes authoritative source data.
- unknown/insufficient semantics produce blockers.
- mapping payload must be reproducible from accepted normalized values and adapter version.

## 16. Key uniqueness/index expectations

At minimum index:
- manufacturer/model names
- stable_vehicle_code
- market/generation/variant
- parameter_code
- source_code
- vehicle_configuration + parameter
- availability/resolution/verification states
- readiness type/status
- QA finding status/severity

## 17. Physical-schema implementation latitude

Codex may:
- use UUIDs or integer surrogate keys;
- use SQLAlchemy enums or constrained strings;
- normalize some repeated enums into lookup tables;
- use association tables instead of JSON where it improves integrity.

Codex may **not**:
- merge raw observations and normalized values;
- collapse the four orthogonal state dimensions;
- remove derivation lineage;
- replace geometry role semantics with one generic image/file field;
- hard-code all parameter definitions as Python-only enums with no data registry;
- make PostgreSQL migration impractical.

## 18. Phase 0 proof requirement

The physical schema is accepted only when every deterministic fixture in `PILOT_AND_ACCEPTANCE.md` can be represented and queried without semantic loss.
