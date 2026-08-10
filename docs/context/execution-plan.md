# Execution Plan

## Purpose

This is the ordered implementation tracker for the project.

Unlike the other context files, this document is expected to change frequently once implementation begins.

## Status Legend

- `todo`
- `in_progress`
- `done`
- `blocked`

## Current Planning State

The repository has been scaffolded through the ingestion foundation and canonical training
pipeline. Training now has a reproducible script entrypoint; forecasting runtime integration,
aggregation persistence, simulation, dashboard, and end-to-end validation remain open.

## Phase 0: Context and Architecture Alignment

- [done] Preserve source PDFs under `docs/reference`.
- [done] Evaluate PRD features against research fit and project constraints.
- [done] Decide that the implementation must be Docker Compose-first.
- [done] Decide that at least one automated ingestion integration is required.
- [done] Select ERPNext as the preferred primary ingestion target for planning.
- [done] Create initial architecture and implementation context documents under `docs/context`.
- [done] Review and refine the context documents.
- [done] Freeze the agreed repository structure and ownership boundaries.

## Phase 1: Repository Scaffolding and Tooling

- [done] Scaffold the agreed top-level repository structure.
- [done] Create root `AGENTS.md`.
- [done] Set up Python 3.13 `uv` workspace for `apps/api`, `apps/worker`, and shared Python packages.
- [done] Add root `pyproject.toml` workspace configuration.
- [done] Set up `pre-commit`.
- [done] Configure `ruff`.
- [done] Configure `mypy`.
- [done] Initialize dashboard tooling with ESLint and Prettier.
- [done] Add basic CI workflow under `.github`.

## Phase 2: Training Pipeline Structure

- [done] Create `training/` structure with `src`, `configs`, `artifacts`, and `notebooks`.
- [done] Move any notebook-based research artifacts into `training/notebooks`.
- [done] Define and implement the script-based training pipeline shape.
- [done] Define the artifact metadata contract for inference-time loading.
- [done] Document how training outputs are versioned.

## Phase 3: Backend and Shared Foundations

- [done] Scaffold `apps/api`.
- [done] Scaffold `apps/worker`.
- [done] Scaffold `apps/dashboard`.
- [done] Scaffold `shared/domain`.
- [done] Scaffold `shared/schemas`.
- [done] Scaffold `shared/database`.
- [done] Scaffold `shared/ml`.
- [done] Scaffold `shared/integrations`.
- [done] Define base domain models for enterprise, ledger, forecast, and simulation concepts.
- [done] Define domain entities and class-based validation rules for enterprise, ingestion, financial, forecasting, and simulation concepts.
- [done] Define shared Pydantic schemas for enterprise and ingestion-source configuration.
- [done] Scaffold forecasting service modules under `apps/api/services/forecasting`.
- [done] Scaffold forecasting service modules under `apps/worker/services/forecasting`.
- [done] Set up shared SQLAlchemy base, database settings, engine creation, session factory, session manager, and database manager.
- [done] Define the agreed SQLAlchemy ORM models for enterprise, ingestion, financial, forecast, and simulation entities.
- [done] Complete API core settings, infrastructure lifecycle, logging, error handling, middleware, pagination, and application wiring.
- [done] Add the shared Redis Streams event-broker package and API infrastructure wiring.

## Phase 4: Infrastructure Foundations

- [done] Scaffold `infra/docker`.
- [done] Scaffold `infra/migrations`.
- [done] Scaffold `infra/seed`.
- [done] Create Docker Compose setup for API, worker, dashboard, PostgreSQL, Redis, and optional ERPNext demo services.
- [done] Define environment-variable strategy.
- [done] Document the agreed database schema in `docs/context/schema-overview.md`.
- [done] Set up migration tooling.
- [done] Wire Alembic to shared database metadata and database settings.

## Phase 5: Ingestion and Persistence

- [done] Implement enterprise and ingestion-source management basics through shared schemas, repositories, UoW, API services, and routes.
- [done] Implement ingestion-source credential management through DTOs, repositories, UoW, API services, and nested routes.
- [done] Add ingestion-source soft deletion with active filtering and Alembic migration.
- [done] Implement ERPNext ingestion workflow according to `docs/context/erpnext-ingestion-plan.md`.
- [done] Implement the source-key ingestion adapter registry in `shared/integrations`.
- [done] Add the adapter-neutral staged-file context and shared file validation helpers.
- [done] Implement and register CSV and Excel file adapters.
- [done] Wire API upload staging, upload-run creation, and Redis dispatch.
- [done] Wire worker staged-file resolution and terminal upload cleanup.
- [done] Define the CSV and Excel ingestion implementation plan in `docs/context/file-ingestion-plan.md`.
- [done] Implement CSV upload ingestion through the shared adapter, API, and worker workflow.
- [done] Implement XLSX upload ingestion through the shared adapter, API, and worker workflow.
- [done] Normalize all ingestion paths into a canonical accounting schema.
- [done] Persist normalized financial records through the shared transaction repository.
- [todo] Build monthly temporal aggregation logic.
- [todo] Build static financial metric persistence logic.

## Phase 6: Forecasting Core

- [todo] Implement model artifact loading.
- [todo] Implement scaler loading and validation.
- [todo] Implement temporal window reconstruction.
- [todo] Implement static feature vector assembly.
- [todo] Implement baseline forecast service.
- [todo] Persist forecast runs and metadata.

## Phase 7: Simulation Services

- [todo] Implement health delta simulation.
- [todo] Implement trapped liquidity simulation.
- [todo] Implement liquidity mitigation recommendation logic.
- [todo] Persist simulation checkpoints and outputs.
- [todo] Define solvency buffer configuration strategy.

## Phase 8: Dashboard

- [todo] Scaffold dashboard routes and shell.
- [todo] Integrate dashboard with backend APIs.
- [todo] Build baseline forecast view.
- [todo] Build health delta view.
- [todo] Build trapped liquidity ranking view.
- [todo] Build liquidity mitigation planning view.
- [todo] Add generated or shared API contracts for frontend use.

## Phase 9: Validation and Demo Packaging

- [todo] Add backend tests.
- [done] Add API/worker Compose services with a shared upload-volume mount.
- [todo] Add forecasting and simulation tests.
- [todo] Add dashboard tests where useful.
- [done] Add the optional ERPNext Compose demo stack.
- [todo] Add demo seed data.
- [todo] Add operator runbook and presentation notes.
- [todo] Validate the end-to-end ERPNext-to-dashboard demo flow.
