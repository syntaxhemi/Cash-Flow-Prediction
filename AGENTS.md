# AGENTS

## Purpose

This file defines the working contract for agents and contributors operating in this repository.

Use this document together with:

- `docs/context/system-overview.md`
- `docs/context/architecture.md`
- `docs/context/data-and-ingestion.md`
- `docs/context/forecasting-and-simulation.md`
- `docs/context/training-and-evaluation.md`
- `docs/context/dashboard.md`
- `docs/context/reproducibility.md`

If there is a conflict between ad hoc assumptions and the context documents, follow the context documents.

## Project Positioning

This repository is a final-year engineering project that develops a cash flow
forecasting model and demonstrates the model through an enterprise-style prediction
and decision-support platform.

Important scope rules:

- build greenfield
- do not reuse `~legacy` code as the base of the new platform
- optimize for technical clarity and reproducibility
- do not overengineer for production scale
- keep the system Docker Compose-first

## Source of Truth

### Primary references

- `docs/reference/research-paper.pdf`
- `docs/reference/prd.pdf`

### Maintained project documentation

- everything under `docs/context`

### Legacy reference

- `~legacy` is reference-only
- do not migrate or extend it as the new platform base

## Repository Structure

Expected top-level layout:

```text
/apps
  /api
  /worker
  /dashboard
/training
  /src
  /configs
  /artifacts
  /notebooks
/shared
  /domain
  /schemas
  /database
  /ml
  /integrations
  /event_broker
/infra
  /docker
  /migrations
  /seed
/docs
  /context
  /reference
/.github
AGENTS.md
.pre-commit-config.yaml
pyproject.toml
uv.lock
docker-compose.yml
README.md
```

## Ownership Boundaries

### `apps/api`

Owns:

- FastAPI entrypoints
- HTTP route definitions
- request handling
- app-layer forecasting orchestration
- app-layer simulation orchestration
- admin-facing APIs

Should not own:

- shared persistence implementation that belongs in `shared/database`
- low-level model loading and inference primitives that belong in `shared/ml`
- ERP/file adapter code that belongs in `shared/integrations`

Internal scaffold direction:

- use `main.py` as the entrypoint
- keep a layered structure with `core`, `dependencies`, `routes`, and `services`
- keep forecasting and simulation orchestration under `services/forecasting`
- do not introduce a separate controller layer

### `apps/worker`

Owns:

- async job execution
- background synchronization tasks
- scheduled forecasting workflows
- batch simulation or recomputation workflows

Should not own:

- duplicate shared business logic already expressed elsewhere

Internal scaffold direction:

- use `main.py` as the entrypoint
- keep a minimal layered structure with `core`, `jobs`, and `services`
- keep forecasting-related background orchestration under `services/forecasting`
- do not add worker-specific packages unless a concrete need appears

### `apps/dashboard`

Owns:

- React + Vite frontend
- executive UI
- API consumption
- presentation logic

Should not own:

- backend business logic
- duplicated handwritten API contracts where shared or generated contracts are available

Internal scaffold direction:

- keep the top-level structure aligned with standard Vite output
- keep only light organization under `src`
- keep `ESLint` and `Prettier` configuration inside `apps/dashboard`

### `training`

Owns:

- script-based training and preprocessing logic
- reproducible training entrypoints
- training configs
- artifact metadata and outputs

Notes:

- notebooks are exploratory
- scripts are canonical
- `training` depends on `cash-flow-ml` and the training libraries it needs

### `shared/domain`

Owns:

- business entities
- core financial concepts
- domain rules independent of framework and storage tooling

Should not own:

- Alembic
- FastAPI routing
- app orchestration
- ORM migration logic

### `shared/schemas`

Owns:

- Python DTOs
- internal contracts
- API payload models

### `shared/database`

Owns:

- ORM models
- repositories
- session helpers
- shared persistence utilities

### `shared/ml`

Owns:

- model loading
- scaler and artifact loading
- tensor preparation support
- low-level inference support

### `shared/integrations`

Owns:

- ERP/accounting adapters
- file-ingestion adapters
- integration clients and payload translation

### `shared/event_broker`

Owns:

- Redis Streams client lifecycle
- event-broker interfaces
- publish, consumer-group, read, acknowledgement, and deletion operations

Should not own:

- domain events or business rules
- financial records or workflow state
- API routes or worker job orchestration

## Architecture Rules

- prefer a modular monolith over microservice sprawl
- keep runtime architecture compact
- use Docker Compose as the primary execution model
- use PostgreSQL as the system of record
- use Redis as a lightweight runtime dependency for async or coordination needs
- use the shared Redis Streams event broker for durable API-worker job transport
- keep one strong automated ingestion path rather than many weak ones
- treat simulation as decision support, not autonomous financial control

## Workflow Rules

### Forecasting and simulation placement

Forecasting and simulation are application/business workflows.

They should not become top-level shared packages.

Recommended placement:

- `apps/api/services/forecasting`
- `apps/worker/services/forecasting`

These workflows should compose:

- `shared/domain`
- `shared/schemas`
- `shared/database`
- `shared/ml`
- `shared/integrations`

### Ingestion strategy

Use one canonical internal accounting shape downstream of all ingestion paths.

Current direction:

- primary automated integration: ERPNext
- fallback ingestion: CSV and Excel

Do not let external source formats leak into downstream forecasting logic.

## Database Rules

- business meaning belongs in `shared/domain`
- persistence implementation belongs in `shared/database`
- schema evolution belongs in `infra/migrations`
- both `api` and `worker` may use the shared persistence layer

Do not collapse these concerns into one folder.

## Tooling Standards

### Python

- Python version: `3.13`
- package manager and workspace: `uv`
- linting and formatting: `ruff`
- type checking: `mypy`
- task runner: `poethepoet`

### Frontend

- framework: `React + Vite`
- linting: `ESLint`
- formatting: `Prettier`

### Repository-wide

- hooks: `pre-commit`

## Documentation Rules

- keep current architecture, behavior, and research evidence in `docs/context`
- describe implemented behavior rather than maintaining planning documents or task
  trackers in `docs/context`
- keep source PDFs in `docs/reference`
- when architecture, model behavior, evaluation evidence, or a major workflow changes,
  update the relevant context documents in the same change

## Implementation Rules

- prefer script-based training code over notebook-only logic
- avoid hidden one-off local workflows
- keep code and configuration reproducible
- do not build features solely for hypothetical production scale
- when in doubt, choose the simpler design that still demonstrates the architecture cleanly
- add Google-style docstrings to every newly added public function and method
- document relevant `Args`, `Returns`, `Raises`, and `Notes` sections in public API docstrings
- keep docstrings accurate when changing a function or method's behavior or contract

## Agent Behavior

Before major implementation work:

1. read the relevant files in `docs/context`
2. verify where the change belongs
3. avoid creating new structural patterns unless necessary

When making structural changes:

1. update the relevant context documents
2. keep naming consistent with existing conventions
3. preserve the agreed ownership boundaries

When uncertain:

- prefer asking whether the change affects architecture or only implementation detail
- do not silently move responsibilities across `shared/domain`, `shared/database`, `shared/ml`, `shared/integrations`, `apps/api`, `apps/worker`, and `infra/migrations`
