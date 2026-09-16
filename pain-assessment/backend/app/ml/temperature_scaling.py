import torch
from torch import nn, optim


class TemperatureScaler(nn.Module):
    def __init__(self):
        super().__init__()
        self.temperature = nn.Parameter(torch.ones(1))

    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        return logits / self.temperature.clamp(min=0.05)

    def probabilities(self, logits: torch.Tensor) -> torch.Tensor:
        calibrated_logits = self.forward(logits)
        return torch.softmax(calibrated_logits, dim=-1)


def fit_temperature(
    val_logits: torch.Tensor,
    val_labels: torch.Tensor,
    lr: float = 0.01,
    max_iter: int = 50,
) -> TemperatureScaler:
    """Learns optimal temperature scaling parameter on validation/calibration set logits

    using NLL loss to minimize overconfidence without changing classification ranks.
    """
    scaler = TemperatureScaler()
    criterion = nn.CrossEntropyLoss()

    optimizer = optim.LBFGS([scaler.temperature], lr=lr, max_iter=max_iter)

    def eval_loss():
        optimizer.zero_grad()
        loss = criterion(scaler(val_logits), val_labels)
        loss.backward()
        return loss

    optimizer.step(eval_loss)
    return scaler
