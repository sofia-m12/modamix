from fastapi.testclient import TestClient
from app.main import app
def test_health_check() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_allows_preflight_from_local_frontend() -> None:
    response = TestClient(app).options(
        "/api/imports",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
