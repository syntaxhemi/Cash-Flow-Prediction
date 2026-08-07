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

The repository has not yet been scaffolded.

This execution plan is the proposed delivery sequence to review before implementation starts.

## Phase 0: Context and Architecture Alignment

- [done] Preserve source PDFs under `docs/reference`.
- [done] Evaluate PRD features against research fit and project constraints.
- [done] Decide that the implementation must be Docker Compose-first.
- [done] Decide that at least one automated ingestion integration is required.
- [done] Select ERPNext as the preferred primary ingestion target for planning.
- [done] Create initial architecture and implementation context documents under `docs/context`.
- [todo] Review and refine the context documents.
- [todo] Freeze the agreed repository structure and ownership boundaries.

## Phase 1: Repository Scaffolding and Tooling

- [todo] Scaffold the agreed top-level repository structure.
- [todo] Create root `AGENTS.md`.
- [todo] Set up Python 3.13 `uv` workspace for `apps/api`, `apps/worker`, and shared Python packages.
- [todo] Add root `pyproject.toml` workspace configuration.
- [todo] Set up `pre-commit`.
- [todo] Configure `ruff`.
- [todo] Configure `mypy`.
- [todo] Initialize dashboard tooling with ESLint and Prettier.
- [todo] Add basic CI workflow under `.github`.

## Phase 2: Training Pipeline Structure

- [todo] Create `training/` structure with `src`, `configs`, `artifacts`, and `notebooks`.
- [todo] Move any notebook-based research artifacts into `training/notebooks`.
- [todo] Define the script-based training pipeline shape.
- [todo] Define artifact metadata contract for inference-time loading.
- [todo] Document how training outputs are versioned.

## Phase 3: Backend and Shared Foundations

- [todo] Scaffold `apps/api`.
- [todo] Scaffold `apps/worker`.
- [todo] Scaffold `apps/dashboard`.
- [todo] Scaffold `shared/domain`.
- [todo] Scaffold `shared/schemas`.
- [todo] Scaffold `shared/database`.
- [todo] Scaffold `shared/ml`.
- [todo] Scaffold `shared/integrations`.
- [todo] Define base domain models for enterprise, ledger, forecast, and simulation concepts.
- [todo] Define shared Pydantic schemas for ingestion, forecasting, and simulation workflows.
- [todo] Scaffold forecasting service modules under `apps/api/services/forecasting`.
- [todo] Scaffold forecasting service modules under `apps/worker/services/forecasting`.

## Phase 4: Infrastructure Foundations

- [todo] Scaffold `infra/docker`.
- [todo] Scaffold `infra/migrations`.
- [todo] Scaffold `infra/seed`.
- [todo] Create Docker Compose setup for API, worker, dashboard, PostgreSQL, Redis, and optional ERPNext demo services.
- [todo] Define environment-variable strategy.
- [todo] Draft the initial database schema.
- [todo] Set up migration tooling.

## Phase 5: Ingestion and Persistence

- [todo] Implement enterprise and ingestion-source management basics.
- [todo] Implement ERPNext ingestion adapter.
- [todo] Implement CSV upload ingestion.
- [todo] Implement Excel upload ingestion.
- [todo] Normalize all ingestion paths into a canonical accounting schema.
- [todo] Persist normalized financial records.
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
- [todo] Add forecasting and simulation tests.
- [todo] Add dashboard tests where useful.
- [todo] Add Compose smoke test flow.
- [todo] Add demo seed data.
- [todo] Add operator runbook and presentation notes.
- [todo] Validate the end-to-end ERPNext-to-dashboard demo flow.
