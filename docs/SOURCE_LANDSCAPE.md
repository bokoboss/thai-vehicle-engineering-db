# Thailand Vehicle Source Landscape v1

Status: Research-derived curation guide  
Research date: 2026-08-30

## 1. Purpose

Guide source acquisition by showing what kinds of engineering data are realistically available from current Thai-market source ecosystems.

This is a **source-coverage guide**, not a guarantee that every model from a manufacturer has the listed fields.

## 2. Coverage legend

- **R** — routinely present in sampled current primary/official sources
- **S** — sometimes / model dependent
- **X** — rarely found
- **U** — effectively unavailable in the public sources sampled

## 3. Basic-geometry source coverage

| Manufacturer | L/W/H | Mirror width | Wheelbase | F/R tread/track | F/R overhang | Ground clearance | Loaded/unloaded GC | Rim/tyre | Kerb/GVW | Axle loads |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Toyota | R | X | R | R | X | R | X | R | S | X |
| Lexus | R | S | R | R | X | R | X | R | R | X |
| Honda | R | X | R | R | X | R | X | R | S | X |
| Isuzu | R | X | R | R | X | R | S | R | R | S |
| Mitsubishi | S–R | X | S–R | S | X | S–R | X | R | S | X |
| Ford | R | S | R | R | S | R | X | R | R | S |
| Nissan | R | X | R | S–R | X | R | X | R | R | S |
| Mazda | R | X | R | S | X | R | S–R | R | S | X |
| Suzuki | R | X | R | R | X | R | X | R | R | X |
| BYD / official Thai distributor | R | X | R | R | X | R | R | R | R | X |
| MG | R | X | R | S | X | R | S | R | S | X |
| GWM / HAVAL / ORA / TANK | R | X | R | R | X | R | S | R | S | X |
| Tesla | R | R | R | R | X | R | S | R | R | X |
| Mercedes-Benz | R | R | R | S | X | S | S | R | R | X |
| BMW | R | R | R | S | X | S | X | R | R | X |
| MINI | S–R | S | R | S | X | S | X | R | S | X |
| Volvo | R | R | R | R | X | R | S | R | R | X |
| Hyundai | R | X | R | R | X | R | X | R | R | X |
| Kia | R | X | R | S | S | R | X | R | R | X |

## 4. Advanced-engineering source coverage

| Manufacturer | Steering ratio / wheel LTL | Max actual road-wheel angle | Turning value | Definition clarity | Wall-to-wall | Approach/departure/breakover | AVT-grade plan outline | Longitudinal lower profile |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Toyota | X | U | R | X | U | S off-road | X | U |
| Lexus | X | U | R | S | U | X | X | U |
| Honda | S–R | U | R | X | U | X | X | U |
| Isuzu | X | U | R | X | U | S | X | U |
| Mitsubishi | X | U | S–R | X | U | S | X | U |
| Ford | X–S | U | S | X | U | S | X–S technical/body-builder | U |
| Nissan | X | U | R | X | U | S | X | U |
| Mazda | X | U | R | R on sampled models | U | X | X | U |
| Suzuki | X | U | R | X | U | X | X | U |
| BYD | X | U | R | X | U | X | X | U |
| MG | S steering/RWS info | X | R | X | U | X | X | U |
| GWM | X | U | S–R | X | U | S off-road | X | U |
| Tesla | S–R | X | R | R on Model Y | X | X | X | U |
| Mercedes-Benz | S, especially RWS | X | S | S | X | S specialist/off-road | X | U |
| BMW | X | U | S | X | U | X | X | U |
| MINI | X | U | S | X | U | X | X | U |
| Volvo | X | U | S–R | S | U | X | X | U |
| Hyundai | X | U | S | X | U | X–S | X | U |
| Kia | X | U | R some models | X | U | X | S dimension illustrations | U |

## 5. What this means for the project

Public retail/owner sources are generally adequate for:

- overall dimensions;
- wheelbase;
- tyre/wheel;
- common ground-clearance values;
- a manufacturer-labelled turning value.

They are normally **not sufficient alone** for:

- actual road-wheel steering lock;
- AVT outer-face tyre track;
- wall-to-wall turning radius;
- detailed steering kinematics;
- exact front/rear overhang across most brands;
- lower underbody geometry;
- detailed ramp interference.

Therefore “source coverage” and “engineering readiness” must remain separate concepts.

## 6. Best next source family by missing parameter

| Missing information | Best next source family |
|---|---|
| Front/rear overhang, axle/datum geometry | OEM body-builder guide, body-repair manual, dimension/homologation drawing |
| Actual road-wheel lock / steering geometry | OEM workshop/alignment/steering manual; controlled measurement |
| Mounted tyre outer faces / AVT track | Explicit engineering drawing or physical measurement of exact fitment |
| OEM approach/departure/breakover | Exact OEM technical/off-road specification |
| Geometry-derived physical ramp angles | Static-loaded tyre/contact geometry + lower-envelope drawing/measurement |
| Longitudinal lower envelope / battery enclosure | body-repair/underbody documentation, CAD, homologation drawing, physical profile survey |
| Axle loads / loaded state | homologation/CoC, body-builder guide, certification plate, service data, weighing |
| Historical dimensions | archived OEM brochures/manuals and homologation material |

## 7. DLT/MOT role

Use DLT/MOT registration data to:

- discover makes/commercial model names in Thailand;
- support market-presence metadata;
- prioritize research by prevalence where model-level counts are available.

Do not use DLT model labels as generation/chassis/trim/wheel-package identity.

The research did not establish a continuous generation-resolved historical model inventory from DLT. Treat DLT as inventory/prioritization evidence, not an engineering geometry source.

## 8. Curation priority implication

The first data effort should prioritize:

1. models with high practical engineering use;
2. source ecosystems that teach us new semantics;
3. difficult technology such as rear steering and loaded-clearance EVs;
4. exact configurations that stress the schema.

Do not spend early effort maximizing manufacturer/model count.
