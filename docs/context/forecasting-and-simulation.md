# Forecasting and Simulation

## Baseline forecast contract

A baseline run predicts net cash flow for one target period. It requires exactly six
complete calendar-month aggregates immediately before that period and the latest
static financial snapshot available by the target end date. Missing months, missing
static context, an invalid date range, or a model-input mismatch rejects the run rather
than filling hidden defaults for temporal history.

The response and persistence record:

- predicted net cash flow
- the user-selected solvency buffer
- buffer gap (`prediction - buffer`)
- run status and timestamps
- model and artifact versions
- links to the six aggregate inputs and static snapshot
- expected inflows and outflows from the transaction ledger
- observed input drivers and cautious trend statements

The forecast represents net cash movement for the next period. It is not a bank-balance
forecast and does not execute financial actions.

## Runtime model

The neural component combines two branches:

```text
6 x 5 temporal sequence -> LSTM(96) -> Dense(48) --+
                                                       -> Fusion Dense(48) -> output
10 static features ----------------> Dense(48) -------+
```

ReLU activations and dropout are used in the dense blocks. Architecture values are
loaded from the committed artifact configuration rather than duplicated in the API.

### Temporal inputs

- total invoice amount
- accumulated payment delay
- monthly repayment
- total inflows
- total outflows

### Static inputs

- capital expenditure and cost of goods sold
- current assets and liabilities
- fixed assets and long-term liabilities
- credit score and failure score
- debt-to-revenue ratio
- missed-payment count

The persisted feature ordering in artifact metadata is authoritative at runtime.

## Stabilized inference

The baseline artifact uses a hybrid estimate:

```text
prediction = 0.675 * neural prediction
           + 0.325 * mean six-month net cash flow
```

This preserves the learned temporal/static relationship while anchoring the result to
the enterprise's recent scale. If any standardized model input exceeds the configured
absolute z-score guard of `200`, the neural weight becomes zero and inference returns
the persistence estimate. This is an explicit out-of-distribution safeguard, not a
confidence interval.

Monetary inputs are converted into the artifact's GBP training units before scaling.
The committed INR mapping divides INR amounts by `100` and converts the prediction
back afterward. Delay, ratio, score, and count features are not converted.

## Counterfactual evaluation

Simulation services reconstruct the baseline inputs from the forecast's persisted
period links and static snapshot. They require the currently loaded artifact to match
the forecast's model and artifact versions. Each scenario applies a bounded patch,
runs the same preparation and inference service, and records:

- patched inputs
- counterfactual prediction
- difference from the baseline
- whether the result meets the original solvency buffer

The output answers "what does this model predict under these changed inputs?" It does
not establish that changing a business variable will cause the predicted outcome.

## Financial-health sensitivity

Health simulation varies selected static financial features through conservative,
standard, or stress profiles, or through validated non-negative custom targets. The
domain layer calculates a separate zero-to-100 health score from liquidity, leverage,
credit, failure, and payment indicators and assigns a health status.

For each scenario the platform stores both cash-flow effects and health-score effects.
This separates an interpretable rule-based financial-health summary from the learned
cash-flow model while allowing the dashboard to compare them in one view.

## Trapped-liquidity analysis

Receivables analysis selects customer aggregates inside the forecast window. For each
candidate it identifies a representative high-outstanding period, derives payment
delay from settled history or amount-weighted overdue invoices, and reduces that
period's modeled inflow by a bounded within-month amount:

```text
at-risk amount = min(outstanding amount, invoice amount)
delay fraction = min(1, delay days / 30)
inflow reduction = min(baseline inflows, at-risk amount * delay fraction)
```

The counterfactual is evaluated by the model and customers are ranked by simulated
cash-flow delta. The summary reports modeled trapped liquidity as the sum of positive
recoverable deltas. A user can also preview a selected payment-delay assumption.

The ranking is a collection-prioritization aid, not a prediction that a customer will
pay or a mandate to contact them.

## Liquidity mitigation

Mitigation is available only when a completed baseline forecast is below its solvency
buffer. Server-controlled profiles generate bounded candidates that can:

- delay capital expenditure in the latest input period
- reduce latest-period total outflows
- adjust latest-period loan repayment and its corresponding outflow

Conservative, standard, and stress profiles control the reduction factors. Every
candidate is evaluated independently against the baseline. Only options that meet the
buffer are retained, ranked by improvement, and limited to three recommendations.

Recommendations are persisted separately from transactions. The platform neither
combines interventions automatically nor mutates the financial plan.

## Interpretation boundary

The forecast and all three simulations are model-based decision support. Suitable
paper claims concern system integration, repeatable inference, transparent input
provenance, and bounded scenario exploration. Claims of causal impact, guaranteed
liquidity recovery, or autonomous optimization are not supported by this design.
