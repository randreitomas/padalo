from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from padalo_forecasting.config import (
    CONFIG,
    DEFAULT_PROVIDER,
    DEMO_PROVIDER,
    SUPPORTED_PROVIDERS,
    ForecastConfig,
    default_dataset_path,
    default_evaluation_path,
)
from padalo_forecasting.dataset.generator import future_feature_frame, load_or_generate_dataset
from padalo_forecasting.models.prophet_model import fit_prophet_model, predict_costs


@dataclass(frozen=True)
class ForecastResult:
    recommended_day: str
    expected_savings_php: Decimal
    confidence_percent: int
    provider: str
    amount_php: Decimal
    reasoning: str
    limitations: str
    model_version: str
    is_synthetic: bool


class FxPilotForecastService:
    """Provider-scoped Prophet forecasting with an in-process immutable model cache."""

    def __init__(
        self,
        *,
        dataset_path: Path | None = None,
        evaluation_path: Path | None = None,
        dataset: pd.DataFrame | None = None,
        config: ForecastConfig = CONFIG,
    ) -> None:
        self.dataset_path = dataset_path or default_dataset_path()
        self.evaluation_path = evaluation_path or default_evaluation_path()
        self.config = config
        self._dataset = self._normalize_dataset(dataset) if dataset is not None else None
        self._models: dict[tuple[str, date], Any] = {}
        self._evaluation: dict[str, Any] | None = None

    def forecast(
        self,
        *,
        provider: str | None,
        amount_php: Decimal | float | int,
        as_of: date | None = None,
    ) -> ForecastResult:
        requested_provider = (provider or DEMO_PROVIDER).strip() or DEMO_PROVIDER
        model_provider = self._resolve_provider(requested_provider)
        observation_date = as_of or date.today()
        amount = Decimal(str(amount_php)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        history = self._history_for(model_provider, observation_date)
        model = self._model_for(model_provider, history)

        future_dates = pd.date_range(
            observation_date + timedelta(days=1),
            periods=self.config.forecast_horizon_days,
            freq="D",
        )
        future = future_feature_frame(model_provider, future_dates)
        prediction = predict_costs(model, future, self.config)
        scale = float(amount) / self.config.reference_amount_php
        estimated_costs = np.maximum(prediction["yhat"].to_numpy(dtype=float) * scale, 0.0)
        lower_costs = np.maximum(prediction["yhat_lower"].to_numpy(dtype=float) * scale, 0.0)
        upper_costs = np.maximum(prediction["yhat_upper"].to_numpy(dtype=float) * scale, 0.0)
        best_index = int(np.argmin(estimated_costs))
        reference_cost = float(np.median(estimated_costs))
        savings = max(0.0, reference_cost - float(estimated_costs[best_index]))
        confidence = self._confidence_percent(
            provider=model_provider,
            expected_cost=float(estimated_costs[best_index]),
            lower_cost=float(lower_costs[best_index]),
            upper_cost=float(upper_costs[best_index]),
        )
        recommended_date = future_dates[best_index].date()
        reasoning = self._reasoning(
            provider=model_provider,
            requested_provider=requested_provider,
            recommended_date=recommended_date,
            history=history,
        )
        limitations = (
            f"{reasoning} This estimate uses deterministic synthetic historical data, not live "
            "provider quotes, a provider commitment, or financial advice."
        )

        return ForecastResult(
            recommended_day=recommended_date.strftime("%A"),
            expected_savings_php=Decimal(str(savings)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            confidence_percent=confidence,
            provider=requested_provider if requested_provider == DEMO_PROVIDER else model_provider,
            amount_php=amount,
            reasoning=reasoning,
            limitations=limitations,
            model_version=self.config.model_version,
            is_synthetic=True,
        )

    def _history_for(self, provider: str, as_of: date) -> pd.DataFrame:
        frame = self._load_dataset()
        history = frame.loc[
            (frame["provider"] == provider) & (frame["date"].dt.date <= as_of)
        ].copy()
        if len(history) < 56:
            raise ValueError(f"FXPilot has insufficient synthetic history for provider {provider}.")
        return history.sort_values("date").reset_index(drop=True)

    def _model_for(self, provider: str, history: pd.DataFrame) -> Any:
        cache_key = (provider, history["date"].max().date())
        model = self._models.get(cache_key)
        if model is None:
            model = fit_prophet_model(history, self.config)
            self._models[cache_key] = model
        return model

    def _load_dataset(self) -> pd.DataFrame:
        if self._dataset is None:
            self._dataset = self._normalize_dataset(load_or_generate_dataset(self.dataset_path))
        return self._dataset

    @staticmethod
    def _normalize_dataset(frame: pd.DataFrame) -> pd.DataFrame:
        normalized = frame.copy()
        normalized["date"] = pd.to_datetime(normalized["date"])
        return normalized

    def _load_evaluation(self) -> dict[str, Any]:
        if self._evaluation is not None:
            return self._evaluation
        if self.evaluation_path.exists():
            self._evaluation = json.loads(self.evaluation_path.read_text(encoding="utf-8"))
        else:
            self._evaluation = {"providers": {}}
        return self._evaluation

    def _confidence_percent(
        self,
        *,
        provider: str,
        expected_cost: float,
        lower_cost: float,
        upper_cost: float,
    ) -> int:
        report = self._load_evaluation()
        provider_report = report.get("providers", {}).get(provider, {})
        mape = float(provider_report.get("prophet", {}).get("mape", 12.0))
        relative_interval = (upper_cost - lower_cost) / max(expected_cost, 1.0)
        score = 90.0 - min(18.0, mape * 0.9) - min(10.0, relative_interval * 25.0)
        return int(round(max(65.0, min(92.0, score))))

    @staticmethod
    def _resolve_provider(provider: str) -> str:
        for supported_provider in SUPPORTED_PROVIDERS:
            if supported_provider.casefold() == provider.casefold():
                return supported_provider
        return DEFAULT_PROVIDER

    def _reasoning(
        self,
        *,
        provider: str,
        requested_provider: str,
        recommended_date: date,
        history: pd.DataFrame,
    ) -> str:
        weekday_costs = (
            history.groupby(history["date"].dt.day_name())["effective_cost_php_15000"].mean()
        )
        recommended_average = float(weekday_costs.get(recommended_date.strftime("%A"), 0.0))
        known_provider = any(
            supported_provider.casefold() == requested_provider.casefold()
            for supported_provider in SUPPORTED_PROVIDERS
        )
        provider_label = provider if not known_provider else requested_provider
        fallback_note = (
            f" A {provider} synthetic profile is used for the labelled demo assumption."
            if requested_provider == DEMO_PROVIDER or not known_provider
            else ""
        )
        return (
            f"Historical synthetic {provider_label} behavior shows lower modeled total send costs "
            "on "
            f"{recommended_date.strftime('%A')} (about PHP {recommended_average:.0f} at the PHP "
            f"{self.config.reference_amount_php:,.0f} reference amount), after weekly, payday, "
            f"holiday, and scheduled promo effects are considered.{fallback_note}"
        )


@lru_cache(maxsize=1)
def get_default_forecast_service() -> FxPilotForecastService:
    return FxPilotForecastService()
