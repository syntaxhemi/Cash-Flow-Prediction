# Training Pipeline

Canonical training code lives under `training/src/training`.

Notebooks under `training/notebooks` are exploratory references and are not intended to be the long-term execution path.

## Run from the repository root

Place the six source CSV files under `training/artifacts/input`, then run:

```powershell
uv run --package cash-flow-training train-model --config training/configs/baseline.yaml
```

For CPU-only local runs:

```powershell
uv run --package cash-flow-training train-model --config training/configs/baseline.yaml --no-gpu
```

The baseline configuration points to the normalized inputs used by the current
experiments. For raw research CSV files, use a separate configuration with the raw
input format:

```powershell
uv run --package cash-flow-training train-model --config training/configs/baseline.yaml --input-format processed --no-gpu
```

The CLI flag overrides `data.input_format` in the YAML configuration. Both modes still
perform the final temporal aggregation, feature joins, scaling, and sequence-window
construction required for model training. Credit-account history is used only to
calculate the fallback outflow ratio because it has no monthly timestamp; its
company-level totals are not repeated into every temporal row.

## Configuration

Training configuration files should live under `training/configs`.

## Outputs

Training artifacts should be written under `training/artifacts`.

## Intended Pipeline Coverage

The training pipeline is expected to cover:

- dataset loading
- preprocessing and feature engineering
- scaler fitting
- model training
- artifact persistence
- metrics generation

Each run writes model weights, fitted temporal/static/target scalers, metrics, artifact
metadata, and a configuration snapshot to `training/artifacts/runs/<run_name>/`. The
target scaler is fitted on training labels only; runtime inference reverses it so API
predictions remain in original cash-flow units.
