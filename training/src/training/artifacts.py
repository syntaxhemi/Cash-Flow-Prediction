"""Persistence for reproducible training outputs."""

import json
import pickle
from pathlib import Path
from typing import Any

import torch
import yaml

from training.config import TrainingConfig, config_to_dict


def prepare_output_directory(output_dir: Path, run_name: str) -> Path:
    run_directory = output_dir / run_name
    run_directory.mkdir(parents=True, exist_ok=True)
    return run_directory


def save_pickle(path: Path, value: Any) -> None:
    with path.open('wb') as file_handle:
        pickle.dump(value, file_handle)


def save_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2), encoding='utf-8', newline='\n')


def save_training_artifacts(
    run_directory: Path,
    config: TrainingConfig,
    model_state: dict[str, Any],
    temporal_scaler: Any,
    static_scaler: Any,
    target_scaler: Any | None,
    metrics: dict[str, Any],
    metadata: dict[str, Any],
) -> None:
    """Persist model, feature scalers, target scaler, and run metadata.

    Args:
        run_directory: Directory receiving the artifact bundle.
        config: Configuration to serialize as a reproducibility snapshot.
        model_state: Model state dictionary.
        temporal_scaler: Fitted temporal feature scaler.
        static_scaler: Fitted static feature scaler.
        target_scaler: Fitted target scaler used during training.
        metrics: Training and validation metrics.
        metadata: Artifact contract and provenance metadata.
    """
    torch.save(model_state, run_directory / 'model.pth')
    save_pickle(run_directory / 'temporal_scaler.pkl', temporal_scaler)
    save_pickle(run_directory / 'static_scaler.pkl', static_scaler)
    if target_scaler is not None:
        save_pickle(run_directory / 'target_scaler.pkl', target_scaler)
    save_json(run_directory / 'metrics.json', metrics)
    save_json(run_directory / 'artifact_metadata.json', metadata)
    (run_directory / 'config.snapshot.yaml').write_text(
        yaml.safe_dump(config_to_dict(config), sort_keys=False),
        encoding='utf-8',
        newline='\n',
    )
