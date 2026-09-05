# Schema Overview

## Purpose

This document records the agreed initial database schema direction for the platform.

It should be used to:

- define the core persisted entities
- clarify ownership boundaries between raw ingestion, normalized records, aggregates, forecasts, and simulations
- identify relationships and constraints before SQLAlchemy models are implemented

## Design Principles

The schema should reflect the platform architecture already agreed:

- PostgreSQL is the system of record
- ingestion paths converge into one internal normalized accounting model
- forecasting is built from temporal and static financial features
- simulation outputs are derived operational artifacts, not primary ledger truth
- the model needs both chronological financial history and point-in-time static health metrics

The schema should therefore separate:

- enterprise identity and configuration
- ingestion source metadata
- normalized financial records
- monthly forecast-ready aggregates
- point-in-time static financial metrics
- forecast executions
- simulation executions

## Schema Layers

The initial schema should be thought of in six layers:

1. enterprise and source configuration
2. normalized operational financial data
3. forecast-ready derived data
4. model execution records
5. simulation and recommendation records
6. artifact and audit metadata

## Proposed Core Entities

### 1. `enterprises`

Represents the target business entity whose cash flow is being modeled.

Suggested fields:

- `id`
- `external_key`
- `legal_name`
- `registration_number`
- `industry`
- `country_code`
- `base_currency`
- `timezone`
- `is_active`
- `created_at`
- `updated_at`

Notes:

- `external_key` is a stable application-level identifier
- `registration_number` may be nullable depending on source quality
- this is the parent entity for most platform data

### 2. `ingestion_sources`

Represents a configured source of accounting data for an enterprise.

Suggested fields:

- `id`
- `enterprise_id`
- `source_key`
- `display_name`
- `status`
- `is_active`
- `deleted_at`
- `last_synced_at`
- `created_at`
- `updated_at`

Notes:

- this table identifies where records came from
- `source_key` should be the stable lookup key used by application code to resolve the correct ingestion implementation
- `(enterprise_id, source_key)` is unique only for active sources, so a deactivated connection does not block a replacement
- credentials or secrets should not be mixed directly into this source identity record if that can be avoided

### 2a. `ingestion_source_credentials`

Represents persisted enterprise-specific connection state required for automated ingestion.

Suggested fields:

- `id`
- `enterprise_id`
- `ingestion_source_id`
- `credential_type`
- `status`
- `config_json`
- `secret_ref`
- `last_rotated_at`
- `expires_at`
- `created_at`
- `updated_at`

Notes:

- enterprise-specific ingestion credentials must be persisted because the platform needs to synchronize data from different enterprises over time
- keep source identity and credential material separated into different tables
- `config_json` should store non-secret connection metadata required by the ingestion implementation
- `secret_ref` stores the credential material required by the ingestion implementation

### 3. `ingestion_runs`

Represents a concrete synchronization or import execution.

Suggested fields:

- `id`
- `enterprise_id`
- `ingestion_source_id`
- `run_type`
- `status`
- `started_at`
- `finished_at`
- `records_received`
- `records_processed`
- `records_failed`
- `error_summary`
- `created_at`

Notes:

- this is useful for traceability and demo visibility
- uploads and automated syncs should both create runs

### 3a. `ingestion_uploads`

Represents metadata for a staged file associated with an upload ingestion run.

Suggested fields:

- `id`
- `ingestion_run_id`
- `storage_key`
- `original_filename`
- `file_format`
- `content_type`
- `size_bytes`
- `sha256`
- `sheet_name`
- `cleanup_status`
- `cleaned_at`
- `cleanup_error`
- `created_at`
- `updated_at`

Notes:

- this is a one-to-one child of `ingestion_runs`
- it stores file metadata only; file contents remain on the configured staging volume
- ERPNext and other non-file runs do not create a row here
- `storage_key` must be an opaque generated key rather than a client-supplied path

### 4. `counterparties`

Represents customers, clients, lenders, or other external parties referenced by financial activity.

Suggested fields:

- `id`
- `enterprise_id`
- `external_key`
- `name`
- `counterparty_type`
- `is_active`
- `created_at`
- `updated_at`

Suggested `counterparty_type` values:

- `customer`
- `supplier`
- `lender`
- `other`

Notes:

- this creates a normalized anchor for receivables and payment-delay analysis
- not every source record will necessarily map cleanly at first, so nullable linkage may be needed elsewhere

### 5. `financial_transactions`

Represents normalized individual financial records after ingestion.

This is the most important operational table.

Suggested fields:

- `id`
- `enterprise_id`
- `ingestion_source_id`
- `ingestion_run_id`
- `counterparty_id`
- `transaction_type`
- `transaction_date`
- `due_date`
- `settlement_date`
- `amount`
- `currency_code`
- `direction`
- `status`
- `reference_number`
- `description`
- `source_record_id`
- `source_payload_hash`
- `created_at`
- `updated_at`

Suggested `transaction_type` values:

- `invoice`
- `payment`
- `loan_repayment`
- `expense`
- `deposit`
- `adjustment`

Suggested `direction` values:

- `inflow`
- `outflow`

Notes:

- this table should store normalized operational truth, not model features
- `source_record_id` plus `ingestion_source_id` should help with idempotency
- `source_payload_hash` can support duplicate detection when source identifiers are weak

### 5a. `invoice_payment_allocations`

Represents the invoice-level application of a payment transaction.

Suggested fields:

- `id`
- `enterprise_id`
- `invoice_id`
- `payment_transaction_id`
- `allocated_amount`
- `created_at`
- `updated_at`

Notes:

- payments remain normalized transactions; this table records how they are
  applied to invoices
- one payment may be allocated across multiple invoices
- one invoice may receive multiple payments
- invoice-level paid, partially-paid, and outstanding amounts are derived from
  allocation rows rather than inferred from counterparty totals

### 6. `monthly_cashflow_aggregates`

Represents enterprise-level monthly temporal features used for forecasting.

Suggested fields:

- `id`
- `enterprise_id`
- `period_start`
- `period_end`
- `total_invoice_amount`
- `total_inflows`
- `total_outflows`
- `monthly_repayment`
- `total_payment_delay_days`
- `invoice_count`
- `payment_count`
- `derived_from_run_id`
- `created_at`
- `updated_at`

Notes:

- one row per enterprise per month
- this table is derived from `financial_transactions`
- it exists to support reproducible temporal window reconstruction
- `total_payment_delay_days` is the sum of settled invoice delays in the month, where each delay is `settlement_date - transaction_date`
- temporal aggregates are intentionally materialized at the enterprise-month level rather than rebuilt on demand from raw transactions during forecasting requests

### 7. `counterparty_monthly_receivables`

Represents client-level monthly receivables features for trapped-liquidity analysis.

Suggested fields:

- `id`
- `enterprise_id`
- `counterparty_id`
- `period_start`
- `period_end`
- `invoice_total`
- `amount_paid`
- `outstanding_amount`
- `average_payment_delay_days`
- `late_invoice_count`
- `created_at`
- `updated_at`

Notes:

- this supports ranking debtors by modeled liquidity impact
- it is derived, not primary operational truth

### 8. `static_financial_snapshots`

Represents point-in-time static health metrics used by the dense branch of the model.

Suggested fields:

- `id`
- `enterprise_id`
- `ingestion_source_id`
- `snapshot_date`
- `entry_mode`
- `credit_score`
- `failure_score`
- `debt_to_revenue_ratio`
- `current_assets`
- `current_liabilities`
- `fixed_assets`
- `long_term_liabilities`
- `capex`
- `cogs`
- `missed_payments_number`
- `created_at`
- `updated_at`

Notes:

- multiple snapshots over time are expected
- the forecasting service should choose the most appropriate snapshot relative to the prediction point
- snapshots should support both source-derived and manually entered or adjusted values
- `ingestion_source_id` may be nullable for manually created snapshots

### 9. `forecast_runs`

Represents baseline forecasting executions.

Suggested fields:

- `id`
- `enterprise_id`
- `run_type`
- `target_period_start`
- `target_period_end`
- `sequence_window_months`
- `static_snapshot_id`
- `model_version`
- `artifact_version`
- `predicted_net_cashflow`
- `solvency_buffer`
- `buffer_gap`
- `status`
- `requested_at`
- `completed_at`
- `created_at`

Suggested `run_type` values:

- `baseline`
- `scheduled_baseline`
- `ad_hoc_baseline`

Notes:

- this records execution outcomes, not just current dashboard state
- it should allow later audit and comparison

### 10. `forecast_run_periods`

Represents the temporal rows used by a specific forecast run.

Suggested fields:

- `id`
- `forecast_run_id`
- `monthly_cashflow_aggregate_id`
- `sequence_index`

Notes:

- this creates an explicit audit trail for which six periods fed the model
- optional, but recommended for reproducibility

### 11. `simulation_runs`

Represents counterfactual simulation executions.

Suggested fields:

- `id`
- `enterprise_id`
- `forecast_run_id`
- `simulation_type`
- `status`
- `summary_result`
- `requested_at`
- `completed_at`
- `created_at`

Suggested `simulation_type` values:

- `health_delta`
- `trapped_liquidity`
- `liquidity_mitigation`

Notes:

- this is the parent record for all simulation outputs

### 12. `simulation_scenarios`

Represents individual scenarios tested within one simulation run.

Suggested fields:

- `id`
- `simulation_run_id`
- `scenario_index`
- `scenario_label`
- `input_patch_json`
- `predicted_net_cashflow`
- `delta_from_baseline`
- `meets_buffer`
- `created_at`

Notes:

- `input_patch_json` stores the changed variables for that scenario
- this is especially useful for health delta sweeps and mitigation permutations
- summary and query-critical fields should remain normal columns
- scenario-specific input modifications should remain in JSON rather than being fully normalized into dedicated columns

### 13. `receivables_rankings`

Represents ranked receivables insights generated by trapped-liquidity simulation.

Suggested fields:

- `id`
- `simulation_run_id`
- `counterparty_id`
- `rank_position`
- `baseline_outstanding_amount`
- `simulated_cashflow_delta`
- `created_at`

Notes:

- this is separate from raw receivables data because it is explicitly model-derived

### 14. `mitigation_recommendations`

Represents recommendation outputs from liquidity mitigation planning.

Suggested fields:

- `id`
- `simulation_run_id`
- `priority_rank`
- `action_type`
- `parameter_name`
- `original_value`
- `recommended_value`
- `expected_cashflow_delta`
- `expected_post_action_cashflow`
- `meets_buffer`
- `created_at`

Suggested `action_type` values:

- `delay_capex`
- `reduce_outflows`
- `adjust_repayment`
- `other`

Notes:

- these are recommendation records, not committed financial plan mutations

## Relationship Summary

High-level relationships:

- one `enterprise` has many `ingestion_sources`
- one `ingestion_source` can have many `ingestion_source_credentials`
- one `enterprise` has many `ingestion_runs`
- one `ingestion_run` can have zero or one `ingestion_upload`
- one `enterprise` has many `counterparties`
- one `enterprise` has many `financial_transactions`
- one `invoice_payment_allocations` row links one invoice transaction to one payment transaction
- one `enterprise` has many `monthly_cashflow_aggregates`
- one `enterprise` has many `static_financial_snapshots`
- one `enterprise` has many `forecast_runs`
- one `forecast_run` has many `forecast_run_periods`
- one `forecast_run` can have many `simulation_runs`
- one `simulation_run` can have many `simulation_scenarios`
- one `simulation_run` can have many `receivables_rankings`
- one `simulation_run` can have many `mitigation_recommendations`

## Initial Constraints and Indexing

### Candidate uniqueness constraints

- `enterprises.external_key`
- `ingestion_sources (enterprise_id, source_key)` for active sources
- `counterparties (enterprise_id, external_key)`
- `financial_transactions (ingestion_source_id, source_record_id)` where source record IDs are reliable
- `monthly_cashflow_aggregates (enterprise_id, period_start, period_end)`
- `counterparty_monthly_receivables (enterprise_id, counterparty_id, period_start, period_end)`
- `static_financial_snapshots (enterprise_id, snapshot_date)`

### Important indexes

- `financial_transactions (enterprise_id, transaction_date)`
- `financial_transactions (enterprise_id, counterparty_id, transaction_date)`
- `financial_transactions (ingestion_run_id)`
- `monthly_cashflow_aggregates (enterprise_id, period_start)`
- `static_financial_snapshots (enterprise_id, snapshot_date desc)`
- `forecast_runs (enterprise_id, created_at desc)`
- `simulation_runs (enterprise_id, created_at desc)`

## Draft Data Type Direction

Suggested direction:

- use UUID primary keys unless there is a strong reason not to
- use `NUMERIC` for financial amounts rather than floating-point columns
- use timezone-aware timestamps for operational events
- use database enums for constrained categorical fields

## Resolved Design Decisions

1. `financial_transactions` should remain purely normalized and atomic.
   Invoice/payment application is represented by the separate
   `invoice_payment_allocations` table so receivables can determine partial
   payment status without changing the normalized transaction records.
2. `monthly_cashflow_aggregates` should remain enterprise-level only.
   On-demand reconstruction from raw transactions adds unnecessary complexity for this project and is not the preferred design.
3. `counterparty_monthly_receivables` is enough.
   A separate outstanding receivables table is not needed.
4. Static financial snapshots should support both source-derived and manually entered or adjusted records.
5. Use a hybrid approach for simulation patches.
   Keep summary and query-critical fields in columns, and store scenario-specific input modifications in JSON.
6. Model and artifact version metadata should live directly on `forecast_runs`.
   A separate `model_artifacts` table is not needed.
7. `currency_code` text is enough.
   Valid currency codes should be enforced through application-side validation before persistence rather than a dedicated currencies reference table.
8. Ingestion credentials and secrets should be represented in schema through persisted connection-state records.
   Environment-only configuration is not sufficient for enterprise-specific automated ingestion.
