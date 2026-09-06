# Current Architecture

## Runtime topology

```text
ERPNext / CSV / XLSX
         |
         v
    FastAPI API ------> Redis Stream ------> Worker
         |                                      |
         |                                      +-- source adapter
         |                                      +-- canonical transactions
         |                                      +-- monthly aggregates
         |                                      |
         +------------------+-------------------+
                            |
                            v
                       PostgreSQL
                            ^
                            |
                     React dashboard

Model artifacts ---> API forecasting and simulation services
```

The API, worker, and dashboard are independently runnable applications within a
modular-monolith repository. Shared packages contain stable domain, contract,
persistence, integration, event-broker, and ML primitives. PostgreSQL owns durable
business state; Redis provides the asynchronous ingestion boundary; model artifacts
are loaded from the filesystem for synchronous forecast and simulation evaluation.

## Ownership boundaries

| Area | Implemented responsibility |
| --- | --- |
| `apps/api` | HTTP routes, request validation, infrastructure lifecycle, and enterprise, ingestion, forecasting, simulation, and receivables orchestration |
| `apps/worker` | Redis consumer, source synchronization, transaction persistence, and monthly aggregation |
| `apps/dashboard` | React presentation, generated OpenAPI contract consumption, and finance-user workflows |
| `training` | Dataset preparation, sequence construction, model training, evaluation, and artifact generation |
| `shared/domain` | Framework-independent entities, enums, validation rules, and health scoring |
| `shared/schemas` | Pydantic contracts shared across applications and persistence boundaries |
| `shared/database` | SQLAlchemy models, repositories, read queries, sessions, and unit of work |
| `shared/ml` | Artifact loading, input validation, currency conversion, runtime model, and inference |
| `shared/integrations` | ERPNext, CSV, and Excel adapters and canonical translation |
| `shared/event_broker` | Redis Streams lifecycle, publishing, group reads, acknowledgement, and deletion |
| `infra/migrations` | Alembic schema history |
| `infra/seed` | Deterministic API, database, and ERPNext demonstration fixtures |

## Ingestion lifecycle

1. The API creates an ingestion run for an active enterprise source. File requests
   first stage an upload in a shared volume and persist its checksum and metadata.
2. The API publishes the run, enterprise, source, and optional cursor identifiers to
   a Redis Stream and returns HTTP `202 Accepted`.
3. The worker consumer resolves the registered adapter: ERPNext, CSV, or Excel.
4. The adapter validates its configuration, fetches records, and translates each
   source record into the canonical transaction contract.
5. The worker creates counterparties as needed and stores transactions using the
   source and source-record identifier as an idempotency boundary.
6. The worker rebuilds every calendar month touched by the run from all canonical
   transactions in that month. It upserts enterprise aggregates and counterparty
   receivable aggregates.
7. The run becomes completed or failed. Staged files are removed and cleanup status
   is recorded. Successfully processed stream messages are acknowledged.

## Forecast lifecycle

1. A request identifies an enterprise, target period, run type, and non-negative
   solvency buffer.
2. The API requires the six complete calendar months preceding the target and the
   latest eligible static financial snapshot.
3. Shared ML services validate feature names and order, normalize currency, apply the
   committed scalers, and evaluate the versioned model.
4. Runtime inference blends the neural prediction with the mean net cash flow of the
   six input periods. Inputs outside the configured standardized support guard fall
   back entirely to the persistence estimate.
5. PostgreSQL stores the result, buffer gap, artifact provenance, and links to every
   aggregate used by the run.
6. Read services add expected cash movements and cautious observations derived from
   the persisted inputs for dashboard presentation.

## Simulation lifecycle

All simulations start from a completed persisted forecast. The service reloads the
artifact used by that forecast and rejects an artifact-version mismatch. A shared
counterfactual evaluator patches only approved temporal or static inputs, runs the same
inference path, and compares the result with the baseline and solvency buffer.

Simulation runs move through pending, running, completed, or failed states. Scenario
inputs, predictions, deltas, rankings, recommendations, and summary metadata are
persisted, keeping hypothetical results separate from financial transactions.

## Persistence boundaries

The principal evidence chain is:

```text
enterprise
  -> ingestion source -> credential
                      -> ingestion run -> upload
                                       -> financial transactions
                                            -> monthly aggregates
                                            -> counterparty receivables
  -> static financial snapshots
  -> forecast run -> forecast input periods
                  -> simulation run
                       -> scenarios
                       -> receivables rankings
                       -> mitigation recommendations
```

Financial values use fixed-precision numeric columns. Operational timestamps are
timezone-aware. UUID identifiers and enterprise foreign keys preserve ownership, while
indexes support date-window and recent-run queries. Alembic migrations are the only
schema-evolution mechanism.

## Deployment model

Docker Compose builds separate API, worker, dashboard, and bootstrap images and starts
PostgreSQL and Redis with health checks. Migration and seed containers are one-shot
dependencies. The API and worker share only the staged-upload volume. An optional
`erpnext` profile adds MariaDB, ERPNext backend/frontend/websocket services, supporting
Redis instances, and an automated ERPNext seed.

The architecture is intentionally compact: application boundaries are explicit
without introducing independently deployed services for every domain operation.
