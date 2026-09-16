from __future__ import annotations

import torch
from torch import nn


class FacialCNNLSTM(nn.Module):
    """
    CNN-LSTM model for facial feature sequence classification.

    Expected input shape:
        batch_size, time_steps, feature_count

    Example:
        [32, 16, 8]
    """

    def __init__(
        self,
        feature_count: int = 8,
        num_classes: int = 4,
        cnn_channels: int = 64,
        lstm_hidden_size: int = 64,
        lstm_layers: int = 1,
        dropout: float = 0.3,
    ):
        super().__init__()

        self.feature_count = feature_count
        self.num_classes = num_classes

        self.cnn = nn.Sequential(
            nn.Conv1d(
                in_channels=feature_count,
                out_channels=cnn_channels,
                kernel_size=3,
                padding=1,
            ),
            nn.BatchNorm1d(cnn_channels),
            nn.ReLU(),

            nn.Conv1d(
                in_channels=cnn_channels,
                out_channels=cnn_channels,
                kernel_size=3,
                padding=1,
            ),
            nn.BatchNorm1d(cnn_channels),
            nn.ReLU(),

            nn.Dropout(dropout),
        )

        self.lstm = nn.LSTM(
            input_size=cnn_channels,
            hidden_size=lstm_hidden_size,
            num_layers=lstm_layers,
            batch_first=True,
            dropout=(
                dropout
                if lstm_layers > 1
                else 0.0
            ),
        )

        self.classifier = nn.Sequential(
            nn.Linear(
                lstm_hidden_size,
                64,
            ),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(
                64,
                num_classes,
            ),
        )

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        """
        Input:
            x: [batch, time_steps, feature_count]

        Output:
            logits: [batch, num_classes]
        """

        if x.ndim != 3:
            raise ValueError(
                "Expected input shape "
                "[batch, time_steps, feature_count]"
            )

        # Conv1d expects:
        # [batch, channels, time_steps]
        x = x.transpose(1, 2)

        x = self.cnn(x)

        # LSTM expects:
        # [batch, time_steps, channels]
        x = x.transpose(1, 2)

        sequence_output, _ = self.lstm(x)

        # Use the final time step representation
        final_output = sequence_output[:, -1, :]

        logits = self.classifier(
            final_output
        )

        return logits


def create_facial_model(
    feature_count: int = 8,
    num_classes: int = 4,
) -> FacialCNNLSTM:
    return FacialCNNLSTM(
        feature_count=feature_count,
        num_classes=num_classes,
    )
