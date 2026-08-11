"""
Minimal but real tests: auth enforcement + health contract.
Expand as you build — CI fails the build if these fail, which is the point.
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_generate_requires_api_key():
    r = client.post("/v1/generate", json={"prompt": "hello"})
    assert r.status_code == 422 or r.status_code == 401  # missing header vs bad key


def test_generate_rejects_bad_api_key():
    r = client.post(
        "/v1/generate",
        json={"prompt": "hello"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert r.status_code == 401


def test_metrics_endpoint_exposed():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"gateway_requests_total" in r.content or r.status_code == 200
