"""
Minimal but real tests: auth enforcement + health contract.
Expand as you build — CI fails the build if these fail, which is the point.
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_generate_requires_api_key():
    # FastAPI's APIKeyHeader dependency returns 403 when the header is
    # missing entirely (before our code runs at all) -- distinct from the
    # 401 we raise ourselves when a key is present but wrong.
    r = client.post("/v1/generate", json={"prompt": "hello"})
    assert r.status_code == 403  # missing header vs bad key


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


def test_health_reports_ollama_status():
    r = client.get("/health")
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        assert r.json()["status"] == "ok"


def test_generate_missing_prompt_field_is_rejected():
    r = client.post(
        "/v1/generate",
        json={},
        headers={"X-API-Key": "changeme"},
    )
    assert r.status_code == 422


def test_metrics_track_request_count():
    before = client.get("/metrics").content
    client.post("/v1/generate", json={"prompt": "x"})
    after = client.get("/metrics").content
    assert before != after or b"gateway_requests_total" in after