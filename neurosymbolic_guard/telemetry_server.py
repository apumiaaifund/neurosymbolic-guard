from __future__ import annotations

import asyncio
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from neurosymbolic_guard.embodied_bridge import EmbodiedEdgeShield


class TelemetryRequest(BaseModel):
    distance_to_human_m: float
    distance_to_obstacle_m: float
    floor_friction_coeff: float
    battery_pct: float
    linear_velocity_ms: float
    angular_velocity_rads: float = 0.0


class ConnectionManager:
    def __init__(self) -> None:
        self._active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._active:
            self._active.remove(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for ws in self._active:
            try:
                await ws.send_json(payload)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(ws)


def create_app() -> FastAPI:
    app = FastAPI(title="APUMIA Embodied Guard — Live Telemetry & BlackBox", version="0.1.0")
    shield = EmbodiedEdgeShield()
    manager = ConnectionManager()

    app.state.shield = shield
    app.state.manager = manager

    @app.get("/", response_class=HTMLResponse)
    async def dashboard() -> str:
        return """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>APUMIA Embodied Guard — Live FlightRecorder</title>
  <style>
    body { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background: #0b0f19; color: #e2e8f0; margin: 24px; }
    h1 { color: #38bdf8; font-size: 20px; }
    .meta { color: #94a3b8; margin-bottom: 16px; font-size: 13px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { border-bottom: 1px solid #1e293b; padding: 8px 10px; text-align: left; }
    th { color: #94a3b8; }
    .Verified { color: #4ade80; font-weight: bold; }
    .Clamped { color: #facc15; font-weight: bold; }
    .EmergencyStop { color: #f87171; font-weight: bold; }
  </style>
</head>
<body>
  <h1>APUMIA EMBODIED GUARD — CRYPTO FLIGHT RECORDER</h1>
  <div class="meta">Backend: <span id="backend">connecting...</span> | Chain Valid: <span id="chain">-</span></div>
  <table>
    <thead><tr><th>Seq</th><th>Status</th><th>Req V</th><th>Safe V</th><th>Latency</th><th>Reason</th><th>Record Hash</th></tr></thead>
    <tbody id="rows"></tbody>
  </table>
  <script>
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${proto}//${location.host}/ws/telemetry`);
    const rows = document.getElementById('rows');
    function addRow(rec, backend, valid) {
      document.getElementById('backend').textContent = backend;
      document.getElementById('chain').textContent = valid ? 'VERIFIED OK' : 'CORRUPTED';
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${rec.seq}</td><td class="${rec.status}">${rec.status}</td><td>${rec.requested_v}</td><td>${rec.safe_v}</td><td>${rec.latency_us ?? 0} µs</td><td>${rec.reason || '-'}</td><td>${rec.record_hash}</td>`;
      rows.prepend(tr);
    }
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.type === 'snapshot') {
        rows.innerHTML = '';
        msg.audit.records.forEach(r => addRow(r, msg.backend, msg.audit.chain_valid));
      } else if (msg.type === 'event') {
        addRow(msg.record, msg.backend, msg.chain_valid);
      }
    };
  </script>
</body>
</html>"""

    @app.post("/api/v1/evaluate")
    async def evaluate_command(req: TelemetryRequest) -> dict[str, Any]:
        verdict = shield.evaluate(
            distance_to_human_m=req.distance_to_human_m,
            distance_to_obstacle_m=req.distance_to_obstacle_m,
            floor_friction_coeff=req.floor_friction_coeff,
            battery_pct=req.battery_pct,
            linear_velocity_ms=req.linear_velocity_ms,
            angular_velocity_rads=req.angular_velocity_rads,
        )
        audit = shield.export_audit_dict()
        latest_record = audit["records"][-1] if audit["records"] else {}
        latest_record["latency_us"] = verdict.latency_us

        event_payload = {
            "type": "event",
            "backend": shield.backend,
            "chain_valid": audit["chain_valid"],
            "verdict": {
                "status": verdict.status,
                "reason": verdict.reason,
                "safe_linear_velocity_ms": verdict.safe_linear_velocity_ms,
                "safe_angular_velocity_rads": verdict.safe_angular_velocity_rads,
                "latency_us": verdict.latency_us,
            },
            "record": latest_record,
        }
        await manager.broadcast(event_payload)
        return event_payload

    @app.get("/api/v1/audit")
    async def get_audit() -> dict[str, Any]:
        return {
            "backend": shield.backend,
            "audit": shield.export_audit_dict(),
        }

    @app.websocket("/ws/telemetry")
    async def websocket_telemetry(websocket: WebSocket) -> None:
        await manager.connect(websocket)
        try:
            await websocket.send_json(
                {
                    "type": "snapshot",
                    "backend": shield.backend,
                    "audit": shield.export_audit_dict(),
                }
            )
            while True:
                await asyncio.sleep(30)
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    return app


app = create_app()
