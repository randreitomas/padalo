from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from padalo_forecasting.config import CONFIG, ForecastConfig, default_evaluation_path
from padalo_forecasting.dataset.generator import future_feature_frame, load_or_generate_dataset
from padalo_forecasting.evaluation.metrics import ErrorMetrics, error_metrics
from padalo_forecasting.models.baseline import rolling_same_weekday_baseline
from padalo_forecasting.models.prophet_model import fit_prophet_model, predict_costs, training_frame
from padalo_forecasting.visualizations.backtest_chart import write_backtest_chart


@dataclass(frozen=True)
class ProviderEvaluation:
    provider: str
    holdout_days: int
    prophet: ErrorMetrics
    baseline: ErrorMetrics
    preferred_model: str

    def to_dict(self) -> dict[str, Any]:
        prophet = self.prophet.to_dict()
        baseline = self.baseline.to_dict()
        return {
            "provider": self.provider,
            "holdout_days": self.holdout_days,
            "prophet": prophet,
            "baseline": baseline,
            "preferred_model": self.preferred_model,
            "comparison": _comparison_statement(prophet, baseline, self.preferred_model),
        }


def evaluate_provider(
    frame: pd.DataFrame,
    provider: str,
    config: ForecastConfig = CONFIG,
) -> ProviderEvaluation:
    provider_frame = (
        frame.loc[frame["provider"] == provider].sort_values("date").reset_index(drop=True)
    )
    if len(provider_frame) <= config.holdout_days + 56:
        raise ValueError("The provider history is too short for the requested holdout window.")

    train_frame = provider_frame.iloc[: -config.holdout_days]
    test_frame = provider_frame.iloc[-config.holdout_days :]
    model = fit_prophet_model(train_frame, config)
    future = future_feature_frame(provider, pd.DatetimeIndex(test_frame["date"]))
    forecast = predict_costs(model, future, config)
    prophet_predictions = forecast["yhat"].to_numpy(dtype=float)

    train_history = training_frame(train_frame)
    test_history = training_frame(test_frame)
    baseline_predictions = rolling_same_weekday_baseline(train_history, test_history)
    actual = test_history["y"].to_numpy(dtype=float)
    prophet_metrics = error_metrics(actual, prophet_predictions)
    baseline_metrics = error_metrics(actual, baseline_predictions)
    preferred_model = "prophet" if prophet_metrics.mae <= baseline_metrics.mae else "baseline"
    return ProviderEvaluation(
        provider=provider,
        holdout_days=config.holdout_days,
        prophet=prophet_metrics,
        baseline=baseline_metrics,
        preferred_model=preferred_model,
    )


def evaluate_all_providers(
    frame: pd.DataFrame,
    config: ForecastConfig = CONFIG,
) -> dict[str, ProviderEvaluation]:
    return {
        provider: evaluate_provider(frame, provider, config)
        for provider in sorted(frame["provider"].unique())
    }


def write_evaluation_report(
    evaluations: dict[str, ProviderEvaluation],
    output_path: Path | None = None,
) -> Path:
    path = output_path or default_evaluation_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "model_version": CONFIG.model_version,
        "dataset_version": CONFIG.dataset_version,
        "providers": {
            provider: evaluation.to_dict() for provider, evaluation in evaluations.items()
        },
    }
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return path


def _comparison_statement(
    prophet: dict[str, float], baseline: dict[str, float], preferred_model: str
) -> str:
    if preferred_model == "prophet":
        return (
            "Prophet has lower MAE than the same-weekday baseline on this deterministic holdout "
            f"({prophet['mae']:.2f} versus {baseline['mae']:.2f} PHP)."
        )
    return (
        "Prophet did not outperform the same-weekday baseline on this deterministic holdout "
        f"({prophet['mae']:.2f} versus {baseline['mae']:.2f} PHP)."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate deterministic FXPilot Prophet models.")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--output", type=Path, default=default_evaluation_path())
    parser.add_argument("--chart", type=Path)
    args = parser.parse_args()

    frame = load_or_generate_dataset(args.dataset)
    evaluations = evaluate_all_providers(frame)
    report_path = write_evaluation_report(evaluations, args.output)
    if args.chart:
        write_backtest_chart(evaluations, args.chart)
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
