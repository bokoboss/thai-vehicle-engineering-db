# Thailand Vehicle Engineering Database

Engineering-grade vehicle geometry and maneuverability database for vehicles used in Thailand.

## Purpose

This project is intended to support:

- Autodesk Vehicle Tracking vehicle definitions and swept-path analysis
- parking, access, porte-cochère, loading and internal-road design
- ramp approach / departure / breakover assessment
- vehicle comparison and design-vehicle selection
- traceable engineering responses to clients

The project treats provenance and uncertainty as first-class data. Published facts, derived engineering values, estimates and unknowns must never be silently mixed.

## Current status

**Foundation / pre-implementation.**

The initial work is to define the product requirements, vehicle data standard, source hierarchy, QA rules, data architecture and pilot acceptance criteria before implementing the web application or populating the database at scale.

## Development workflow

This repository uses a lean adoption of the shared [Engineering Development Workflow](https://github.com/bokoboss/engineering-development-workflow).

ChatGPT acts as the control plane for research, data methodology, architecture, requirements, acceptance design and GitHub review. Codex is used only for bounded execution that requires local code/runtime/browser work.

## Working principle

> Unknown is a valid engineering value. Unsupported precision is not.

No vehicle parameter should be presented as verified unless its definition, source and applicability to the exact vehicle configuration are traceable.
