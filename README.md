# Cash Flow Prediction Platform

An enterprise-style applied machine-learning platform that ingests accounting data,
forecasts next-period net cash flow, and supports bounded financial scenario analysis.

The project develops a hybrid cash-flow forecasting model and embeds it in a
reproducible end-to-end system: dataset preparation and training, ERPNext and file
ingestion, canonical financial records, asynchronous aggregation, artifact-controlled
inference, persisted counterfactuals, and an executive React dashboard.

## Capabilities

- ERPNext, CSV, and XLSX accounting-data ingestion
- Redis Streams API-to-worker processing
- PostgreSQL transaction, aggregate, forecast, and simulation history
- Six-month temporal and static-feature cash-flow forecasting
- Financial-health, trapped-liquidity, and mitigation simulations
- Responsive overview, forecast, health, receivables, planning, and data views
- Deterministic local demonstration and optional automated ERPNext environment

## Architecture

```text
ERPNext / files -> FastAPI -> Redis Streams -> worker
                       |                       |
                       +------ PostgreSQL <----+
                                  ^
                                  |
                           React dashboard

Model artifacts -> API forecast and simulation services
```

The repository is a modular monolith with independently runnable API, worker, and
dashboard applications. Shared packages own domain rules, schemas, persistence, ML,
integrations, and event-broker primitives.

## Documentation

The maintained project documentation is in [docs/context](./docs/context/README.md).
It covers the implemented system, architecture, data pipeline, forecasting and
simulation behavior, training evidence, dashboard, and reproducibility. The source
research paper and original product requirements are preserved in `docs/reference`.

## Local setup

Requirements are Python 3.13, uv, Node.js, npm, Docker, and Docker Compose.

```powershell
uv sync
npm --prefix apps/dashboard install
docker compose up -d --build
```

The default stack starts and seeds:

- API: `http://localhost:8000`
- Dashboard: `http://localhost:5173`
- PostgreSQL: `localhost:5435`
- Redis: `localhost:6381`
- background worker, migrations, and deterministic platform fixture

For the complete ERPNext demonstration:

```powershell
docker compose --profile erpnext up -d --build
```

ERPNext is available at `http://localhost:8090` with the local demonstration account
documented in [infra/seed/README.md](./infra/seed/README.md). The seed workflow creates
the ERPNext site and data, configures a dedicated integration token, and requests an
initial full synchronization.

## Training

The committed baseline can be reproduced from the repository root:

```powershell
uv run --package cash-flow-training train-model `
  --config training/configs/baseline.yaml --no-gpu
```

See [training/README.md](./training/README.md) for the command contract and
[training-and-evaluation.md](./docs/context/training-and-evaluation.md) for the data,
method, results, and research limitations.

## Quality checks

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

## Project status

The planned platform workflow is implemented. The repository is suitable for local
demonstration, implementation study, and applied engineering research reporting. It is
not presented as a production treasury system or as an autonomous financial-control
tool.
