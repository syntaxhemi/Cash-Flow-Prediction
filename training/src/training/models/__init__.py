"""Training model definitions."""

from training.models.forecasting import (
    TemporalStaticDataset,
    train_model,
)

__all__ = ['TemporalStaticDataset', 'train_model']
