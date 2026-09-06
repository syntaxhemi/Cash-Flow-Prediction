# Demo seed data

This directory contains the reproducible 2026 demo fixture for the Cash Flow
Prediction platform. The fixture is based on the database models, shared schemas,
domain enums, aggregation rules, and forecasting/simulation persistence contracts.

## Files

- `seed-data.json` — the single source of truth for API resources and database rows.
- `seed_api.py` — creates or reuses the demo enterprise, ingestion sources, and
  ERPNext credential through the API.
- `seed_database.py` — inserts deterministic, idempotent records through the shared
  SQLAlchemy models.
- `seed_platform.py` — runs both platform seed stages in one ephemeral operation for
  Docker Compose.
- `seed-state.json` — generated local resource IDs; do not commit it.

Additional ERPNext bootstrap files:

- `erpnext-seed-data.json` — ERPNext setup, master, and transaction fixtures modeled
  after `demo-upload-aug-sep-2026.csv`.
- `seed_erpnext.py` — completes ERPNext setup through HTTP APIs, seeds accounting
  records, rotates a dedicated integration token, configures the platform credential,
  and requests a full synchronization.

## One-command ERPNext bootstrap

For the complete local stack, including the platform fixture, ERPNext bootstrap, and
initial synchronization, run:

```powershell
docker compose --profile erpnext up -d --build
```

Compose runs `platform-seed` first to load the historical platform fixture. The
`erpnext-seed` one-shot service then waits for ERPNext, logs in with the
local Administrator bootstrap account, completes company setup, and creates or reuses
demo masters and transactions. It generates a fresh token for the dedicated
integration user on every run and rotates the same credential entry through the cash
flow API. The token is not printed or written to disk. Inspect progress with:

```powershell
docker compose logs -f platform-seed erpnext-seed
```

The worker connects to ERPNext over the shared Compose network at
`http://erpnext-frontend:8080`. Set `TRIGGER_ERPNEXT_SYNC=false` on the seed service to
configure the source without automatically requesting a full synchronization.

## Seed order

Compose automates the following dependency order:

```text
migrate -> API -> platform-seed -> erpnext-seed -> full sync
```

For a manual host-side seed, start PostgreSQL, Redis, and the API first. Then run:

```powershell
uv run alembic -c infra/migrations/alembic.ini upgrade head
uv run python .\infra\seed\seed_api.py
uv run python .\infra\seed\seed_database.py
```

The API loader must run before the database loader because the database fixture uses
the API-created enterprise and ingestion-source IDs. Both loaders are safe to rerun;
existing seeded records are preserved by deterministic IDs and the database natural
keys.

## Configuration

The loaders use the normal application environment variables. The database loader
uses `DB_HOST`, `DB_PORT`, `DB_USERNAME`, `DB_PASSWORD`, and `DB_NAME`. The API loader
accepts:

```text
--base-url URL       API URL; defaults to http://localhost:8000
--seed-file PATH     Alternate JSON fixture
--state-file PATH    Alternate generated state file
```

The database loader accepts `--seed-file` and `--state-file` with the same defaults.

The fixture uses February through July 2026 as the six-month temporal history and
August 2026 as the forecast target period. Monetary values are stored as strings in
JSON so they remain exact decimals through loading.

The India-facing fixture is denominated in INR and calibrated to the baseline
artifact's fixed `1 GBP = 100 INR` model-reference rate. Its converted monthly inputs
remain within a maximum absolute standardized magnitude of 5, and its monthly net cash
flow remains within the research dataset's observed target envelope. The stored
forecast and simulation outputs are evaluations from baseline artifact version 3, not
hand-authored presentation values.

Seed integrity tests recompute monthly aggregates and receivable balances from the
transaction ledger, rerun the baseline model, and reproduce health, trapped-liquidity,
and mitigation outcomes. The database loader updates deterministic seed rows on rerun,
so fixture revisions do not require recreating the database.
