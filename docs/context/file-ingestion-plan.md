# CSV and Excel Ingestion Plan

## Purpose

This document defines the implementation strategy for fallback CSV and Excel file
imports. It is the detailed plan for the CSV and Excel work items tracked in
`docs/context/execution-plan.md`.

The file-import path must accept a documented accounting template, validate it
strictly, translate every accepted row into the same canonical transaction shape as
ERPNext, and persist the result through the existing ingestion-run workflow.

## Objectives

- Support `.csv` and `.xlsx` uploads through the API.
- Keep parsing and file-format concerns inside `shared/integrations`.
- Reuse the existing adapter registry, canonical transaction DTO, worker job, run
  lifecycle, counterparty resolution, and idempotent transaction repository.
- Make malformed rows visible through run counts and error summaries.
- Make repeated uploads deterministic and idempotent.
- Prevent external column names and spreadsheet-specific values from reaching
  forecasting services.

## Scope

### Included

- A documented canonical upload template.
- CSV parsing using the Python standard library.
- Excel parsing using pandas with the `openpyxl` engine for `.xlsx` workbooks.
- Header, type, enum, date, currency, amount, and row-level validation.
- CSV and Excel adapter implementations registered under stable source keys.
- Multipart upload API orchestration and asynchronous worker processing.
- Upload metadata, temporary-file lifecycle, and content-hash handling.
- Reuse of the existing financial transaction persistence and run-status endpoints.
- Unit, integration, and Compose demonstration coverage.

### Deferred

- Arbitrary spreadsheet column mapping UI.
- Multi-workbook reconciliation or cross-file joins.
- Automatic accounting classification from free-form descriptions.
- Raw-row persistence as a second financial source of truth.
- Direct import of static financial snapshots; this may use a later, separate template.
- Large-scale object storage and production antivirus/data-loss-prevention tooling.

## Ownership Boundaries

### `shared/integrations`

Owns file-type detection, CSV/Excel readers, canonical-header validation, row
translation, deterministic source identifiers, payload hashing, and adapter-specific
exceptions. It must not own FastAPI uploads, ORM models, repositories, or worker
scheduling.

Recommended modules:

- `csv.py`: CSV reader and row translation.
- `excel.py`: workbook reader and row translation.
- `file_models.py`: file configuration and parsed-row contracts if the existing
  integration models become too ERPNext-specific.
- `file_validation.py`: shared header and scalar validation helpers.

### `shared/schemas`

Owns adapter-neutral upload request/response DTOs and any internal upload metadata
contract. The canonical transaction persistence schema remains the existing
`FinancialTransactionCreateSchema`.

### `shared/database`

Owns any upload metadata persistence and the existing ingestion-run and transaction
repositories. It remains the database-level idempotency boundary.

### `apps/api`

Owns multipart request handling, file size and extension checks, source ownership
validation, upload staging, run creation, and Redis command publication. It should
not parse spreadsheet rows or translate accounting values.

### `apps/worker`

Owns loading the staged upload, resolving the adapter by `source_key`, executing the
same bounded translation/persistence loop used by automated ingestion, updating run
counts, and cleaning up staged files after processing.

## Canonical Upload Template

The initial implementation should require one stable header contract rather than
supporting arbitrary user-defined mappings. Header matching should trim whitespace,
be case-insensitive, and normalize spaces/hyphens to underscores.

Required columns:

- `source_record_id`
- `transaction_type`
- `transaction_date`
- `amount`
- `currency_code`
- `direction`

Optional columns:

- `due_date`
- `settlement_date`
- `status` (default `pending` when absent)
- `counterparty_external_key`
- `counterparty_name`
- `counterparty_type`
- `reference_number`
- `description`

Supported values must be exactly the existing domain enum values after normalization:
`transaction_type`, `direction`, `status`, and `counterparty_type` must not be
silently guessed from descriptions. Amounts must be positive decimal values, currency
codes must be three-letter ISO-style uppercase codes, and settlement/due dates must
not precede the transaction date.

The template documentation should include CSV and Excel examples, date format rules
(ISO `YYYY-MM-DD`), decimal and blank-value rules, maximum text lengths, and one row
per transaction. Excel imports should read a configured sheet name when supplied;
otherwise they should use the first visible worksheet and reject workbooks without a
usable header row.

## Upload Handoff and Metadata

File bytes must not be placed in Redis Streams. The API should:

1. Verify the enterprise and active file ingestion source.
2. Verify extension, supported MIME type, configured maximum size, and a non-empty
   filename.
3. Stream the upload to a configured staging directory shared by API and worker
   containers, while calculating SHA-256 and byte count.
4. Create an `UPLOAD` ingestion run and persist the staged-file metadata needed by the
   worker: storage key/path, original filename, detected format, content hash, and
   size.
5. Publish only the run identifier, source identifier, enterprise identifier, and
   trace metadata through Redis Streams.

Because the current `ingestion_runs` model has no file reference, add a small upload
metadata representation before implementation. Prefer an `ingestion_uploads` table
linked one-to-one with `ingestion_runs`; it should contain the run ID, original name,
storage key, format, SHA-256, byte size, and cleanup status/timestamps. Do not store
file contents in PostgreSQL. If implementation review shows a dedicated table is
unnecessary, equivalent fields may be added to `ingestion_runs`, but the choice must
be recorded in the schema context and migration.

The staged file must be addressed by an opaque generated key, not by an untrusted
client filename. API and worker Compose services must mount the same staging volume.
The worker must delete or quarantine the file after terminal processing, and failed
cleanup must be recorded without changing a successfully completed run to failed.

## Adapter and Processing Workflow

Register two source keys:

- `csv` -> `CSVFileAdapter`
- `excel` -> `ExcelFileAdapter`

Both adapters should implement the existing `IIngestionAdapter` contract. Their
`fetch_records` methods read the staged file and yield `RawIngestionRecord` values;
their `translate_record` methods return `CanonicalTransactionRecord` values. The
worker should not need format-specific branches beyond adapter resolution.

The end-to-end flow is:

1. The API receives a multipart upload and performs cheap request-level checks.
2. The API stages the file, creates an `UPLOAD` run and upload metadata, then publishes
   the run command.
3. The worker loads the run, source, and upload metadata and resolves `csv` or `excel`
   through the registry.
4. The adapter validates headers and emits rows with stable row context.
5. Each row is translated to the canonical transaction DTO.
6. The worker resolves or creates a counterparty when all counterparty identity fields
   are present.
7. Transactions are persisted in bounded batches using the existing unique
   `(ingestion_source_id, source_record_id)` constraint.
8. Duplicate rows or repeated uploads are counted as skipped/duplicate work, not as
   fatal run errors. The existing run counters may need a `records_skipped` field if
   duplicate visibility is required by the API; otherwise document that processed
   means accepted rows and failed means rejected rows.
9. The worker completes or fails the run, records a bounded error summary, updates
   `last_synced_at` only on successful processing, and cleans up the staged file.

For deterministic idempotency, use the supplied `source_record_id` when present. If
it is blank and the template permits a generated identifier, generate
`<file_sha256>:row:<one-based-row-number>`; otherwise reject the row. Never use only
the human filename as an identity key.

## Validation and Error Policy

Validation should happen in two layers:

- File-level: extension/format, readable encoding, workbook/sheet availability,
  required headers, duplicate headers, and configured row/file limits.
- Row-level: required values, date parsing, decimal parsing, enum values, currency,
  positive amount, date ordering, and maximum lengths.

Use structured integration exceptions that include the source row number and column
name. A bad row should increment `records_failed` and allow later rows to continue.
An unreadable file, missing required header, unsupported workbook, or parser failure
should fail the run as a whole. Error output must be bounded and must not include file
contents or secrets.

Encoding policy for CSV should be explicit: try UTF-8 (including BOM handling), then
reject with a clear error rather than guessing across many legacy encodings. Excel
formula cells should use their stored/calculated values; formulas that do not expose a
usable value are row-level validation failures.

## API Surface

Add an upload route nested under the existing source resource, for example:

`POST /enterprises/{enterprise_id}/ingestion-sources/{source_id}/upload`

The request contains one file and optional workflow parameters such as `sheet_name`
and a replace/duplicate policy only if the implementation needs them. The response
is `202 Accepted` with the created `IngestionRunSchema`; clients use the existing run
history and run-detail endpoints for progress.

The route must reject sources whose `source_key` is not `csv` or `excel`, prevent
enterprise/source mismatches, avoid exposing staged paths, and never return credential
or file contents. A separate template-download endpoint is optional and should not
block the initial import workflow.

## Implementation Phases

### Phase A: Contract and configuration

- Freeze the canonical headers and enum/date/amount rules.
- Add file-specific adapter configuration and maximum file/row limits.
- Define upload metadata schema, cleanup states, and migration.
- Define structured file-validation exceptions and row error representation.

### Phase B: Shared file adapters

- Implement common header/scalar/date/decimal validation.
- Implement streaming CSV reading with row numbers.
- Implement bounded Excel worksheet reading and sheet selection.
- Implement deterministic source IDs and payload hashes.
- Register `csv` and `excel` adapters.
- Add adapter unit tests with valid, malformed, duplicate-header, BOM, blank-row,
  formula, and unsupported-value fixtures.

### Phase C: API upload orchestration

- Add multipart upload route and request validation.
- Add safe staging service with size limit, generated storage key, hash, and metadata.
- Create `UPLOAD` runs and publish compact Redis messages.
- Add cleanup for failures between staging and dispatch.
- Add API tests for ownership, extension/MIME mismatch, size limits, and dispatch.

### Phase D: Worker persistence integration

- Load upload metadata from the run.
- Reuse or refactor the existing synchronization loop so file and ERPNext adapters
  share counterparty resolution, batch persistence, lifecycle transitions, and counts.
- Add duplicate handling and per-row error aggregation.
- Implement terminal cleanup/quarantine behavior.
- Add worker tests for successful imports, partial row failures, repeated uploads, and
  terminal failure paths.

### Phase E: End-to-end verification and documentation

- Add representative CSV and Excel fixtures using the canonical template.
- Run migration checks and verify the upload metadata relationship.
- Exercise API -> Redis Streams -> worker -> PostgreSQL in Docker Compose.
- Verify normalized records are usable by monthly aggregation without source-specific
  branches.
- Document the template, demo command sequence, supported limitations, and cleanup
  behavior in the operator README.

## Verification Criteria

The workflow is complete when:

- valid CSV and Excel uploads create `UPLOAD` runs and return `202` responses;
- the worker resolves both adapters through `source_key`;
- valid rows become canonical `financial_transactions` records;
- invalid rows are counted and reported with row/column context;
- missing headers and unreadable files fail the run clearly;
- repeated uploads do not create duplicate transactions;
- source-specific columns and values do not reach forecasting services;
- staged files are not exposed through API responses and are cleaned up/quarantined;
- API and worker can access the same staged file in Compose;
- upload and ERPNext runs share the same run-history API and persistence boundary;
- Ruff, mypy, migration checks, adapter tests, API tests, worker tests, and the
  Compose smoke test pass.

## Risks and Decisions to Preserve

- Do not make arbitrary column mapping part of the MVP; it weakens reproducibility.
- Do not send file bytes through Redis or keep them only in API process memory.
- Do not let pandas/openpyxl dataframes become shared downstream contracts; translate
  immediately into adapter-neutral records.
- Do not silently infer transaction direction, type, or status from descriptions.
- Keep the first implementation focused on normalized transactions. Static snapshots
  and monthly aggregates should be separate workflows built on explicit contracts.
