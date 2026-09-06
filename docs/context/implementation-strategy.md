# Implementation Strategy

## Purpose

This document is the stable architectural reference for the platform build. It explains:

- the intended system shape
- the implementation priorities
- the main constraints and tradeoffs
- corrections and interpretations applied to the PRD

This file should change less often than the execution tracker.

## Delivery Positioning

This project should demonstrate enterprise-style financial forecasting workflows without pretending to be a production treasury platform.

The correct target is:

- greenfield platform build
- Docker Compose-first delivery
- strong architectural clarity
- one credible automated ingestion integration
- reproducible local demonstration

## High-Level Architecture

The platform should be built as a compact modular monorepo with a small number of deployable services.

### Runtime Components

1. `api`
   - FastAPI application
   - owns ingestion endpoints, forecasting endpoints, simulation endpoints, admin APIs, and dashboard-facing APIs

2. `worker`
   - executes asynchronous or scheduled jobs
   - owns synchronization, derived data refresh, background simulation tasks, and future scheduled forecasting workflows

3. `dashboard`
   - React + Vite frontend
   - provides executive visibility and planning interfaces

4. `platform dependencies`
   - PostgreSQL
   - Redis
   - optional ERPNext demo container or external ERPNext instance for ingestion demonstration

### Deployment Model

Primary delivery format:

- Docker Compose
- environment-variable-based configuration
- all core value demonstrable locally

This project should not depend on cloud-only infrastructure to prove its architecture.

### Redis Streams Event Broker

Redis is used as a lightweight transport between the API and worker for durable
application jobs. The shared `event_broker` package owns Redis Streams client lifecycle,
publishing, consumer-group creation, reads, acknowledgements, and message deletion.

The broker transports compact commands such as an ingestion run identifier. PostgreSQL
remains the source of truth for run state and financial data. The package must not become
a generic domain-event framework or carry financial records in stream messages.

Important clarification:

- PostgreSQL and Redis are not separate repository apps
- they are infrastructure dependencies managed through Docker Compose
- only `api`, `worker`, and `dashboard` are application modules we scaffold inside this repository

## Canonical Platform Workflow

1. Enterprise financial data is ingested from ERPNext or imported from CSV/Excel.
2. The API validates and normalizes incoming records.
3. Normalized records are persisted in PostgreSQL as the system of record.
4. Derived temporal windows and static feature vectors are constructed from stored data.
5. Application services produce a baseline next-interval cash flow prediction.
6. Application services generate counterfactual runs for:
   - health delta
   - trapped liquidity
   - solvency recovery planning
7. The dashboard presents forecast outcomes, recommendations, and historical context.

## Service Responsibility Strategy

### API

Use a layered FastAPI structure:

- `main.py` as entrypoint
- `core/` for runtime concerns
- `dependencies/` for dependency providers
- `routes/` for HTTP entrypoints
- `services/` for orchestration

Do not split `routes` and `controllers`.

Forecasting and simulation orchestration should live under app services, for example:

- `apps/api/src/api/services/forecasting`
- `apps/worker/src/worker/services/forecasting`

### Worker

Use a minimal layered structure:

- `main.py` as entrypoint
- `core/` for config, errors, and logging
- `jobs/` for async or scheduled tasks
- `services/` for orchestration used by jobs

Do not create worker-specific abstractions without a clear concrete need.

### Dashboard

Keep the frontend top-level structure close to a standard Vite app.

## Persistence Strategy

Recommended split:

- `shared/domain`: business concepts and rules
- `shared/database`: ORM models, repositories, session helpers, shared persistence utilities
- `infra/migrations`: schema evolution

The database is the operational source of truth for:

- enterprise entities
- ingestion records
- temporal transaction aggregates
- static financial metrics
- forecast runs
- simulation checkpoints

Shared packages should stop at reusable capability boundaries such as:

- domain models
- schemas
- persistence
- ML/runtime inference support
- integration adapters

Baseline forecasting and counterfactual simulations are business workflows built from those capabilities and therefore belong in the application layer.

## Data Model Direction

At a minimum, the platform should persist:

- enterprise profile and registration metadata
- ingestion source definitions and connection metadata
- raw or normalized ledger/financial records
- monthly temporal aggregates used for forecasting
- static financial health metrics
- forecast outputs
- simulation runs and checkpoints

## Ingestion Strategy

### Primary automated integration

The first automated integration should target ERPNext.

Reason:

- open source and practical for local Compose-based demos
- credible enterprise accounting workflow
- avoids dependence on paid API access

### Fallback import paths

The platform should also support:

- CSV uploads
- Excel uploads

These are fallback and compatibility paths, not the main product story.

### Integration boundary

All ingestion paths should converge into one internal normalized accounting schema before downstream forecasting logic runs.

## Forecasting and Simulation Strategy

### Baseline forecasting

The baseline path should:

- reconstruct the required temporal sequence window
- load associated static features
- apply scaler and artifact metadata
- return next-interval net cash flow prediction

The selected runtime artifact uses a calibrated hybrid prediction:

- 67.5 percent from the research-aligned temporal/static LSTM
- 32.5 percent from the mean observed net cash flow across the six input months

The persistence component is an explicit stability path for enterprise inputs whose
cash scale differs from the research dataset. Its weight and strategy are stored in
artifact metadata and evaluated by the training pipeline, so training and runtime use
the same forecast calculation. Research credit and failure scores must be normalized
to the platform's canonical 0-to-1 scale before fitting the static scaler.

Artifacts also record an input z-score limit above the observed validation envelope.
When runtime inputs exceed that limit, inference uses the persistence path alone rather
than extrapolating the LSTM across an unsupported enterprise cash scale.

The NayaOne SME UK dataset is treated as GBP-denominated by explicit project
assumption because its published Kaggle description identifies UK economic coverage
but does not declare a currency field. The artifact records GBP as its training
currency and a fixed 2020 model-reference conversion of 1 GBP = 100 INR. For INR
enterprises, only monetary temporal and static features are converted to GBP before
scaling and inference; the predicted target is converted back to INR before API
persistence. Non-monetary delays, scores, ratios, and counts remain unchanged. This
fixed historical conversion is part of the reproducible model contract and must not be
presented as a current FX quote.

### Health delta simulation

This path should:

- freeze temporal inputs
- sweep selected static variables within bounded ranges
- compare simulated outputs against the baseline

### Trapped liquidity simulation

This path should:

- clone the temporal sequence
- adjust payment-delay-related inputs
- estimate forecast change attributable to late payments

Payment-delay scenarios should also reduce the affected period's inflow by a bounded
share of the counterparty's outstanding invoice amount. The share is proportional to
the delay within a 30-day forecast interval and cannot exceed recorded inflows. This
keeps the counterfactual connected to cash realization rather than relying on a weak
payment-delay embedding alone.

### Liquidity mitigation planning

This path should:

- trigger when forecasted liquidity breaches a buffer
- permute bounded discretionary outflow changes
- return ranked recommended actions

Initial action mappings should remain distinct:

- `delay_capex` changes the static `capex` input and the bounded monthly outflow
  represented by that annual amount.
- `reduce_outflows` changes the temporal `total_outflows` input by a bounded amount.
- `adjust_repayment` changes both temporal `monthly_repayment` and its corresponding
  `total_outflows` amount.

Counterfactual runs must use the same model and artifact version as their persisted
baseline forecast. A new baseline is required after an artifact upgrade.

This should be described as recommendation logic, not autonomous optimization.

## Training and Artifact Strategy

Training should live under `training/` and become script-driven.

Recommended principles:

- notebooks are exploratory
- scripts are canonical
- artifact metadata must be explicit
- inference-time assumptions should be loaded from artifact metadata, not embedded implicitly in API code

## Tooling Strategy

### Python

- Python 3.13
- `uv` for workspace and dependency management
- `ruff` for formatting and linting
- `mypy` for type checking

### Frontend

- React + Vite
- ESLint
- Prettier

### Repository-wide

- `pre-commit`

## Scope-Conscious Principles

### Prefer one strong workflow over many weak ones

Focus on:

- one end-to-end ingestion path
- one forecasting path
- a small number of strong simulations
- one cohesive dashboard

### Keep the runtime compact

Prefer a modular monolith with a small number of services over many fine-grained services.

### Preserve explainability

Platform behavior must be easy to explain in an academic review:

- where data comes from
- how features are derived
- how the model is invoked
- how recommendations are generated

## Recommended MVP

The strongest MVP for this project is:

- ERPNext ingestion
- CSV/Excel fallback ingestion
- PostgreSQL-backed financial record persistence
- baseline forecast API
- health delta simulation API
- trapped liquidity simulation API
- solvency mitigation recommendation API
- executive dashboard

## Immediate Strategic Priorities

1. finalize context documents
2. finalize repository structure
3. scaffold the agreed modules
4. establish Python workspace and tooling
5. implement ingestion and persistence foundations
6. implement baseline forecasting before simulation breadth
