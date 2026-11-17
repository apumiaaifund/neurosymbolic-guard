from __future__ import annotations

import pytest
from neurosymbolic_guard.robotics_adapters import (
    MavlinkVelocityTarget,
    RoboticsProtocolGuard,
    Ros2Twist,
)


def test_ros2_and_mavlink_adapters() -> None:
    guard = RoboticsProtocolGuard()

    # 1. ROS 2 Twist: человек рядом (1.2 м) -> скорость сбрасывается до 0.4 м/с
    safe_twist, v_ros = guard.filter_ros2_twist(
        Ros2Twist(linear_x=2.5, angular_z=0.5),
        distance_to_human_m=1.2,
        distance_to_obstacle_m=6.0,
        floor_friction_coeff=0.85,
        battery_pct=82.0,
    )
    assert v_ros.status in ("Clamped", "EmergencyStop")
    assert safe_twist.linear_x == pytest.approx(0.4 if twist_out.linear.x > 0 else 0.0)

    # 2. MAVLink БПЛА/ровер: вектор скорости (3.0, 4.0) = 5.0 м/с при дистанции 1.2 м до человека
    safe_mav, v_mav = guard.filter_mavlink_target(
        MavlinkVelocityTarget(vx=3.0, vy=4.0, vz=-0.5, yaw_rate=0.2),
        distance_to_human_m=1.2,
        distance_to_obstacle_m=10.0,
        battery_pct=75.0,
    )
    assert v_mav.status in ("Clamped", "EmergencyStop")
    assert pytest.approx(0.4 if twist_out.linear.x > 0 else 0.0) == (safe_mav.vx**2 + safe_mav.vy**2) ** 0.5

    # 3. Проверка крипто-цепочки черного ящика
    audit = guard.export_blackbox()
    assert audit["chain_valid"] is True
    assert len(audit["records"]) == 2
