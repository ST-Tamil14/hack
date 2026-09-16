from __future__ import annotations

import torch
from torch import nn


class BehavioralCNNLSTM(nn.Module):
    def __init__(
        self,
        feature_count: int,
        num_classes: int = 4,
    ) -> None:
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv1d(
                feature_count,
                64,
                kernel_size=3,
                padding=1,
            ),
            nn.BatchNorm1d(64),
            nn.ReLU(),

            nn.Conv1d(
                64,
                128,
                kernel_size=3,
                padding=1,
            ),
            nn.BatchNorm1d(128),
            nn.ReLU(),

            nn.Dropout(0.25),
        )

        self.lstm = nn.LSTM(
            input_size=128,
            hidden_size=64,
            batch_first=True,
            bidirectional=True,
        )

        self.classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(64, num_classes),
        )

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        # Input shape: [batch, time, features]
        x = x.transpose(1, 2)

        x = self.cnn(x)

        x = x.transpose(1, 2)

        x, _ = self.lstm(x)

        x = x[:, -1, :]

        return self.classifier(x)


def create_behavioral_model(
    feature_count: int,
    num_classes: int = 4,
) -> BehavioralCNNLSTM:
    return BehavioralCNNLSTM(
        feature_count=feature_count,
        num_classes=num_classes,
    )
