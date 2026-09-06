# Data and Ingestion

## Canonical accounting boundary

Every ingestion path produces the same canonical transaction shape before data can
reach aggregation or forecasting. The contract records enterprise and source
provenance, transaction type, transaction and optional due/settlement dates, positive
amount, three-letter currency, inflow/outflow direction, status, optional counterparty,
reference and description, stable source-record identifier, and source-payload hash.

This boundary prevents ERPNext fields, spreadsheet column details, and transport
configuration from leaking into forecasting logic.

## Supported sources

### ERPNext

The adapter uses token authentication and paginated REST requests. It ingests:

| ERPNext document | Canonical type | Direction |
| --- | --- | --- |
| Sales Invoice | invoice | inflow |
| Purchase Invoice | invoice | outflow |
| Payment Entry | payment | receive or pay direction |
| Journal Entry | adjustment | outflow |

Incremental requests filter by posting date. ERPNext status, currency, party, dates,
and monetary fields are validated and translated; unsupported or malformed individual
records are counted as failures without exposing their source format downstream.

### CSV and Excel

File uploads use a canonical tabular schema. CSV files must be UTF-8 and XLSX files
may specify a worksheet. Headers, row widths, dates, positive amounts, currency codes,
enums, and paired counterparty fields are validated. When a row omits a source-record
identifier, the adapter derives a stable identifier from the file checksum and row
number.

The API restricts accepted extensions, size, and upload paths. It persists checksum
and cleanup metadata, stages the file under an opaque key, and the worker verifies that
the resolved path remains inside the configured upload directory. Cleanup success or
failure is recorded after processing.

## Asynchronous processing and failure semantics

The API persists the ingestion request before publishing its command. The worker uses
a Redis consumer group and acknowledges a message only after its processing routine
returns successfully. Run-level states expose pending, running, completed, and failed
processing to the dashboard.

Adapter translation errors are isolated per record and reflected in received,
processed, and failed counters. Domain, adapter, and database failures roll back the
active unit of work, persist a failed run with a bounded error summary, and leave the
message unacknowledged for operational inspection or retry.

## Derived financial data

For every calendar month affected by an ingestion run, the worker reloads all
canonical transactions for that enterprise and month. It derives:

- total invoice amount
- total inflows and total outflows
- loan repayment total
- accumulated invoice payment-delay days
- invoice and payment counts

This rebuild-and-upsert strategy makes the aggregate reflect the complete canonical
ledger rather than only the latest batch.

The same pass derives customer-level invoice total, amount paid, outstanding balance,
average observed payment delay, and late-invoice count. Invoice-to-payment allocations
are also represented explicitly in persistence so partial settlements do not require
mutating the canonical invoice record.

## Static financial context

Forecasts combine temporal aggregates with the latest static snapshot available for
the requested target. A snapshot contains:

- credit and failure scores
- debt-to-revenue ratio
- current and fixed assets
- current and long-term liabilities
- capital expenditure and cost of goods sold
- missed-payment count

Entry mode distinguishes source-derived values from manual values. Snapshots are
unique per enterprise and date, so historical forecasts can retain the exact snapshot
they used.

## Data integrity and auditability

- Active ingestion source keys are unique within an enterprise; soft deletion permits
  replacement without erasing history.
- Transactions are unique by ingestion source and source-record identifier.
- Monetary columns use `NUMERIC`, avoiding binary floating-point storage for business
  values.
- Aggregate rows are unique by enterprise and calendar period.
- Forecast-run periods link predictions to the specific aggregate rows used as model
  inputs.
- Simulation patches are stored as JSON alongside query-critical typed columns.
- Public credential responses omit the stored secret value. The current repository
  stores `secret_ref` in PostgreSQL for demonstration purposes; a production design
  should replace this with an external secret manager.

## Research relevance

The ingestion layer is the bridge between an experimental model and a usable applied
system. Its canonicalization, provenance, validation, and aggregation rules define the
operational meaning of every feature later presented as evidence in a forecast or
simulation. These rules should be reported with the model because changing them can
change model inputs even when weights remain fixed.
