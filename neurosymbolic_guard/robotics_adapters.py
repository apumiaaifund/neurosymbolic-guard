from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from neurosymbolic_guard.embodied_bridge import EdgeVerdict, EmbodiedEdgeShield


@dataclass(frozen=True)
class Ros2Twist:
    """Эквивалент geometry_msgs/msg/Twist в ROS 2."""

    linear_x: float
    linear_y: float = 0.0
    linear_z: float = 0.0
    angular_x: float = 0.0
    angular_y: float = 0.0
    angular_z: float = 0.0


@dataclass(frozen=True)
class MavlinkVelocityTarget:
    """Эквивалент MAVLink SET_POSITION_TARGET_LOCAL_NED (vx, vy, vz, yaw_rate)."""

    vx: float
    vy: float = 0.0
    vz: float = 0.0
    yaw_rate: float = 0.0


class RoboticsProtocolGuard:
    """Адаптер ROS 2 и MAVLink поверх нативного Rust EmbodiedEdgeShield (< 1 мкс)."""

    def __init__(self, shield: EmbodiedEdgeShield | None = None) -> None:
        self.shield = shield or EmbodiedEdgeShield()

    def filter_ros2_twist(
        self,
        twist: Ros2Twist,
        *,
        distance_to_human_m: float,
        distance_to_obstacle_m: float,
        floor_friction_coeff: float,
        battery_pct: float,
    ) -> tuple[Ros2Twist, EdgeVerdict]:
        verdict = self.shield.evaluate(
            distance_to_human_m=distance_to_human_m,
            distance_to_obstacle_m=distance_to_obstacle_m,
            floor_friction_coeff=floor_friction_coeff,
            battery_pct=battery_pct,
            linear_velocity_ms=twist.linear_x,
            angular_velocity_rads=twist.angular_z,
        )
        safe_twist = Ros2Twist(
            linear_x=verdict.safe_linear_velocity_ms,
            linear_y=0.0 if verdict.status == "EmergencyStop" else twist.linear_y,
            linear_z=0.0 if verdict.status == "EmergencyStop" else twist.linear_z,
            angular_x=0.0,
            angular_y=0.0,
            angular_z=verdict.safe_angular_velocity_rads,
        )
        return safe_twist, verdict

    def filter_mavlink_target(
        self,
        target: MavlinkVelocityTarget,
        *,
        distance_to_human_m: float,
        distance_to_obstacle_m: float,
        surface_friction_coeff: float = 0.85,
        battery_pct: float = 80.0,
    ) -> tuple[MavlinkVelocityTarget, EdgeVerdict]:
        ground_speed = math.hypot(target.vx, target.vy)
        verdict = self.shield.evaluate(
            distance_to_human_m=distance_to_human_m,
            distance_to_obstacle_m=distance_to_obstacle_m,
            floor_friction_coeff=surface_friction_coeff,
            battery_pct=battery_pct,
            linear_velocity_ms=ground_speed,
            angular_velocity_rads=target.yaw_rate,
        )
        if ground_speed > 1e-9 and math.isfinite(ground_speed):
            scale = verdict.safe_linear_velocity_ms / ground_speed
        else:
            scale = 0.0

        safe_target = MavlinkVelocityTarget(
            vx=round(target.vx * scale, 6),
            vy=round(target.vy * scale, 6),
            vz=0.0 if verdict.status == "EmergencyStop" else target.vz,
            yaw_rate=verdict.safe_angular_velocity_rads,
        )
        return safe_target, verdict

    def export_blackbox(self) -> dict[str, Any]:
        return self.shield.export_audit_dict()
