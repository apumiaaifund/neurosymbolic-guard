from __future__ import annotations

import json
from neurosymbolic_guard.embodied_bridge import EdgeVerdict, EmbodiedEdgeShield, embodied_guard

shield = EmbodiedEdgeShield()


@embodied_guard(shield)
def dispatch_wheel_motors(
    *,
    sensors: dict[str, float],
    linear_velocity_ms: float,
    angular_velocity_rads: float = 0.0,
    edge_verdict: EdgeVerdict | None = None,
) -> dict[str, object]:
    return {
        "dispatched_v_ms": linear_velocity_ms,
        "status": edge_verdict.status if edge_verdict else "Unknown",
        "reason": edge_verdict.reason if edge_verdict else "",
        "latency_us": edge_verdict.latency_us if edge_verdict else -1,
        "backend": edge_verdict.backend if edge_verdict else "none",
    }


def main() -> None:
    scenarios = [
        ("1. Штатный проезд", {"distance_to_human_m": 8.5, "distance_to_obstacle_m": 12.0, "floor_friction_coeff": 0.85, "battery_pct": 80.0}, 2.2),
        ("2. Мокрый пол (μ=0.2)", {"distance_to_human_m": 6.0, "distance_to_obstacle_m": 1.5, "floor_friction_coeff": 0.2, "battery_pct": 78.0}, 2.8),
        ("3. Человек в зоне 1.1м", {"distance_to_human_m": 1.1, "distance_to_obstacle_m": 5.0, "floor_friction_coeff": 0.8, "battery_pct": 75.0}, 1.9),
        ("4. Сбой лидара (NaN)", {"distance_to_human_m": float("nan"), "distance_to_obstacle_m": 4.0, "floor_friction_coeff": 0.8, "battery_pct": 74.0}, 2.5),
    ]

    print(f"=== APUMIA EMBODIED GUARD ({shield.backend}) ===")
    for title, sensors, cmd_v in scenarios:
        res = dispatch_wheel_motors(sensors=sensors, linear_velocity_ms=cmd_v)
        print(f"{title}: req={cmd_v:.2f} -> safe={res['dispatched_v_ms']:.2f} м/с | {res['status']} ({res['latency_us']} мкс) {res['reason']}")

    audit = shield.export_audit_dict()
    print(f"\nКрипто-цепочка FlightRecorder валидна: {audit['chain_valid']} | Записей: {len(audit['records'])}")
    print("Последняя запись в JSON:", json.dumps(audit["records"][-1], ensure_ascii=False))


if __name__ == "__main__":
    main()
