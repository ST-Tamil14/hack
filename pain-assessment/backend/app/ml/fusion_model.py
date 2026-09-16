from __future__ import annotations

import torch
from torch import nn


FUSION_FEATURE_NAMES = [
    "facial_score",
    "physiological_score",
    "behavioral_score",
    "voice_score",

    "facial_confidence",
    "physiological_confidence",
    "behavioral_confidence",
    "voice_confidence",

    "facial_quality",
    "physiological_quality",
    "behavioral_quality",
    "voice_quality",

    "facial_available",
    "physiological_available",
    "behavioral_available",
    "voice_available",

    "communication_nonverbal",
    "communication_intubated",
    "mobility_restricted",
    "facial_limitation",
    "speech_limitation",
    "sedated",
]


class MultimodalFusionModel(nn.Module):
    """
    Multimodal Fusion MLP model for calibrated pain-related activity classification.
    Input size: 22 features (scores, confidence, quality, availability, patient profile)
    """

    def __init__(
        self,
        input_size: int = 22,
        num_classes: int = 4,
    ) -> None:
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(64, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


def create_fusion_model(
    input_size: int = 22,
    num_classes: int = 4,
) -> MultimodalFusionModel:
    return MultimodalFusionModel(
        input_size=input_size,
        num_classes=num_classes,
    )
