from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app


def test_health() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "padalo-api"}


def test_loopback_dashboard_origin_is_allowed() -> None:
    response = TestClient(create_app()).get(
        "/health",
        headers={"Origin": "http://127.0.0.1:3000"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"


def test_agent_stream_requires_an_openai_key(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/households/cccccccc-cccc-4ccc-8ccc-cccccccccccc/agent/stream",
        json={"message": "How is the budget?"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "OpenAI is not configured. Set OPENAI_API_KEY to enable the assistant."
    )
    get_settings.cache_clear()
