"""Health endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_200_and_paper_banner() -> None:
    client = TestClient(create_app())
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_mode"] == "paper"
    assert body["live_trading_enabled"] is False
    assert body["trading_enabled"] is False
    assert "PAPER TRADING" in body["simulation"]
    assert "SEM DINHEIRO REAL" in body["simulation"]
    assert "timestamp" in body
    assert body["service"] == "trading-bot-backend"


def test_health_does_not_expose_secrets() -> None:
    client = TestClient(create_app())
    body = client.get("/api/v1/health").json()
    serialized = str(body).lower()
    forbidden = [
        "service_role",
        "supabase_anon",
        "api_key",
        "password",
        "secret",
        "bearer",
        "jwt",
    ]
    for token in forbidden:
        assert token not in serialized


def test_only_health_api_route_is_registered() -> None:
    app = create_app()
    api_paths = sorted(
        {
            getattr(route, "path", "")
            for route in app.routes
            if getattr(route, "path", "").startswith("/api/")
        }
    )
    assert api_paths == ["/api/v1/health"]
