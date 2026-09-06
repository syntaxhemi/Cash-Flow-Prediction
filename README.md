# Cash Flow Prediction Platform

## Overview

This repository contains an enterprise-style cash flow prediction platform built around an applied research forecasting model.

The platform is being built with:

- FastAPI backend
- Python worker
- React + Vite dashboard
- PostgreSQL
- Redis
- Docker Compose

## Repository Structure

```text
apps/
  api/
  worker/
  dashboard/
training/
shared/
infra/
docs/
```

Key references:

- `docs/context/`
- `docs/reference/`

## Tooling

- Python `3.13`
- `uv` workspace
- `ruff`
- `mypy`
- `pre-commit`
- `ESLint`
- `Prettier`

## Local Setup

### Python workspace

```bash
uv sync
```

### Dashboard

```bash
npm --prefix apps/dashboard install
```

### Infrastructure

```bash
docker compose up -d --build
```

This starts and seeds the complete local application stack:

- API at `http://localhost:8000`
- Dashboard at `http://localhost:5173`
- PostgreSQL
- Redis
- Worker

The API and worker share a Docker volume for staged file uploads. Compose waits for
PostgreSQL and Redis health checks before starting the application services. One-shot
seed services then create the API-owned resources and load the deterministic database
fixture, including historical transactions, forecasts, snapshots, receivables, and
simulations.

The local images use CPU-only PyTorch. The worker excludes the unused ML runtime, and
the API and worker Dockerfiles cache third-party dependencies independently from
application source changes to keep images and rebuilds substantially smaller.

The local ERPNext demo is optional because it adds several services and can take a
few minutes to initialize. Start it with:

```bash
docker compose --profile erpnext up -d --build
```

ERPNext will be available at `http://localhost:8090` with username `Administrator`
and password `admin`. After the general demo seed completes, the one-shot
`erpnext-seed` service completes company setup, loads deterministic August/September
2026 accounting data, rotates the existing ERPNext credential with a dedicated API
token, and requests an initial full sync. No manual ERPNext wizard or credential setup
is required. Follow its progress with:

```bash
docker compose logs -f platform-seed erpnext-seed
```

## Quality Checks

Run repository hooks:

```bash
pre-commit run --all-files
```

Run repository linting:

```bash
uv run ruff check .
```

Run repository formatting:

```bash
uv run ruff format .
```

## Status

The repository is currently scaffolded and ready for implementation work. The next phase is building platform logic on top of the established structure.
