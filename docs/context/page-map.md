# Dashboard Page Map

## Purpose

This document defines the primary dashboard pages, their responsibilities, and the
main workflows they contain. It is the page-level source of truth for dashboard
implementation.

The dashboard is an executive decision-support application for cash-flow forecasting,
bounded simulations, receivables analysis, and financial-data ingestion.

## Primary Navigation

```text
Overview · Forecast · Health · Receivables · Planning · Data
```

All six pages are first-class application areas. `Data` is not an administrative-only
settings page because connecting a source or uploading a file is required before the
application can produce a meaningful forecast.

## Pages

### Overview

The executive starting point. It answers the expected cash position, buffer status,
main driver, and next action in one coherent reading flow.

Includes:

- current predicted net cash flow
- buffer status and interpretation
- historical and baseline forecast trend
- primary risk or opportunity driver
- featured recommended next action
- quieter secondary actions
- freshness and source context

Flow: `Current position -> forecast trend -> driver -> recommended next action`

### Forecast

The detailed baseline forecast view. It explains the forecast and the financial data
context behind it.

Includes:

- forecast horizon and selected period
- historical values and baseline forecast
- uncertainty range when available
- solvency buffer comparison
- historical-to-forecast boundary
- input-period and source freshness context
- forecast-run history or selected snapshot

### Health

The bounded health and sensitivity view. This is model-driven decision support, not a
formal covenant-compliance engine.

Includes:

- baseline forecast health
- selected financial features or assumptions
- bounded scenario controls
- baseline versus simulated result
- directional health delta
- buffer impact
- assumptions and modeled-result disclosure

### Receivables

The trapped-liquidity and counterparty-impact view. It explains which receivables most
affect the modeled cash-flow outlook.

Includes:

- ranked counterparties
- outstanding amount
- payment behavior or delay indicators
- predicted cash-flow delta
- modeled trapped-liquidity estimate
- impact priority
- counterparty detail and supporting records
- drill-down into payment-delay simulation

### Planning

The scenario and mitigation workspace. It presents bounded options without implying
that any financial action has been committed.

Includes:

- recommended mitigation actions
- proposed scenario inputs
- original and adjusted values
- expected cash-flow delta
- post-scenario cash flow
- buffer status after the scenario
- baseline versus scenario comparison
- modeled-result and draft-recommendation labeling
- links back to the affected driver or receivable

### Data

The source and ingestion application flow. It is a primary page because forecasting
depends on connected or uploaded financial data.

Includes:

- configured source list
- create and edit source flow
- ERPNext connection setup
- sensitive credential and key entry
- CSV and XLSX upload flow
- file validation and data-preview state
- ingestion run status and history
- processing errors and recovery guidance
- synchronization freshness
- normalized-record processing summary
- source activation, deactivation, and deletion controls

## First-Run Data Flow

When no usable source exists, the application should guide the user through setup
rather than showing an empty executive dashboard:

```text
Choose source
-> connect ERPNext or upload CSV/XLSX
-> provide required source details
-> validate source or file
-> process and normalize records
-> confirm source readiness
-> run the first forecast
```

The Overview empty state should direct the user to `Data` and explain why a forecast is
not yet available.

## Shared Page Requirements

Every page should preserve:

- current enterprise context where it supports the page workflow; the detached
  breadcrumb-style context row is an Overview-only pattern
- source freshness where relevant
- explicit modeled-versus-recorded labeling
- accessible loading, empty, error, and unavailable states
- responsive behavior consistent with the design system
- progressive disclosure for relevant source records and business context

Model versions, artifact identifiers, and other runtime diagnostics are not dashboard
content. They belong in backend logs, operator diagnostics, or development tooling.

## Naming Decisions

- Use **Health** in user-facing navigation instead of `Covenant Health`.
- Use **Planning** for mitigation and scenario workflows.
- Use **Data** as the primary navigation label; the page heading may use
  **Data & Ingestion** when more explanatory text is appropriate.
