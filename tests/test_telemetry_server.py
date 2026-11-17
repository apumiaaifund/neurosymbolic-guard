from __future__ import annotations

from fastapi.testclient import TestClient
from neurosymbolic_guard.telemetry_server import create_app


def test_rest_and_websocket_telemetry_stream() -> None:
    app = create_app()
    client = TestClient(app)

    with client.websocket_connect("/ws/telemetry") as ws:
        initial = ws.receive_json()
        assert initial["type"] == "snapshot"
        assert initial["backend"] in ("rust-edge-core", "python-failsafe")
        assert initial["audit"]["chain_valid"] is True

        resp = client.post(
            "/api/v1/evaluate",
            json={
                "distance_to_human_m": 6.0,
                "distance_to_obstacle_m": 1.5,
                "floor_friction_coeff": 0.2,
                "battery_pct": 78.0,
                "linear_velocity_ms": 2.8,
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["verdict"]["status"] == "Clamped"
        assert body["verdict"]["safe_linear_velocity_ms"] == 1.0

        streamed = ws.receive_json()
        assert streamed["type"] == "event"
        assert streamed["chain_valid"] is True
        assert streamed["record"]["status"] == "Clamped"
        assert len(streamed["record"]["record_hash"]) == 16

    audit_resp = client.get("/api/v1/audit").json()
    assert audit_resp["audit"]["chain_valid"] is True
    assert len(audit_resp["audit"]["records"]) == 1
