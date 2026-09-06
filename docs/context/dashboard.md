# Dashboard Surface

## Purpose

The dashboard is the finance-user surface for the platform. It consumes the
enterprise-scoped FastAPI contract and turns forecast and simulation records into a
progressive decision workflow: establish the current position, inspect the baseline,
test financial sensitivity, investigate receivables, consider mitigation, and manage
input data.

## Views

### Overview

The overview presents the latest projected net cash flow, its relationship to the
solvency buffer, a compact historical/forecast chart, the leading observation driver,
and links to the next analytical steps. If data exists but no forecast has been run,
the page can initiate the first baseline automatically; otherwise it directs the user
to connect data.

### Forecast

The forecast workspace accepts a target range and creates an ad-hoc baseline. It
shows historical net cash movement, the predicted point, expected inflows and outflows,
buffer status, observed drivers, cautious narrative observations, model provenance,
and forecast-run history.

### Health

The health workspace submits financial-health sensitivity profiles and compares the
baseline with persisted scenarios. It combines the rule-based health score and status
with the corresponding model-predicted cash-flow movement, making trade-offs visible
without presenting the scenario as a guaranteed outcome.

### Receivables

The receivables workspace filters customer balances, displays supporting invoice and
payment records, and uses trapped-liquidity simulations to rank collection
opportunities. A user can select a customer and preview how an assumed delay changes
modeled cash flow. The page labels estimates as decision support rather than confirmed
collection outcomes.

### Planning

The planning workspace requests conservative, standard, or stress mitigation profiles
when the baseline is below its buffer. It displays only model-evaluated actions that
restore the selected buffer, including original and recommended values, expected
improvement, post-action cash flow, and priority.

### Data

The data workspace creates, edits, and deactivates ingestion sources; manages ERPNext
credential metadata and rotation; requests synchronization; uploads CSV/XLSX files;
and presents current processing status and paginated ingestion history. Secret values
are write-only from the normal response contract.

## Frontend architecture

React Router defines the six top-level routes under a shared application layout.
Enterprise context is provided once and consumed through focused hooks. Resource hooks
wrap API calls and expose loading, error, refresh, and mutation states. Feature-level
adapters translate generated API contracts into presentation-specific view models.

The API client uses generated TypeScript types produced from FastAPI's OpenAPI schema.
Small aliases in `api/contracts.ts` keep components readable while avoiding a separate
handwritten copy of backend payloads.

## Presentation and interaction principles

- Plain finance language leads; model terms and artifact versions remain supporting
  evidence.
- Risk and buffer states use text as well as color.
- Responsive components preserve the analytical hierarchy on smaller screens.
- Loading skeletons, resource errors, inline mutation errors, empty states, and retry
  actions are explicit.
- Currency and date formatting are centralized.
- Simulations remain visually and semantically distinct from observed financial facts.
- Recommendations invite review; they do not imply automatic execution.

The dashboard is an executive decision-support interface, not a training console or a
replacement for professional financial judgment.
