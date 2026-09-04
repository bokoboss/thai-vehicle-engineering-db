# Agent Instructions

This repository contains engineering software **and engineering data**. Data integrity is a protected product behavior.

## Before changing anything

1. Read `AGENTS.md`.
2. Read `PROJECT_PROFILE.md`.
3. Read the current GitHub Issue / execution contract and referenced PR.
4. Read the relevant documents under `docs/`, especially `docs/VEHICLE_DATA_STANDARD.md`.
5. Inspect `git status`.
6. Record the current branch and exact `HEAD`.
7. Inspect recent commits and relevant refs (`main`, the task branch, and remote-tracking refs).
8. Confirm the expected branch, base and PR from the execution packet before editing.
9. Treat repository files, Git history, GitHub Issues/PRs and accepted release artifacts as authoritative over remembered chat context.

If the execution packet conflicts with actual repository/Git/GitHub state, stop and report the conflict instead of silently guessing or repairing around it.

Do not assume access to any previous ChatGPT or Codex conversation, account, session or scratchpad. A task must be reconstructable from the repository, Git/GitHub state and the current execution packet.

For material schema, engineering-methodology or AVT-mapping changes, apply scrutiny before implementation.

## Control plane and execution plane

Use the workflow boundary below unless a task-specific contract explicitly overrides it:

- **ChatGPT = control plane:** reasoning, source research, architecture/methodology, scope, acceptance criteria, independent review, GitHub/PR/CI inspection and preparation of execution packets.
- **Codex = execution plane:** bounded local repository/file/code/data mutation, local runtime or browser execution, tests, packaging and implementation work.

Codex tasks must be self-contained. They must state the repository, expected branch/base, baseline `HEAD`, bounded scope, acceptance criteria, required tests and stop conditions, and must not depend on prior Codex chat history.

Preserve recoverable Git baselines. Do not use destructive Git/file operations or overwrite accepted data/release artifacts unless the execution contract explicitly authorizes them.

## Non-negotiable data rules
- Never fabricate a vehicle dimension or parameter.
- Never turn an unknown value into a numeric estimate without explicitly classifying it as estimated and preserving the method.
- Never reinterpret an OEM label such as “turning radius” as curb-to-curb or wall-to-wall unless the source defines it or another authoritative source establishes the definition.
- Never assume vehicles with the same commercial model name share geometry across generations, markets, drivetrains, body styles or variants.
- Preserve raw source wording, original value/unit and provenance.
- Keep published, measured, derived and estimated values distinguishable.
- Conflicting evidence must be retained and surfaced; do not silently choose one value.
- Do not compute a “verified” approach, departure or breakover angle from global minimum ground clearance unless the required contact/clearance geometry is actually known.
- Do not infer maximum road-wheel angle from steering-wheel lock-to-lock alone.
- Autodesk Vehicle Tracking wheel-track semantics must not be populated directly from OEM tread/track-center values without an explicit mapping/derivation.

## Source policy
Prefer, in order appropriate to the parameter:
- Thai regulatory / official data where applicable;
- Thai OEM technical/specification material for the exact configuration;
- OEM regional/global technical material verified to match the same geometry;
- OEM service/body-repair/homologation material;
- reputable secondary technical sources only when primary evidence is unavailable;
- documented measurement or estimation with explicit method and limitations.

Source authority, exact vehicle applicability and evidence method are separate metadata.

## Engineering calculations
Every calculation intended for publication must have:
- formula/version identifier;
- required inputs and units;
- validity conditions;
- uncertainty/limitations;
- deterministic tests;
- provenance back to input observations.

## Completion
Implementation exists != accepted.

Report:
- repository and exact branch;
- baseline `HEAD` and final `HEAD`;
- changed files/contracts/behavior;
- tests and evidence;
- PR and CI state where applicable;
- unresolved data/methodology questions or blockers;
- any values or records that remain partial or unverified.

This project uses a lean adoption of:
https://github.com/bokoboss/engineering-development-workflow
