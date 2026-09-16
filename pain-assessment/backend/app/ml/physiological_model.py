from __future__ import annotations

import torch
from torch import nn


class PhysiologicalCNNLSTM(nn.Module):
    """
    1D CNN + LSTM model for physiological time-series classification.

    Input:
        [batch_size, time_steps, feature_count]

    Output:
        [batch_size, num_classes]
    """

    def __init__(
        self,
        feature_count: int,
        num_classes: int = 4,
        lstm_hidden_size: int = 64,
    ) -> None:
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv1d(
                in_channels=feature_count,
                out_channels=64,
                kernel_size=3,
                padding=1,
            ),
            nn.BatchNorm1d(64),
            nn.ReLU(),

            nn.Conv1d(
                in_channels=64,
                out_channels=128,
                kernel_size=3,
                padding=1,
            ),
            nn.BatchNorm1d(128),
            nn.ReLU(),

            nn.Dropout(0.25),
        )

        self.lstm = nn.LSTM(
            input_size=128,
            hidden_size=lstm_hidden_size,
            num_layers=1,
            batch_first=True,
            bidirectional=True,
        )

        self.classifier = nn.Sequential(
            nn.Linear(lstm_hidden_size * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(64, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [batch, time, features]

        x = x.transpose(1, 2)

        # [batch, features, time]
        x = self.cnn(x)

        # [batch, time, cnn_features]
        x = x.transpose(1, 2)

        x, _ = self.lstm(x)

        # Use the last time step
        x = x[:, -1, :]

        return self.classifier(x)


def create_physiological_model(
    feature_count: int,
    num_classes: int = 4,
) -> PhysiologicalCNNLSTM:
    return PhysiologicalCNNLSTM(
        feature_count=feature_count,
        num_classes=num_classes,
    )
