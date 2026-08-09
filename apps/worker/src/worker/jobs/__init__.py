"""Worker jobs package."""

from worker.jobs.ingestion import run_ingestion_consumer

__all__ = ['run_ingestion_consumer']
