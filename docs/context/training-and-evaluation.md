# Training and Evaluation

## Ownership and execution

Canonical training code lives in `training/src/training`; the notebook is exploratory.
The supported entrypoint is:

```powershell
uv run --package cash-flow-training train-model `
  --config training/configs/baseline.yaml --no-gpu
```

Configuration controls source files, input format, split, random seed, architecture,
optimization, feature order, persistence blend, support guard, and currency metadata.
Each run writes to an immutable directory under `training/artifacts/runs`.

## Source data

The experiment uses six SME data tables inherited from the applied research work:

| Table | Baseline rows | Role |
| --- | ---: | --- |
| Account receivable | 79,648 | invoice values and payment timing |
| Businesses | 974 | company financial attributes |
| Credit account history | 1,421 | fallback inflow/outflow relationship |
| Credit card history | 353 | missed-payment indicators |
| Credit rating | 900 | credit, failure, and leverage indicators |
| Loan | 90 | repayment history |

The pipeline accepts either raw research files or processed notebook-compatible files.
Credit score is normalized from `0-1000` and failure score from `0-100` into the
runtime's `0-1` convention.

## Feature preparation

Receivables are aggregated by company and month into invoice total and accumulated
payment delay. Loan records provide monthly repayment. Inflows begin with invoice
totals and outflows begin with repayments. When a month has no repayment-derived
outflow, a dataset-level pay-out/pay-in ratio from credit-account history supplies the
fallback estimate.

Credit-account history has no monthly timestamp, so its company totals are not copied
into every temporal row. Static business, rating, and credit-card attributes are
joined by company registration number and missing static values are filled with zero.

For every company with sufficient history, a sliding window uses six months of five
temporal features to predict the seventh month's net cash flow. The same company's ten
static features accompany each window. The prepared baseline contains 10,593 monthly
rows and 4,851 sequence samples.

## Split and leakage controls

The configured test quantile is `0.80`: samples before the 80th percentile of label
month form the training set and later samples form the held-out validation set. This
produced 3,935 training and 916 validation samples. Temporal and static standardizers
are fitted only on training data and then applied to validation and runtime data.

The split is chronological by prediction month, which is appropriate for forecasting
and avoids randomly mixing later economic observations into the training partition.
Sequence construction uses only months preceding each label. The random seed is `32`.

The current experiment has a training/validation split but no independent final test
set or rolling-origin evaluation. Results should therefore be reported as held-out
validation evidence, not as a final estimate of generalization.

## Model and optimization

The model fuses an LSTM representation of the temporal sequence with a dense
representation of static features. The baseline uses:

- LSTM hidden width `96`
- branch and fusion width `48`
- dropout `0.40`
- Smooth L1 loss with beta `1.0`
- AdamW, learning rate `0.0001`, weight decay `0.001`
- plateau learning-rate reduction and gradient clipping at `1.0`
- maximum 50 epochs and early-stopping patience of five

The best checkpoint is selected using validation mean absolute error. Target scaling
is disabled in the promoted artifact.

## Baselines and reported results

The neural output is evaluated beside a six-month mean persistence baseline and their
configured blend. For the committed artifact version 3:

| Measure | Held-out validation MAE |
| --- | ---: |
| Neural model | 33.5069 |
| Persistence baseline | 40.5298 |
| Blended forecast | 32.3725 |

The best checkpoint occurred at epoch 16. The blend improves validation MAE by about
20.1% relative to persistence and 3.4% relative to the neural component alone. These
figures are in the research dataset's target units and come directly from the
committed `metrics.json`.

The run records zero validation cases crossing the out-of-distribution support guard.
That observation validates consistency on this split; it does not establish a
calibrated uncertainty estimate.

## Artifact contract

The baseline run contains:

- `model.pth`
- `temporal_scaler.pkl`
- `static_scaler.pkl`
- `metrics.json`
- `artifact_metadata.json`
- `config.snapshot.yaml`

Metadata version 3 records feature order and dimensions, sequence length, model
architecture, target-scaling mode, blend weight and strategy, z-score guard, random
seed, input format, training currency, currency conversion constants, and artifact
filenames. The loader validates metadata and reconstructs the runtime model before
loading weights.

Training and serving share the model class from `shared/ml`, reducing architectural
drift. Runtime preparation selects values in metadata-declared order, uses the fitted
scalers, reverses optional target scaling, and returns model and artifact versions with
every prediction.

## Experimental limitations

- The dataset covers a particular UK SME sample and historical period.
- The GBP denomination is a project assumption derived from dataset context.
- The fixed INR conversion is a model-reference normalization, not exchange-rate
  modeling.
- The current evaluation reports MAE only; it has no probabilistic interval, error by
  industry, stress-period analysis, or statistical significance test.
- The blended weight and support threshold are configured engineering choices and
  have not been tuned through a documented broad search.
- Operational demo data is deterministic and designed for workflow coverage, not an
  additional independent evaluation population.

These limits should appear alongside quantitative claims in an applied engineering
paper. The strongest evidence is that the implemented hybrid improves held-out MAE on
the documented split and can be reproduced from committed configuration and artifacts.
