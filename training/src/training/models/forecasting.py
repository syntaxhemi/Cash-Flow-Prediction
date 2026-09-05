"""LSTM temporal/static fusion model and training loop."""

from dataclasses import dataclass

import numpy as np
import torch
from ml.models import RuntimeForecastModel, RuntimeModelConfig
from torch import nn, optim
from torch.utils.data import DataLoader, Dataset

from training.config import ModelConfig


class TemporalStaticDataset(Dataset[tuple[torch.Tensor, torch.Tensor, torch.Tensor]]):
    def __init__(
        self,
        sequences: np.ndarray,
        static_values: np.ndarray,
        labels: np.ndarray,
    ) -> None:
        self.sequences = torch.tensor(sequences, dtype=torch.float32)
        self.static_values = torch.tensor(static_values, dtype=torch.float32)
        self.labels = torch.tensor(labels.reshape(-1, 1), dtype=torch.float32)

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(
        self, index: int
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return self.sequences[index], self.static_values[index], self.labels[index]


@dataclass(slots=True)
class TrainingResult:
    model: RuntimeForecastModel
    device: str
    train_losses: list[float]
    validation_losses: list[float]
    validation_maes: list[float]
    best_epoch: int


def _evaluate(
    loader: DataLoader[tuple[torch.Tensor, torch.Tensor, torch.Tensor]],
    model: RuntimeForecastModel,
    criterion: nn.Module,
    device: torch.device,
    target_center: float,
    target_scale: float,
) -> tuple[float, float]:
    model.eval()
    total_loss = 0.0
    total_mae = 0.0
    total_count = 0
    mae_loss = nn.L1Loss(reduction='sum')
    with torch.no_grad():
        for sequences, static_values, labels in loader:
            sequences = sequences.to(device)
            static_values = static_values.to(device)
            labels = labels.to(device)
            predictions = model(sequences, static_values)
            count = sequences.size(0)
            total_loss += float(criterion(predictions, labels).item()) * count
            predictions_original = predictions * target_scale + target_center
            labels_original = labels * target_scale + target_center
            total_mae += float(mae_loss(predictions_original, labels_original).item())
            total_count += count
    return total_loss / total_count, total_mae / total_count


def train_model(
    sequences_train: np.ndarray,
    static_train: np.ndarray,
    labels_train: np.ndarray,
    sequences_validation: np.ndarray,
    static_validation: np.ndarray,
    labels_validation: np.ndarray,
    config: ModelConfig,
    use_gpu: bool = True,
    target_center: float = 0.0,
    target_scale: float = 1.0,
) -> TrainingResult:
    """Train the LSTM model on optionally target-scaled labels.

    Args:
        sequences_train: Scaled temporal training sequences.
        static_train: Scaled static training features.
        labels_train: Training labels in the model's target space.
        sequences_validation: Scaled temporal validation sequences.
        static_validation: Scaled static validation features.
        labels_validation: Validation labels in the model's target space.
        config: Model and optimization configuration.
        use_gpu: Whether CUDA may be used when available.
        target_center: Original-unit target mean used for validation metrics.
        target_scale: Original-unit target standard deviation used for validation
            metrics.

    Returns:
        Training result containing the best model state and metric histories.

        Notes:
        Optimization occurs in the target space supplied through ``labels_train``.
        Validation MAE is restored to original target units using ``target_center``
        and ``target_scale``.
    """
    device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
    model = RuntimeForecastModel(
        sequence_input_size=sequences_train.shape[2],
        static_input_size=static_train.shape[1],
        config=RuntimeModelConfig(
            lstm_hidden=config.lstm_hidden,
            dense_hidden=config.dense_hidden,
            dropout=config.dropout,
        ),
    ).to(device)
    train_loader = DataLoader(
        TemporalStaticDataset(sequences_train, static_train, labels_train),
        batch_size=config.batch_size,
        shuffle=True,
    )
    validation_loader = DataLoader(
        TemporalStaticDataset(
            sequences_validation, static_validation, labels_validation
        ),
        batch_size=config.batch_size,
        shuffle=False,
    )
    criterion = nn.SmoothL1Loss(beta=config.smooth_l1_beta)
    optimizer: optim.Optimizer = optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='min',
        factor=config.scheduler_factor,
        patience=config.scheduler_patience,
    )
    best_mae = float('inf')
    best_state: dict[str, torch.Tensor] | None = None
    patience = 0
    best_epoch = 0
    train_losses: list[float] = []
    validation_losses: list[float] = []
    validation_maes: list[float] = []

    for epoch in range(config.epochs):
        model.train()
        total_loss = 0.0
        total_count = 0
        for sequences, static_values, labels in train_loader:
            sequences = sequences.to(device)
            static_values = static_values.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(sequences, static_values), labels)
            loss.backward()
            if config.gradient_clip_norm > 0:
                nn.utils.clip_grad_norm_(model.parameters(), config.gradient_clip_norm)
            optimizer.step()
            count = sequences.size(0)
            total_loss += float(loss.item()) * count
            total_count += count

        train_loss = total_loss / total_count
        validation_loss, validation_mae = _evaluate(
            validation_loader,
            model,
            criterion,
            device,
            target_center,
            target_scale,
        )
        train_losses.append(train_loss)
        validation_losses.append(validation_loss)
        validation_maes.append(validation_mae)
        print(
            f'Epoch {epoch + 1}/{config.epochs} | '
            f'Train Loss: {train_loss:.6f} | '
            f'Val Loss: {validation_loss:.6f} | Val MAE: {validation_mae:.6f}'
        )

        scheduler.step(validation_mae)
        if validation_mae < best_mae:
            best_mae = validation_mae
            best_state = {
                name: parameter.detach().cpu().clone()
                for name, parameter in model.state_dict().items()
            }
            best_epoch = epoch + 1
            patience = 0
        else:
            patience += 1
            if patience >= config.early_stopping_patience:
                print(f'Early stopping triggered at epoch {epoch + 1}')
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    return TrainingResult(
        model=model,
        device=str(device),
        train_losses=train_losses,
        validation_losses=validation_losses,
        validation_maes=validation_maes,
        best_epoch=best_epoch,
    )
