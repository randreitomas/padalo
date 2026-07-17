from __future__ import annotations

from decimal import Decimal

from padalo_agent.schemas.models import ForecastRecommendation, ForecastRemittanceInput
from padalo_forecasting.services.forecast_service import get_default_forecast_service

_DEMO_AMOUNT_PHP = Decimal("15000.00")


def forecast_remittance(payload: ForecastRemittanceInput) -> ForecastRecommendation:
    """Adapt the independent Prophet service to the frozen agent tool response contract."""

    result = get_default_forecast_service().forecast(
        provider=payload.provider,
        amount_php=payload.amount_php or _DEMO_AMOUNT_PHP,
    )
    return ForecastRecommendation(
        recommended_day=result.recommended_day,
        expected_savings_php=result.expected_savings_php,
        confidence=f"{result.confidence_percent}% historical-pattern confidence",
        provider=result.provider,
        amount_php=result.amount_php,
        is_mock=True,
        disclaimer=result.limitations,
    )
