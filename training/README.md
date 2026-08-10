# Training Pipeline

Canonical training code lives under `training/src/training`.

Notebooks under `training/notebooks` are exploratory references and are not intended to be the long-term execution path.

## Run from the repository root

Place the six source CSV files under `training/artifacts/input`, then run:

```powershell
uv run --package cash-flow-training train-model --config training/configs/default.yaml
```

For CPU-only local runs:

```powershell
uv run --package cash-flow-training train-model --config training/configs/default.yaml --no-gpu
```

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

Each run writes model weights, both fitted scalers, metrics, artifact metadata, and a
configuration snapshot to `training/artifacts/runs/<run_name>/`.
