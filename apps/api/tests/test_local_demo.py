from fastapi.testclient import TestClient

from app.config import get_settings
from app.database import create_database_engine, create_session_factory
from app.main import create_app


def clear_database_caches() -> None:
    engine = create_database_engine()
    if engine is not None:
        engine.dispose()
    create_session_factory.cache_clear()
    create_database_engine.cache_clear()
    get_settings.cache_clear()


def test_local_demo_bootstraps_the_santos_family_without_postgres(monkeypatch, tmp_path) -> None:
    demo_database = tmp_path / "padalo-demo.sqlite3"
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("LOCAL_DEMO_MODE", "true")
    monkeypatch.setenv("LOCAL_DEMO_DATABASE_URL", f"sqlite:///{demo_database.as_posix()}")
    clear_database_caches()

    try:
        with TestClient(create_app()) as client:
            households = client.get("/api/v1/households")
            dashboard = client.get(
                "/api/v1/households/cccccccc-cccc-4ccc-8ccc-cccccccccccc/dashboard/summary"
            )

        assert households.status_code == 200
        assert len(households.json()["items"]) == 1
        assert households.json()["items"][0]["id"] == "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
        assert households.json()["items"][0]["name"] == "Santos Family"
        assert dashboard.status_code == 200
        assert dashboard.json()["household"]["name"] == "Santos Family"
        assert len(dashboard.json()["envelopes"]) == 5
    finally:
        clear_database_caches()
