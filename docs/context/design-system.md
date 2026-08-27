# Cash Flow Design System

## Status

This is the initial design-system direction for the dashboard. It is intentionally
incomplete. The dashboard is an executive decision-support interface for cash-flow
forecasting and bounded financial simulations, so the system should favor clarity,
trust, and explainability over visual novelty.

The current visual reference is:

- [Desktop mockup](assets/desktop-mockup.png)
- [Mobile responsive mockup](assets/mobile-mockup.png)

The page responsibilities and navigation source of truth are documented in
[Dashboard Page Map](page-map.md).

## Product Design Idea

Functional product name: **Cash Flow**.

This is a temporary functional name, not the final product or brand name. The final
name should be selected after further product-positioning and naming discussions.

The interface turns financial signals into decisions:

```text
Observe signal -> inspect driver -> simulate option -> review recommendation
```

The design should feel:

- calm and trustworthy during normal operation
- analytical without looking like a data-science notebook
- clear enough for executive scanning
- visibly urgent when liquidity risk increases
- explicit about modeled estimates versus confirmed financial facts

The interface must not imply autonomous financial control. Forecasts, simulations,
and recommendations are decision-support outputs.

## Design Principles

### 1. Lead with the decision signal

Pages should answer the most important business question before exposing technical
detail. A user should quickly understand the expected cash position, buffer status,
main driver, and possible next action.

### 2. Preserve context around every number

Financial values should be accompanied by their period, currency, source, freshness,
and interpretation where relevant. A number without context is not an insight.

### 3. Separate fact, forecast, and simulation

The visual language must distinguish:

- recorded financial data
- baseline model forecasts
- counterfactual simulation results
- recommendations derived from simulations

### 4. Make uncertainty visible

Forecast values should not be presented with more certainty than the model supports.
Where confidence or an uncertainty range is available, it should be shown beside or
within the forecast visualization.

### 5. Use urgency carefully

Risk should be prominent when it matters, but the interface should not make every
negative value feel like a crisis. Use severity labels and supporting explanations,
not color alone.

### 6. Prefer progressive disclosure

The overview should remain compact. Detailed assumptions and source records should be
available through drill-downs, drawers, or detail sections rather than competing with
the primary signal. Model versions, artifact identifiers, and runtime diagnostics are
internal concerns and should not be shown in the dashboard.

## Visual Direction

The visual language is a light, editorial enterprise interface with chalk-like paper,
deep ink typography, a distinctive oxblood accent, muted plum scenario states, and
warm brass attention colors. The interface should feel seamless and contemporary,
with an English print-and-stationery character rather than a generic SaaS palette.

Avoid:

- neon colors
- crypto or trading-terminal styling
- excessive glassmorphism
- full-screen dark themes
- decorative illustrations competing with financial data
- dense dashboards with every metric visible at once

## Color Tokens

These are initial values and may change after implementation and accessibility review.

### Foundation

| Token                | Value     | Use                                    |
| -------------------- | --------- | -------------------------------------- |
| `--color-ink`        | `#24211F` | Primary text and navigation            |
| `--color-text-muted` | `#766E69` | Supporting text and metadata           |
| `--color-canvas`     | `#F7F2EA` | Application background                 |
| `--color-surface`    | `#FFFDF8` | Featured surfaces and focused overlays |
| `--color-border`     | `#E7DED4` | Borders, dividers, and chart guides    |

### Semantic accents

| Token                  | Value     | Use                                      |
| ---------------------- | --------- | ---------------------------------------- |
| `--color-primary`      | `#9D2B2B` | Primary actions and forecast emphasis    |
| `--color-primary-soft` | `#F4E6E1` | Primary backgrounds and selected states  |
| `--color-simulation`   | `#705A6B` | Counterfactual and scenario workflows    |
| `--color-positive`     | `#39715A` | Improvement, healthy, above buffer       |
| `--color-warning`      | `#B47C2C` | Attention, thresholds, moderate severity |
| `--color-risk`         | `#B53D35` | Buffer breach and high-severity risk     |

Semantic colors must always be paired with text, icons, patterns, or position. Color
must not be the sole way a user identifies status.

## Typography

The selected type system is **Instrument Sans + Newsreader**.

`Instrument Sans` is the primary interface typeface. It should be used for
navigation, labels, tables, filters, chart legends, body copy, buttons, and financial
values. Its clean proportions keep dense financial information readable without
falling back to a generic system-sans appearance.

`Newsreader` is the restrained editorial display face. It should be used for selected
page titles, narrative callouts, and short interpretive statements. It should not be
used for navigation, metadata, chart axes, tables, or large collections of numbers.
This limited use gives the English editorial palette character without making the
dashboard feel traditional or slow to scan.

Technical metadata may use `IBM Plex Mono` sparingly for model versions, artifact
identifiers, and other genuinely technical values.

```css
:root {
    --font-ui: "Instrument Sans", sans-serif;
    --font-display: "Newsreader", serif;
    --font-mono: "IBM Plex Mono", monospace;
}
```

| Role                | Initial size |  Weight | Notes                                                  |
| ------------------- | -----------: | ------: | ------------------------------------------------------ |
| Page title          |    `24-28px` |     600 | `Instrument Sans`; keep the page entry point compact   |
| Section label       |    `11-13px` |     600 | `Instrument Sans`; uppercase only for compact eyebrows |
| Section title       |    `16-20px` |     600 | `Instrument Sans`; use sparingly for content grouping  |
| Editorial statement |    `20-24px` |     400 | `Newsreader`; one short narrative statement per view   |
| KPI value           |    `32-44px` | 500-600 | `Instrument Sans` with tabular numerals                |
| Body                |    `14-16px` |     400 | `Instrument Sans`; primary reading text                |
| Metadata            |    `12-13px` | 400-500 | `Instrument Sans`; source, freshness, timestamps       |
| Technical metadata  |    `12-13px` |     400 | `IBM Plex Mono` used sparingly                         |

Currency values, percentages, dates, and other repeated data should use Instrument
Sans with tabular numerals and consistent formatting. Units should not be separated
from their values in a way that makes scanning difficult. Newsreader should never be
used to compensate for weak hierarchy; spacing, scale, and grouping remain the
primary tools for structure.

## Spacing, Shape, and Elevation

Initial spacing direction:

- base unit: `4px`
- common spacing: `8px`, `12px`, `16px`, `24px`, `32px`
- component spacing: `12px` to `20px` within a content group
- section separation: `64px` to `96px` on desktop; `48px` to `72px` on mobile
- shell-to-content separation: `32px` to `40px` below the navbar; Overview may include an additional context row
- card radius: `16px`
- control radius: `8px`
- pill radius: `999px`
- default border: `1px solid var(--color-border)`
- shadows: subtle and reserved for raised surfaces or overlays

Use whitespace, alignment, and subtle separators as the primary grouping mechanisms.
Avoid a dense grid of equally weighted cards. Shadows should be nearly imperceptible
and reserved for overlays. Headings should establish hierarchy through position and
spacing before relying on scale.

## Application Shell

The desktop shell consists of:

- slim top navigation
- enterprise selector and page header
- data freshness indicator
- primary page action
- responsive main content area

Suggested navigation:

- Overview
- Forecast
- Covenant Health
- Receivables
- Mitigation
- Data & Ingestion

The header should expose the current enterprise, synchronization status, and a
contextual primary action such as `Run forecast` or `Create simulation`.

The Overview page may use a detached enterprise/freshness context row beneath the
navbar. Other pages should not repeat this row as breadcrumbs; they should begin
with their own page-specific heading and controls. Enterprise and freshness context
may still appear inline where it directly supports that page's workflow.

The navigation should collapse into a compact menu on smaller screens. A permanent
dark sidebar is not the default shell direction.

On mobile, the shell should preserve breathing space rather than compressing the
desktop header. Keep the context row visibly detached from the navbar, stack the
enterprise and freshness/action controls, and use a compact menu affordance.

## Information Architecture

### Overview

The overview answers:

1. What is the expected cash position?
2. Is it above or below the solvency buffer?
3. What is driving the risk or opportunity?
4. What action should be considered next?

Suggested content, in this order:

- current predicted net cash flow and buffer status
- cash-flow outlook trend
- key risk or opportunity signal
- recommended next actions
- supporting source and freshness metadata

The page should follow one coherent reading flow rather than presenting unrelated
cards at equal visual weight:

```text
Current position -> forecast trend -> signal/driver -> recommended next action
```

The Overview page should have one dominant narrative and no more than two visually
elevated surfaces above the fold. Supporting information should be expressed through
typography, alignment, annotations, separators, and progressive disclosure rather
than a grid of generic cards. Recommendations should use one featured next action,
followed by quieter secondary prompts in an open two-column arrangement; do not use a
table-like action list or three equal action cards.

The hierarchy should be legible without relying on oversized headings:

```text
compact eyebrow -> primary value -> interpretation -> visualization -> driver -> action
```

Use space, alignment, and restrained type scale to establish these levels. On mobile,
the primary cash-flow value is a supporting KPI, not a hero display; keep it around
`40-48px` and let the editorial statement and section spacing carry the emphasis.

### Forecast

The forecast view should provide the baseline forecast, the input period used, the
selected static snapshot, source freshness, and the buffer comparison. Model versions,
artifact identifiers, and runtime diagnostics remain outside the dashboard.

### Covenant Health

This is a bounded health and sensitivity view, not a compliance engine. It should
show baseline metrics, adjustable scenario inputs, scenario results, and directional
health deltas.

### Receivables

This view should rank counterparties by modeled liquidity impact. Outstanding amount,
payment behavior, predicted cash-flow delta, and priority should be visible together.

### Mitigation

This view should present bounded recommendations for improving the forecast toward
the solvency buffer. Recommendations are drafts for decision support and must not
imply that actions were committed to an accounting system.

### Data & Ingestion

This view should expose source status, latest synchronization or upload state,
record-processing summaries, errors, and freshness information.

## Core Components

The initial reusable component vocabulary is:

- `AppShell`
- `Navigation`
- `PageHeader`
- `EnterpriseSelector`
- `MetricBlock`
- `StatusBadge`
- `FreshnessIndicator`
- `ForecastChart`
- `BufferIndicator`
- `ScenarioPanel`
- `ScenarioComparison`
- `RankingList`
- `RecommendationSequence`
- `DataGrid`
- `Drawer`
- `Modal`
- `Toast`
- `LoadingState`
- `EmptyState`
- `ErrorState`

Every data-heavy component should have loading, empty, error, and unavailable states.

## Data Visualization Rules

### Cash-flow outlook

The primary forecast chart should use:

- historical values as a solid deep-ink line
- baseline forecast as a solid oxblood line
- solvency buffer as a dashed deep-ink guide with a clear label
- uncertainty as a translucent band when available
- a clear boundary between historical and forecast periods
- a highlighted breach interval when the forecast crosses the buffer

The chart should have a short adjacent interpretation, not require users to infer
the meaning from the legend alone.

### Simulation comparison

Simulation views should show:

- baseline as a neutral reference
- scenario result using the simulation accent
- signed delta from baseline
- direction and severity labels
- scenario assumptions beside the result

### Trapped liquidity ranking

Use a ranked horizontal bar chart or table. Rank by modeled cash-flow impact, not only
by outstanding amount. The minimum useful fields are counterparty, outstanding
amount, predicted delta, and priority.

### Mitigation recommendations

Show the proposed action, original value, recommended value, expected cash-flow delta,
post-action cash flow, and buffer status. Clearly label the result as modeled.

## Interaction and Content Rules

- Keep the executive summary visible before detailed controls.
- Let users drill down from KPIs into charts or source records.
- Keep simulation inputs beside their outputs.
- Preserve the baseline while comparing scenarios.
- Display model assumptions that materially affect a result.
- Use plain-language labels before technical field names.
- Prefer `Modeled impact`, `Forecast`, and `Recommendation` over claims of certainty.
- Use explicit freshness labels such as `Synced 8 min ago` and `As of ...`.

## Responsive Behavior

The primary target is desktop executive use, with tablet support and a designed mobile
experience.

- Desktop: slim top navigation, centered editorial canvas, and open multi-column briefing
- Tablet: compact navigation and reflowed editorial sections with preserved whitespace
- Mobile: compact top bar, single-column flow, readable chart, and vertically ordered actions

Charts should simplify labels and remain readable at narrow widths. Dense tables should
become focused record views or expandable details; do not squeeze desktop grids into a
mobile viewport.

## Accessibility Requirements

The dashboard should target WCAG 2.2 AA where practical.

- Meet contrast requirements for text and controls.
- Provide visible keyboard focus states.
- Support keyboard navigation through shell, filters, tables, and scenarios.
- Never communicate status through color alone.
- Provide text summaries for important charts.
- Label currency, units, date ranges, and time zones.
- Announce long-running forecast and simulation state changes appropriately.
- Respect `prefers-reduced-motion`.
- Ensure charts have useful fallback content when unavailable.

## Implementation Direction

The design system should initially be implemented with CSS custom properties and
small React components rather than introducing a large UI framework.

Suggested structure:

```text
apps/dashboard/src/
  components/
    layout/
    data-display/
    feedback/
    simulation/
  pages/
    Overview/
    Forecast/
    CovenantHealth/
    Receivables/
    Mitigation/
    DataIngestion/
  services/
  hooks/
  lib/
  styles/
    tokens.css
    globals.css
    utilities.css
```

The generated OpenAPI types should be consumed in the service layer. Presentation
components should receive view-oriented props rather than depending directly on raw
API response shapes.
