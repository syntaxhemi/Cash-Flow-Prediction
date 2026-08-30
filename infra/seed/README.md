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
- `seed-state.json` — generated local resource IDs; do not commit it.

## Seed order

Start PostgreSQL, Redis, and the API first. Then run:

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
