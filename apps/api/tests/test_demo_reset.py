from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import create_app


class FakeTransaction:
    def __enter__(self) -> object:
        return object()

    def __exit__(self, *_: object) -> None:
        return None


class FakeEngine:
    def begin(self) -> FakeTransaction:
        return FakeTransaction()


def test_demo_reset_is_hidden_until_enabled(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.routers.demo.get_settings",
        lambda: SimpleNamespace(demo_reset_enabled=False, demo_reset_token=""),
    )
    response = TestClient(create_app()).post("/_ops/demo/reset")

    assert response.status_code == 404


def test_demo_reset_reseeds_only_when_the_deployment_token_matches(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        "app.api.routers.demo.get_settings",
        lambda: SimpleNamespace(demo_reset_enabled=True, demo_reset_token="demo-secret"),
    )
    monkeypatch.setattr("app.api.routers.demo.create_database_engine", lambda: FakeEngine())
    monkeypatch.setattr("app.api.routers.demo.upsert_roles", lambda _: calls.append("roles"))
    monkeypatch.setattr(
        "app.api.routers.demo.reset_demo_household", lambda _: calls.append("household")
    )
    monkeypatch.setattr("app.api.routers.demo.upsert_demo_rows", lambda _: calls.append("rows"))
    client = TestClient(create_app())

    denied = client.post("/_ops/demo/reset", headers={"X-Padalo-Demo-Reset-Token": "wrong"})
    accepted = client.post(
        "/_ops/demo/reset",
        headers={"X-Padalo-Demo-Reset-Token": "demo-secret"},
    )

    assert denied.status_code == 403
    assert accepted.status_code == 204
    assert calls == ["roles", "household", "rows"]
