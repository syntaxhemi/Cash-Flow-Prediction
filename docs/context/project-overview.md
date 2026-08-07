# Project Overview

## Purpose

This project is a final-year engineering platform build around an existing applied research model for enterprise cash flow forecasting.

The LSTM-based forecasting foundation already exists conceptually in the research paper. The remaining work is to build a credible enterprise-style platform around that model theory:

- automated financial data ingestion
- data persistence and feature preparation
- forecasting and simulation APIs
- decision-support workflows
- executive dashboarding
- reproducible local deployment

## What This Project Is

This is:

- a greenfield platform build
- a Docker Compose-first system
- a technically credible enterprise workflow demonstration
- a software architecture project built around an applied ML forecasting core

## What This Project Is Not

This is not:

- a production rollout
- a large microservice estate
- a cloud-dependent platform
- a continuation of the `~legacy` wrapper implementation

## Scope Positioning

The target is an enterprise-style platform that is academically defensible and practical to demonstrate locally.

The expected balance is:

- realistic architecture boundaries
- strong connection to the research model
- enough automation to justify enterprise positioning
- restrained operational complexity

## Primary Goals

- package the research model into a reusable forecasting component
- ingest enterprise accounting data continuously rather than only through manual forms
- persist normalized financial records as the system of record
- produce baseline and simulation-based liquidity forecasts
- expose executive-facing insights through a dashboard
- demonstrate mitigation-oriented planning workflows around predicted cash deficits

## Non-Goals

- broad ERP/accounting connector coverage
- production-grade resilience, scale, and compliance depth
- full autonomous financial decisioning
- rewriting or extending `~legacy` as the new system base

## Reference Documents

- [research-paper.pdf](../reference/research-paper.pdf)
- [prd.pdf](../reference/prd.pdf)

## Current High-Level Stack Direction

- frontend: React + Vite dashboard
- backend API: FastAPI
- orchestration worker: Python async worker
- database: PostgreSQL
- queue/cache: Redis
- packaging: Docker Compose
- Python tooling: Python 3.13 + `uv`

## Important Working Assumptions

- `~legacy` is reference only
- the research paper is the source of truth for model assumptions
- the PRD is the source of truth for platform direction, but not every implementation detail in it should be followed literally
- one automated ingestion integration is required for architectural credibility
- ERPNext is the current preferred primary ingestion target because it is open source, practical for local Compose-based demos, and aligns with the project constraints
- CSV and Excel ingestion remain required as fallback import paths
