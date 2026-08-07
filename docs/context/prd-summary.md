# PRD Summary

## Purpose

This document interprets the PRD in implementation terms and separates strong features from overextended ones.

## PRD Direction

The PRD aims to transform a basic input-to-output model wrapper into an enterprise financial management platform centered on derived insights.

The most important themes in the PRD are:

- automated ingestion
- persistent financial records
- simulation-driven executive dashboards
- receivables visibility
- liquidity mitigation guidance

## Features Interpreted for This Project

### 1. Automated Data Ingestion

This is in scope and should be treated as a first-class architectural requirement.

Reason:

- the platform claims continuous forecasting
- that claim is weak if the primary story is still manual spreadsheet upload
- at least one real integration is needed for academic credibility

Current preferred interpretation:

- primary automated integration: ERPNext
- fallback ingestion: CSV and Excel uploads
- optional later recognition connector: QuickBooks sandbox if time permits

### 2. Covenant Health Dashboard

This is in scope and should be reframed as a simulation and sensitivity dashboard rather than a compliance engine.

Strong interpretation:

- show baseline next-interval forecast
- vary selected static features within bounded ranges
- compare baseline and simulated outputs
- present a derived health delta score or directional improvement indicator

Important caveat:

- this is a model-driven decision-support view, not a literal covenant-monitoring system

### 3. Receivables Optimization Engine

This is strongly in scope.

Best interpretation:

- use payment-delay counterfactual simulation
- estimate forecast improvement if specific debtors paid on time
- rank debtors by predicted negative liquidity impact

Important caveat:

- treat outputs as modeled trapped-liquidity estimates, not exact ground truth

### 4. Liquidity Crisis Router

This is in scope if implemented as bounded recommendation logic rather than autonomous optimization.

Best interpretation:

- detect when predicted cash flow breaches a solvency threshold
- run constrained scenario permutations on discretionary outflows
- recommend recovery actions that improve the forecast toward the buffer

Important caveat:

- do not commit actions directly into live operational systems in the initial project scope

## PRD Elements That Should Be Softened

- "autonomous" routing should become deterministic recommendation orchestration
- "exact" trapped-liquidity language should become modeled estimate language
- direct budget mutation should become draft simulation output
- cloud-like operational breadth should be reduced to a local Compose-first delivery

## MVP Feature Set Derived from the PRD

The strongest MVP for this project is:

- ERP/accounting ingestion through one real automated connector
- fallback CSV/Excel imports
- normalized financial ledger persistence
- baseline cash flow forecast API
- health delta simulation API
- trapped liquidity simulation API
- liquidity mitigation recommendation API
- dashboard for executive insight and planning

## Important Product Constraints

- connector breadth is less important than one credible end-to-end integration
- workflow clarity is more important than heavy automation
- explainability is more important than advanced optimization sophistication
- local reproducibility is mandatory
