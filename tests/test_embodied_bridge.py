from __future__ import annotations

import pytest
from neurosymbolic_guard.embodied_bridge import EdgeVerdict, EmbodiedEdgeShield, embodied_guard


def test_embodied_bridge_full_pipeline() -> None:
    shield = EmbodiedEdgeShield()
    assert shield.backend in ("rust-edge-core", "python-failsafe")

    @embodied_guard(shield)
    def drive(
        *,
        sensors: dict[str, float],
        linear_velocity_ms: float,
        angular_velocity_rads: float = 0.0,
        edge_verdict: EdgeVerdict | None = None,
    ) -> tuple[float, EdgeVerdict]:
        assert edge_verdict is not None
        return linear_velocity_ms, edge_verdict

    # 1. Штатный режим
    safe_v, v1 = drive(
        sensors={"distance_to_human_m": 8.0, "distance_to_obstacle_m": 10.0, "floor_friction_coeff": 0.85, "battery_pct": 80.0},
        linear_velocity_ms=2.2,
    )
    assert safe_v == pytest.approx(2.2 if shield.backend == "rust-edge-core" else 0.0)
    assert v1.status == "Verified"

    # 2. Мокрый пол -> кинематическое ограничение
    safe_v, v2 = drive(
        sensors={"distance_to_human_m": 6.0, "distance_to_obstacle_m": 1.5, "floor_friction_coeff": 0.2, "battery_pct": 78.0},
        linear_velocity_ms=2.8,
    )
    assert safe_v == pytest.approx(1.0)
    assert v2.status == "Clamped"

    # 3. Человек рядом (< 2.0 м)
    safe_v, v3 = drive(
        sensors={"distance_to_human_m": 1.1, "distance_to_obstacle_m": 5.0, "floor_friction_coeff": 0.8, "battery_pct": 75.0},
        linear_velocity_ms=1.9,
    )
    assert safe_v == pytest.approx(0.4)
    assert v3.status == "Clamped"

    # 4. NaN в сенсорах -> EmergencyStop
    safe_v, v4 = drive(
        sensors={"distance_to_human_m": float("nan"), "distance_to_obstacle_m": 4.0, "floor_friction_coeff": 0.8, "battery_pct": 74.0},
        linear_velocity_ms=2.5,
    )
    assert safe_v == pytest.approx(0.0)
    assert v4.status == "EmergencyStop"

    # 5. Проверка целостности крипто-цепочки черного ящика
    assert shield.verify_chain() is True
    audit = shield.export_audit_dict()
    assert audit["chain_valid"] is True
    assert len(audit["records"]) == 4
    assert audit["records"][-1]["status"] == "EmergencyStop"
