from dataclasses import dataclass

import torch
from torch import nn


@dataclass(frozen=True, slots=True)
class RuntimeModelConfig:
    """Architecture parameters required to reconstruct one model artifact."""

    lstm_hidden: int
    dense_hidden: int
    dropout: float


class RuntimeForecastModel(nn.Module):
    """LSTM and dense feature-fusion model used for runtime forecasting."""

    def __init__(
        self,
        sequence_input_size: int,
        static_input_size: int,
        config: RuntimeModelConfig,
    ) -> None:
        """Initialize the runtime model architecture.

        Args:
            sequence_input_size: Number of temporal features per sequence row.
            static_input_size: Number of static features per enterprise.
            config: Architecture parameters recorded by training.
        """
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=sequence_input_size,
            hidden_size=config.lstm_hidden,
            batch_first=True,
        )
        self.sequence_block = nn.Sequential(
            nn.Linear(config.lstm_hidden, config.dense_hidden),
            nn.ReLU(),
            nn.Dropout(config.dropout),
        )
        self.static_block = nn.Sequential(
            nn.Linear(static_input_size, config.dense_hidden),
            nn.ReLU(),
            nn.Dropout(config.dropout),
        )
        self.fusion_block = nn.Sequential(
            nn.Linear(config.dense_hidden * 2, config.dense_hidden),
            nn.ReLU(),
            nn.Dropout(config.dropout),
        )
        self.output_layer = nn.Linear(config.dense_hidden, 1)

    def forward(
        self, input_sequence: torch.Tensor, input_static: torch.Tensor
    ) -> torch.Tensor:
        """Predict the next-period net cash flow.

        Args:
            input_sequence: Scaled temporal tensor with shape ``(batch, steps, features)``.
            input_static: Scaled static tensor with shape ``(batch, features)``.

        Returns:
            Tensor containing one prediction per batch item.
        """
        sequence_output, _ = self.lstm(input_sequence)
        sequence_features = self.sequence_block(sequence_output[:, -1, :])
        static_features = self.static_block(input_static)
        fused = self.fusion_block(
            torch.cat((sequence_features, static_features), dim=1)
        )
        return self.output_layer(fused)
