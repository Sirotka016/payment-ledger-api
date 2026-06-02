from app.main import create_app


def test_healthcheck_returns_status_ok():
    app = create_app("payment-ledger-api-test")

    _, response = app.test_client.get("/health")

    assert response.status == 200
    assert response.json == {"status": "ok"}
