from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from padalo_forecasting.evaluation.backtest import ProviderEvaluation


def write_backtest_chart(evaluations: dict[str, ProviderEvaluation], output_path: Path) -> Path:
    """Write a small MAE comparison chart for hackathon documentation and review."""

    providers = list(evaluations)
    prophet_mae = [evaluations[provider].prophet.mae for provider in providers]
    baseline_mae = [evaluations[provider].baseline.mae for provider in providers]
    positions = list(range(len(providers)))

    figure, axis = plt.subplots(figsize=(8, 4.5))
    width = 0.36
    axis.bar([position - width / 2 for position in positions], prophet_mae, width, label="Prophet")
    axis.bar(
        [position + width / 2 for position in positions],
        baseline_mae,
        width,
        label="Naive baseline",
    )
    axis.set_ylabel("MAE (PHP effective cost)")
    axis.set_title("FXPilot deterministic backtest")
    axis.set_xticks(positions, providers)
    axis.legend()
    axis.grid(axis="y", alpha=0.2)
    figure.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=160)
    plt.close(figure)
    return output_path
