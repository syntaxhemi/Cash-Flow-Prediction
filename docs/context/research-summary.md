# Research Summary

## Purpose

This document summarizes the model-side constraints that should shape the platform architecture.

## Core Research Direction

The research paper proposes a hybrid forecasting framework for SME cash flow prediction based on:

- an LSTM branch for temporal financial sequences
- a dense branch for static organizational health indicators
- feature fusion for next-interval net cash flow prediction

The platform should therefore be built around a forecasting and simulation workflow, not a generic analytics shell.

## Problem Framing from the Paper

The paper argues that traditional methods such as ARIMA and moving averages do not adequately capture:

- non-linear volatility
- long-term dependencies
- combined temporal and static financial effects

The platform should preserve that framing in its architecture:

- time-series transaction history must be persisted
- static balance sheet and credit health features must be modeled separately
- inference must support combining both data families into one forecast

## Important Model Assumptions

### Inputs

The paper centers on two input families:

- temporal features such as invoice amounts, payment delays, inflows, outflows, and repayment behavior
- static features such as credit score, failure score, debt-to-revenue ratio, and asset/liability indicators

### Sequence Shape

The paper uses a 6-month sliding window for temporal modeling.

This has direct platform implications:

- ingestion must preserve chronological records
- the database and feature pipeline must support rolling-window reconstruction
- APIs should be able to build model-ready tensors from stored records

### Target

The predictive target is next-period net cash flow.

This means the platform's baseline forecasting interface should be framed around:

- next-month or next-interval net liquidity
- explicit distinction between baseline prediction and simulated prediction

## Training and Evaluation Notes

The paper describes:

- chronological train/test separation
- scaling and normalization
- early stopping
- MSE and MAE as primary evaluation indicators

The platform should reflect these as reproducibility concerns:

- scaler and artifact metadata must be versioned
- training logic should be scriptable and not notebook-only
- inference services should load explicit artifacts rather than infer runtime assumptions ad hoc

## What the Paper Directly Supports

The paper directly supports:

- baseline cash flow forecasting
- integration of temporal and static financial features
- simulation over model inputs to compare forecast outcomes
- sensitivity-style decision support

## What the Paper Does Not Fully Support

The paper does not fully justify:

- strong causal claims
- autonomous financial decision execution
- exact optimization guarantees
- broad enterprise process automation beyond forecast-driven decision support

These limits should shape how the platform is described:

- use terms such as simulation, scenario testing, sensitivity analysis, and recommendation
- avoid claiming exact trapped capital or provably optimal action plans

## Architectural Consequences

The research summary implies that the platform needs:

- durable financial data storage
- a canonical feature-preparation pipeline
- a reusable model-serving layer
- simulation endpoints for counterfactual runs
- model and scaler artifact versioning
- clear separation between training-time code and runtime inference code
