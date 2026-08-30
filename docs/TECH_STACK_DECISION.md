# Technology Stack Decision — Phase 0 / MVP

Status: Accepted control-plane decision for implementation  
Date: 2026-08-30

## Decision

Use a **Python-first monolithic web application** with server-rendered HTML.

### Application
- Python
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic 2.x
- Jinja2 templates
- HTMX only where small dynamic interactions materially improve usability
- small project-owned CSS; no SPA framework required

### Persistence
- SQLite for local development/test/single-instance pilot
- PostgreSQL-compatible SQLAlchemy models for shared deployment

### Data export
- Python standard CSV
- openpyxl for XLSX

### Tests
- pytest
- FastAPI/HTTP test client
- deterministic database fixtures
- schema/migration tests
- browser/E2E only when UI behaviour requires it

## Why this stack

The product is a data-heavy engineering reference tool with a deliberately thin UI.

The stack should optimize for:
- data validation and engineering logic;
- transparent relational modelling;
- fast development;
- easy CSV/XLSX generation;
- low operational complexity;
- no mandatory Node/React toolchain;
- portability from SQLite to PostgreSQL;
- straightforward automated testing.

A React/Next.js SPA, microservices, message queues, GraphQL, event streaming and other platform infrastructure are explicitly unnecessary for the current product.

## Application shape

```text
FastAPI application
├─ domain / validation
├─ SQLAlchemy repositories
├─ service layer
├─ Jinja2 pages
├─ small JSON endpoints where useful
├─ CSV/XLSX export
└─ SQLite / PostgreSQL
```

## UI principle

Prefer normal web pages first.

HTMX may be used for:
- incremental search;
- compare selection;
- evidence expansion;
- filtered issue lists.

Do not use HTMX merely to make static pages dynamic.

## Deployment implications

The application must remain a single deployable service.

A shared deployment later requires:
- hosted Python web service;
- PostgreSQL;
- source snapshot/object storage only if needed;
- backups.

Deployment-provider selection is intentionally deferred; the application must not depend on provider-specific runtime APIs.

## Alternatives considered

### Next.js / React + ORM
Rejected for Phase 0 because it adds a separate JavaScript application/toolchain without solving the hard part of this project, which is evidence semantics and data curation.

### Django
Viable, particularly for built-in admin, but FastAPI + SQLAlchemy/Pydantic gives a smaller explicit domain/API surface for this bounded application. A custom curation UI can remain minimal.

### Streamlit
Rejected. The project is a persistent searchable engineering database and should behave like a normal web application rather than an analytical notebook UI.

### Separate frontend + backend services
Rejected as unnecessary complexity.

## Revisit triggers

Reconsider the stack only if one of these becomes real:
- complex collaborative editing;
- substantial interactive geometry editing;
- offline-first client application;
- very high concurrency;
- large-scale public API requirements;
- provider/runtime limitation that cannot be solved cleanly.

None is currently required.

## Implementation constraint

Codex should implement this decision rather than reopen framework selection unless a concrete blocker is demonstrated.
