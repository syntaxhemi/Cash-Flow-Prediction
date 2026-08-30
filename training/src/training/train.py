"""Command-line orchestration for the canonical cash flow training pipeline."""

import argparse
import random
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
from sklearn.preprocessing import StandardScaler

from training.artifacts import prepare_output_directory, save_training_artifacts
from training.config import InputFormat, TrainingConfig, load_config
from training.data import load_datasets
from training.features import build_sequences, prepare_datasets
from training.models import train_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Train the cash flow forecasting model.'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=Path('training/configs/default.yaml'),
        help='Path to the YAML configuration file.',
    )
    parser.add_argument(
        '--no-gpu',
        action='store_true',
        help='Force CPU training even when CUDA is available.',
    )
    parser.add_argument(
        '--input-format',
        choices=('raw', 'processed'),
        default=None,
        help='Override the configured input format for this run.',
    )
    parser.add_argument(
        '--run-name',
        default=None,
        help='Override the artifact run name for this run.',
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=None,
        help='Override the configured number of training epochs.',
    )
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=None,
        help='Override the configured learning rate.',
    )
    return parser.parse_args()


def set_random_seeds(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _split_by_time(data: object, test_quantile: float) -> tuple[np.ndarray, np.ndarray]:
    months = np.asarray(data)
    cutoff = np.quantile(
        months.astype('datetime64[ns]').astype(np.int64), test_quantile
    )
    return months.astype('datetime64[ns]').astype(np.int64) <= cutoff, months.astype(
        'datetime64[ns]'
    ).astype(np.int64) > cutoff


def train_pipeline(
    config: TrainingConfig,
    use_gpu: bool = True,
    input_format: InputFormat | None = None,
    run_name: str | None = None,
    epochs: int | None = None,
    learning_rate: float | None = None,
) -> Path:
    """Run preprocessing, training, evaluation, and artifact persistence.

    Args:
        config: Training configuration loaded from YAML.
        use_gpu: Whether CUDA may be used when it is available.
        input_format: Optional per-run override for the configured input format.
        run_name: Optional artifact run-name override.
        epochs: Optional training epoch override.
        learning_rate: Optional learning-rate override.

    Returns:
        Directory containing the generated training artifacts.

    Raises:
        FileNotFoundError: If a configured input dataset is missing.
        ValueError: If preprocessing or the chronological split cannot produce a
            valid training and validation set.
    """
    if input_format is not None:
        config = replace(config, data=replace(config.data, input_format=input_format))
    model_config = config.model
    if epochs is not None:
        model_config = replace(model_config, epochs=epochs)
    if learning_rate is not None:
        model_config = replace(model_config, learning_rate=learning_rate)
    if model_config != config.model:
        config = replace(config, model=model_config)
    if run_name is not None:
        config = replace(config, artifacts=replace(config.artifacts, run_name=run_name))
    set_random_seeds(config.split.random_state)
    datasets = load_datasets(config.data)
    prepared = prepare_datasets(datasets, input_format=config.data.input_format)
    sequence_data = build_sequences(prepared.temporal, prepared.static, config.features)
    train_mask, validation_mask = _split_by_time(
        sequence_data.label_months, config.split.test_quantile
    )

    if not train_mask.any() or not validation_mask.any():
        raise ValueError(
            'The temporal split must produce both training and validation rows.'
        )

    temporal_scaler = StandardScaler()
    static_scaler = StandardScaler()

    sequence_train = sequence_data.sequences[train_mask]
    sequence_validation = sequence_data.sequences[validation_mask]

    static_train = sequence_data.static[train_mask]
    static_validation = sequence_data.static[validation_mask]

    temporal_scaler.fit(sequence_train.reshape(-1, sequence_train.shape[2]))
    sequence_train_scaled = temporal_scaler.transform(
        sequence_train.reshape(-1, sequence_train.shape[2])
    ).reshape(sequence_train.shape)
    sequence_validation_scaled = temporal_scaler.transform(
        sequence_validation.reshape(-1, sequence_validation.shape[2])
    ).reshape(sequence_validation.shape)

    static_train_scaled = static_scaler.fit_transform(static_train)
    static_validation_scaled = static_scaler.transform(static_validation)
    labels_train = sequence_data.labels[train_mask]
    labels_validation = sequence_data.labels[validation_mask]
    target_scaler = StandardScaler() if config.model.target_scaling else None
    if target_scaler is not None:
        labels_train_scaled = target_scaler.fit_transform(
            labels_train.reshape(-1, 1)
        ).reshape(-1)
        labels_validation_scaled = target_scaler.transform(
            labels_validation.reshape(-1, 1)
        ).reshape(-1)
        target_center = float(target_scaler.mean_[0])
        target_scale = float(target_scaler.scale_[0])
    else:
        labels_train_scaled = labels_train
        labels_validation_scaled = labels_validation
        target_center = 0.0
        target_scale = 1.0

    result = train_model(
        sequence_train_scaled,
        static_train_scaled,
        labels_train_scaled,
        sequence_validation_scaled,
        static_validation_scaled,
        labels_validation_scaled,
        config.model,
        use_gpu=use_gpu,
        target_center=target_center,
        target_scale=target_scale,
    )
    best_history_index = result.best_epoch - 1
    best_validation_loss = result.validation_losses[best_history_index]
    best_validation_mae = result.validation_maes[best_history_index]
    run_directory = prepare_output_directory(
        config.artifacts.output_dir, config.artifacts.run_name
    )
    metrics = {
        'dataset_rows': {name: len(frame) for name, frame in datasets.items()},
        'temporal_rows': len(prepared.temporal),
        'sequence_samples': len(sequence_data.labels),
        'train_samples': int(train_mask.sum()),
        'validation_samples': int(validation_mask.sum()),
        'temporal_features': config.features.temporal_features,
        'static_features': config.features.static_features,
        'device': result.device,
        'best_epoch': result.best_epoch,
        'train_loss_history': result.train_losses,
        'validation_loss_history': result.validation_losses,
        'validation_mae_history': result.validation_maes,
        'best_validation_loss': best_validation_loss,
        'best_validation_mae': best_validation_mae,
        'last_validation_loss': result.validation_losses[-1],
        'last_validation_mae': result.validation_maes[-1],
        'final_validation_loss': best_validation_loss,
        'final_validation_mae': best_validation_mae,
        'input_format': config.data.input_format,
    }
    artifact_files = {
        'model': 'model.pth',
        'temporal_scaler': 'temporal_scaler.pkl',
        'static_scaler': 'static_scaler.pkl',
        'metrics': 'metrics.json',
        'metadata': 'artifact_metadata.json',
        'config_snapshot': 'config.snapshot.yaml',
    }
    if target_scaler is not None:
        artifact_files['target_scaler'] = 'target_scaler.pkl'
    metadata = {
        'model_version': config.artifacts.run_name,
        'artifact_version': 1,
        'training_run_name': config.artifacts.run_name,
        'created_at': datetime.now(UTC).isoformat(),
        'sequence_length': config.features.sequence_length,
        'temporal_features': config.features.temporal_features,
        'static_features': config.features.static_features,
        'label_column': config.features.label_column,
        'sequence_input_size': len(config.features.temporal_features),
        'static_input_size': len(config.features.static_features),
        'random_state': config.split.random_state,
        'input_format': config.data.input_format,
        'target_scaling': 'standard' if target_scaler is not None else 'none',
        'artifact_files': artifact_files,
    }
    save_training_artifacts(
        run_directory,
        config,
        result.model.state_dict(),
        temporal_scaler,
        static_scaler,
        target_scaler,
        metrics,
        metadata,
    )
    return run_directory


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    run_directory = train_pipeline(
        config,
        use_gpu=not args.no_gpu,
        input_format=args.input_format,
        run_name=args.run_name,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
    )
    print(f'Training artifacts written to: {run_directory}')


if __name__ == '__main__':
    main()
