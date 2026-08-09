# ERPNext Ingestion Plan

## Purpose

This document defines the implementation strategy for the ERPNext ingestion workflow. It
is the detailed plan for the ERPNext work item tracked in
`docs/context/execution-plan.md`.

The workflow must demonstrate that an enterprise can configure an automated accounting
source, trigger synchronization, normalize ERPNext records, and persist financial data
for downstream forecasting.

## Objectives

- Resolve the ERPNext integration through the configured `source_key`.
- Authenticate using the configured ingestion-source credential.
- Fetch supported ERPNext accounting records incrementally.
- Translate external records into the canonical financial transaction shape.
- Persist ingestion-run progress, counts, and errors.
- Make synchronization repeatable and idempotent.
- Keep ERPNext-specific types and fields out of forecasting services.

## Scope

### Included

- Shared adapter protocol and source registry.
- ERPNext HTTP client and authentication handling.
- ERPNext record retrieval and pagination.
- Translation of supported ERPNext records into canonical transaction DTOs.
- Ingestion-run persistence and lifecycle updates.
- Worker synchronization job.
- API endpoints to request synchronization and inspect run status.
- Local Compose demonstration configuration.

### Deferred

- CSV and Excel ingestion.
- Full ERPNext accounting coverage.
- Bidirectional writes to ERPNext.
- Automatic credential discovery or secret-manager integration.
- Production-grade retry orchestration and distributed scheduling.

## Ownership Boundaries

### `shared/integrations`

Owns the adapter protocol, adapter registry, ERPNext client, ERPNext response models,
and ERPNext-to-canonical translation. It does not own ORM models, repositories, worker
scheduling, API routes, or forecasting logic.

### `shared/schemas`

Owns canonical transaction DTOs, ingestion-run request/response DTOs, and adapter-neutral
synchronization contracts.

### `shared/database`

Owns ingestion-run repository operations, financial-transaction persistence, and the
database-level idempotency boundary.

### `apps/api`

Owns synchronization request and run-status routes, request validation, and application
orchestration.

### `apps/worker`

Owns synchronization job execution and worker-side ingestion-run lifecycle orchestration.

## Workflow

1. An API client requests synchronization for an active enterprise ingestion source.
2. The API validates source ownership and active credentials.
3. The API creates a pending `ingestion_runs` record.
4. The API dispatches a synchronization job through the configured worker mechanism.
5. The worker marks the run as running.
6. The worker resolves the adapter using the source `source_key`.
7. The adapter retrieves ERPNext records using source configuration and credentials.
8. The adapter translates each supported record into a canonical transaction DTO.
9. The worker persists transactions using source-level idempotency keys.
10. The worker updates received, processed, and failed counts.
11. The worker marks the run completed or failed and records an error summary when needed.
12. Downstream aggregation workflows consume only canonical persisted records.

## Adapter Contract

The adapter contract should be framework-independent and expose operations equivalent to:

- `validate_configuration`
- `fetch_records`
- `translate_record`

The contract receives source configuration from `config_json`, credential material from
`secret_ref`, and an optional synchronization cursor or lower-bound timestamp.

The contract returns adapter-neutral records or canonical transaction DTOs. It must not
return ORM models or require a database session.

## Adapter Registry

The registry maps the persisted `source_key` to an adapter implementation.

Initial registration:

- `erpnext` -> `ERPNextAdapter`

Registry requirements:

- fail clearly when a source key is not registered
- prevent duplicate registrations during application startup
- expose a lookup interface usable by API and worker services
- keep registry construction deterministic for local demonstration

## ERPNext Integration Contract

The initial adapter should use ERPNext's HTTP API and support a focused set of accounting
records sufficient for the demonstration:

- Sales Invoices.
- Purchase Invoices.
- Payment Entries.
- Journal Entries where the required accounting fields are available.

The adapter should support a configured base URL, API key and API secret credentials,
request timeout, page size, incremental lower-bound date, response validation, and clear
transport and translation errors.

The adapter should not assume that every ERPNext installation has identical optional
fields. Required fields must be validated explicitly, and unsupported records must be
reported rather than silently discarded.

## Canonical Transaction Contract

The canonical transaction DTO should contain the fields required by
`financial_transactions`:

- enterprise, ingestion source, and ingestion run identifiers
- optional counterparty identifier or external counterparty key
- transaction type, date, optional due date, and optional settlement date
- amount as `Decimal`
- three-letter currency code
- inflow or outflow direction
- transaction status
- optional reference number and description
- stable source record identifier
- optional source payload hash

The DTO should validate currency-code shape, supported transaction type and direction
combinations, required source identity fields, and date ordering where both dates exist.
Financial amounts must remain decimal values through translation and persistence.

## ERPNext Mapping Rules

The mapping rules must be explicit and isolated from the HTTP client.

- Sales Invoice records map to invoice transactions with inflow direction.
- Purchase Invoice records map to invoice transactions with outflow direction.
- Payment Entry records map to payment transactions using their paid or received direction.
- Journal Entry records map only when one unambiguous canonical amount and direction can be derived.
- ERPNext document names become `source_record_id` values.
- ERPNext posting dates become transaction dates.
- Due dates and clearance dates are mapped when available.
- ERPNext totals and paid amounts are selected according to record type and documented in code.
- Unsupported currencies, malformed amounts, and ambiguous records produce translation errors.

## Persistence and Idempotency

The existing uniqueness constraint on `(ingestion_source_id, source_record_id)` is the
primary transaction idempotency boundary.

The workflow must use the same source record identifier for repeated fetches, treat
duplicates as already-ingested rather than fatal failures, avoid deleting historical
transactions during incremental synchronization, and keep run counts meaningful for
inserted, skipped, and failed records.

Ingestion-run transitions are limited to:

- `pending` -> `running`
- `running` -> `completed`
- `running` -> `failed`

The service layer owns lifecycle transitions; repositories only persist requested state
changes.

## API Surface

The initial API surface is nested under enterprise and source resources:

- `POST /enterprises/{enterprise_id}/ingestion-sources/{source_id}/sync`
  - create a pending run and dispatch work
- `GET /enterprises/{enterprise_id}/ingestion-sources/{source_id}/runs`
  - return paginated ingestion-run history
- `GET /enterprises/{enterprise_id}/ingestion-sources/{source_id}/runs/{run_id}`
  - return one run and its counts/status

The API must not return credential values. Synchronization requests accept only workflow
parameters such as an incremental lower-bound date or force-full-sync intent.

## Worker Design

The worker job accepts an ingestion-run identifier, loads the run/source/enterprise and
active credential, resolves the adapter from `source_key`, executes retrieval and
translation, persists canonical transactions in bounded batches, updates run progress,
and ensures expected errors do not leave runs indefinitely in `running`.

Redis may be used for job dispatch and coordination, but PostgreSQL remains the source of
truth for ingestion-run state.

## Implementation Phases

### Phase A: Contracts and Registry

- Define canonical transaction DTOs.
- Define adapter-neutral record and synchronization contracts.
- Define adapter exceptions.
- Implement the adapter registry.
- Register `erpnext` by source key.
- Define the ingestion job stream, consumer group, and message envelope.
- Publish only the `ingestion_run_id` and required trace metadata to Redis Streams.

### Phase B: ERPNext Adapter

- Implement ERPNext client configuration and API-key authentication.
- Implement paginated record retrieval.
- Add ERPNext response schemas.
- Implement isolated record translators.
- Add explicit mapping and validation errors.

### Phase C: Persistence Workflow

- Define ingestion-run schemas.
- Add ingestion-run repository methods.
- Add financial-transaction repository methods.
- Extend unit-of-work interfaces and implementation.
- Implement idempotent transaction persistence.

### Phase D: Worker Execution

- Add worker synchronization service.
- Add synchronization job entrypoint.
- Implement run lifecycle transitions.
- Implement batch counts and failure handling.
- Wire Redis dispatch if required by the worker runtime.
- Consume ingestion job messages through the shared `event_broker` package.

### Phase E: API Orchestration

- Add synchronization request service.
- Add paginated run-history service.
- Add synchronization and run-status routes.
- Enforce ownership and active-resource checks.

### Phase F: Compose Demonstration

- Add local ERPNext connection configuration.
- Add seed or setup instructions for demo accounting records.
- Verify API-triggered synchronization through the worker.
- Verify persisted transactions and run status in PostgreSQL.

## Verification Criteria

The workflow is complete when:

- an active ERPNext source and credential can be configured through the API
- a synchronization request creates a pending run
- the worker resolves the ERPNext adapter through `source_key`
- supported ERPNext records become canonical financial transactions
- repeated synchronization does not create duplicate transactions
- failed records and transport errors are reflected in run counts and status
- run history is paginated
- no ERPNext-specific fields appear in forecasting service inputs
- the complete flow runs through Docker Compose
- Ruff, mypy, Alembic checks, and API import checks pass
