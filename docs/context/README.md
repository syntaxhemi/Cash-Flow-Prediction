# Project Documentation

This directory contains the maintained documentation for the implemented Cash Flow
Prediction platform. The collection describes the system as it exists and records
the engineering and experimental evidence needed to explain it in an applied
engineering research paper.

## Reading order

1. [system-overview.md](./system-overview.md): problem, scope, capabilities, and
   research contribution
2. [architecture.md](./architecture.md): runtime topology, module ownership, and
   principal workflows
3. [data-and-ingestion.md](./data-and-ingestion.md): canonical accounting model,
   ingestion adapters, aggregation, and persistence
4. [forecasting-and-simulation.md](./forecasting-and-simulation.md): inference,
   health analysis, receivables analysis, and mitigation logic
5. [training-and-evaluation.md](./training-and-evaluation.md): dataset preparation,
   model design, evaluation, and artifact contract
6. [dashboard.md](./dashboard.md): executive decision-support experience and API
   integration
7. [reproducibility.md](./reproducibility.md): setup, seeding, validation, and
   deployment properties

## Evidence boundary

These documents distinguish implemented behavior from project assumptions and
experimental limitations. Exact model results come from the committed baseline
artifact metadata and metrics. Product requirements and the source study remain in
`docs/reference`; the implementation is the authority for current system behavior.

The collection is descriptive documentation, not a task tracker. Architecture or
behavior changes should update the relevant document in the same change.
