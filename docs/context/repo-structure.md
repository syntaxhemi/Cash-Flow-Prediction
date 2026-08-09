# Repository Structure

## Purpose

This document records the intended repository layout before scaffolding begins.

## Proposed Top-Level Structure

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

## Rationale

### `apps`

This directory contains runnable applications:

- `api`: FastAPI backend
- `worker`: async orchestration and scheduled processing
- `dashboard`: React + Vite frontend

These are the runtime components most likely to map directly to Docker Compose services.

### `training`

This directory contains the reproducible model training and artifact-generation pipeline.

Suggested meaning:

- `src`: canonical training and preprocessing code
- `configs`: experiment and pipeline configuration
- `artifacts`: tracked model outputs and metadata
- `notebooks`: exploratory work only

### `shared`

This directory contains reusable Python code shared across `api`, `worker`, and training where appropriate.

Suggested responsibilities:

- `domain`: business entities and core financial concepts
- `schemas`: API payloads and internal DTOs
- `database`: ORM models, repositories, and shared persistence utilities
- `ml`: model loading, tensor preparation, and inference support
- `integrations`: ERP/accounting and file-ingestion adapters
- `event_broker`: shared Redis Streams transport and lifecycle manager for API-worker jobs

Forecasting and simulation should not be top-level shared packages.

Reason:

- they are application/business workflows
- they compose `domain`, `schemas`, `database`, `ml`, and `integrations`
- they belong in app-layer services rather than in a shared capability package

### `infra`

This directory contains infrastructure support for local reproducibility:

- Docker support files
- migration tooling
- seed and demo fixtures

### `docs`

This directory contains:

- `reference`: source PDFs and primary research inputs
- `context`: architecture and implementation guidance

## Recommended Internal Application Layout

### `apps/api`

```text
/apps/api
  /src
    /api
      __init__.py
      main.py
      /core
        /config
        /errors
        /logging
        /middleware
      /dependencies
      /routes
      /services
        /forecasting
  /tests
  pyproject.toml
```

### `apps/worker`

```text
/apps/worker
  /src
    /worker
      __init__.py
      main.py
      /core
        /config
        /errors
        /logging
      /jobs
      /services
        /forecasting
  /tests
  pyproject.toml
```

### `apps/dashboard`

```text
/apps/dashboard
  /public
  /src
    /assets
    /components
    /pages
    /layouts
    /routes
    /services
    /hooks
    /lib
    /styles
    main.jsx|tsx
    App.jsx|tsx
  index.html
  package.json
  vite.config.js|ts
  eslint.config.js|ts
  .prettierrc
```

## Database Ownership Strategy

Recommended split:

- `shared/domain`: business meaning and financial concepts
- `shared/database`: persistence implementation
- `infra/migrations`: schema evolution

This keeps platform meaning separate from ORM and migration concerns while still allowing both `api` and `worker` to share one persistence layer.

## Schema Strategy

Python services should share:

- `shared/domain`
- `shared/schemas`
- `shared/database`
- `shared/ml`
- `shared/integrations`
- `shared/event_broker`

For the dashboard:

- define API contracts in FastAPI/Pydantic
- expose OpenAPI
- generate TypeScript types or client code when useful

## Deliberate Constraints

This structure is modular, but not microservice-heavy.

The goals are:

- clean boundaries
- low operational overhead
- clear academic explainability
- easy Compose-first deployment
