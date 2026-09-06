# Reproducibility and Deployment

## Reference environment

Docker Compose is the primary execution model. The default stack runs:

- API at `http://localhost:8000`
- Dashboard at `http://localhost:5173`
- PostgreSQL on host port `5435`
- Redis on host port `6381`
- background ingestion worker
- one-shot migration and platform-seed services

The optional `erpnext` profile adds ERPNext at `http://localhost:8090`, MariaDB,
ERPNext cache/queue Redis instances, backend and websocket processes, and an automated
ERPNext bootstrap and sync.

## Setup

Install the Python workspace and dashboard dependencies:

```powershell
uv sync
npm --prefix apps/dashboard install
```

Start and seed the core platform:

```powershell
docker compose up -d --build
```

Start the complete platform with the ERPNext demonstration:

```powershell
docker compose --profile erpnext up -d --build
```

Compose waits for PostgreSQL and Redis health, applies Alembic migrations, starts the
API and worker, and loads the platform fixture. The ERPNext profile additionally
creates the ERPNext site, configures the demo company, loads accounting records,
rotates a dedicated API token into the platform, and requests an initial full sync.
Each migration and seed service declares the bootstrap build definition directly.
Compose therefore creates project-local images on a fresh clone instead of depending
on a pre-existing image tag or attempting to pull a private registry image. The
services still reuse the same Docker build layers.

## Deterministic demonstration data

The platform seed uses one JSON source of truth and two stages:

1. `seed_api.py` creates or reuses the enterprise, ingestion sources, and ERPNext
   credential through public API paths.
2. `seed_database.py` loads the related ledger, snapshots, forecasts, receivables, and
   simulations through shared database models.

Both stages are idempotent. Monetary values remain decimal strings in JSON and stable
identifiers make reruns repeatable. The fixture uses February through July 2026 as the
six-month model history and August 2026 as the forecast target.

The fixture is INR-denominated and calibrated through artifact version 3's fixed
model-reference currency mapping. Stored forecast and simulation results are model
evaluations, not hand-authored UI values. Seed integrity routines recompute aggregate
and receivable values and rerun baseline and simulation calculations.

## Training reproduction

The six input CSV files, baseline YAML configuration, source code, artifact metadata,
metrics, scalers, and weights are present in the repository. Run the configured
experiment with:

```powershell
uv run --package cash-flow-training train-model `
  --config training/configs/baseline.yaml --no-gpu
```

The run name is also the artifact directory name; use a new name before conducting a
new experiment to avoid replacing the evidence for the committed baseline. See
[training-and-evaluation.md](./training-and-evaluation.md) for the split, metrics, and
limitations.

## Validation commands

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest
npm --prefix apps/dashboard run lint
npm --prefix apps/dashboard run typecheck
npm --prefix apps/dashboard run build
pre-commit run --all-files
```

The focused Python tests cover feature normalization and preparation, currency-aware
hybrid inference and out-of-distribution fallback, and counterfactual consistency.
The CI workflow installs Python and Node dependencies and runs repository pre-commit
checks. Docker health checks cover service readiness; the seed process supplies
end-to-end demonstration coverage.

## Reproducibility properties

- Python dependencies are locked in `uv.lock`; dashboard dependencies are locked in
  `package-lock.json`.
- Database evolution is fully represented by ordered Alembic revisions.
- FastAPI produces the OpenAPI source used to generate dashboard TypeScript contracts.
- Model metadata records architecture, features, scaling, blend, support, and currency
  assumptions.
- Forecast runs record artifact versions and exact aggregate input links.
- Simulation runs persist their patches and derived outputs.
- Container configuration is supplied through environment variables and explicit
  Compose service dependencies.

## Deployment and security limits

The containers are portable to comparable container infrastructure, and PostgreSQL or
Redis can be replaced by compatible managed services. The reference environment is
nevertheless development-oriented: it uses fixed local credentials, exposes service
ports, has no authentication gateway, and stores ingestion secrets directly in the
application database. Production deployment would require secret management,
authentication and authorization, TLS, backup and retention policy, monitoring,
resource limits, and recovery procedures.

Reproducibility here means the research model, application workflow, schema, and demo
state can be reconstructed consistently. It does not imply production readiness or
external validity beyond the documented experiment.
