# Training Pipeline

Canonical training code lives under `training/src/training`.

Notebooks under `training/notebooks` are exploratory references and are not intended to be the long-term execution path.

## Run from the repository root

Training entrypoints are not implemented yet. This package currently exists to establish the workspace structure for the future script-based pipeline.

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
