# Cash Flow Prediction Platform: System Overview

## Purpose

The Cash Flow Prediction platform is an enterprise-style decision-support system
implemented as an applied machine-learning engineering project. It turns accounting
records into a next-period net cash-flow forecast, compares that forecast with a
user-selected solvency buffer, and lets a finance user test bounded counterfactuals
before taking action.

The project develops both the cash-flow forecasting model and the complete,
reproducible software platform around it. Its contribution spans dataset preparation,
feature engineering, model design, training, and evaluation as well as data
acquisition, canonicalization, asynchronous processing, artifact-controlled
inference, scenario analysis, audit persistence, and an executive dashboard.

## Implemented capabilities

- Enterprise onboarding and enterprise-scoped data access
- Automated ERPNext ingestion for sales invoices, purchase invoices, payments, and
  journal entries
- UTF-8 CSV and XLSX upload ingestion through the same canonical transaction contract
- Redis Streams handoff from the API to a background worker
- Idempotent financial transaction storage and monthly aggregate reconstruction
- Static financial snapshots with manual or source-derived entry modes
- Six-month temporal and ten-feature static model input preparation
- Versioned LSTM/static-feature inference blended with a persistence estimate
- Currency normalization between the GBP research data and INR demonstration data
- Baseline forecasts with solvency-buffer comparison and model provenance
- Financial-health sensitivity scenarios
- Counterparty receivables ranking and trapped-liquidity estimation
- Bounded liquidity-mitigation recommendations
- Executive dashboard for overview, forecast, health, receivables, planning, and data
  management
- Deterministic platform and optional ERPNext demonstration data

## Applied research contribution

The research component investigates the feasibility of combining temporal cash-flow
history with enterprise financial attributes and implements the resulting hybrid
forecasting model. The engineering component addresses the complementary system
question: how can that model be trained reproducibly, served with explicit artifact
contracts, supplied with operational accounting data, and used for transparent
decision support without automating financial control?

The implemented design contributes four practical mechanisms:

1. A canonical accounting boundary isolates forecasting from ERP- and file-specific
   formats.
2. A versioned artifact contract keeps training feature order, model architecture,
   scalers, currency assumptions, and runtime inference aligned.
3. Persisted forecast inputs and counterfactual results make outputs inspectable and
   reproducible.
4. Bounded simulations translate a point forecast into sensitivity analysis,
   collection prioritization, and feasible mitigation options.

## Scope and limitations

The platform is a final-year engineering demonstrator, not a production treasury
system. It deliberately does not claim:

- production calibration across industries, countries, or economic regimes
- causal effects from counterfactual forecasts
- autonomous payment, lending, collection, or capital-expenditure decisions
- enterprise identity and access management or production secret storage
- exhaustive ERP connector coverage or hyperscale event processing

The training dataset represents UK SMEs and is assumed to be GBP-denominated. The
India-facing fixture uses a fixed model-reference conversion of `1 GBP = 100 INR`.
That value is an explicit normalization assumption, not a live exchange rate.

## Core engineering principles

1. PostgreSQL is the system of record; Redis Streams is the durable asynchronous
   transport between API and worker.
2. Source formats end at the integration boundary. Forecasting consumes only the
   canonical transaction and aggregate model.
3. Forecast runs retain their input-period links and artifact provenance.
4. Scenario outputs remain decision support and are stored separately from source
   financial facts.
5. Training scripts are canonical; notebooks are exploratory.
6. The runtime remains a compact modular monolith packaged with Docker Compose.

## Technology baseline

- Python 3.13, FastAPI, Pydantic, SQLAlchemy, and Alembic
- PyTorch, pandas, NumPy, and scikit-learn
- React 19, TypeScript, Vite, and Tailwind CSS
- PostgreSQL 17 and Redis 8
- Docker Compose, uv, Ruff, mypy, pytest, ESLint, Prettier, and pre-commit

## Documentation boundary

The source study and original product requirements are preserved under
`docs/reference`. The documents in this directory describe the completed repository,
its rationale, its measurable results, and the limitations that should accompany any
research-paper claims.
