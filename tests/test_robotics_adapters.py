import pytest
from neurosymbolic_guard.robotics_adapters import ROS2TwistGuard, MAVLinkVelocityGuard


def test_ros2_and_mavlink_adapters():
    ros = ROS2TwistGuard(human_dist_m=1.2)
    safe_twist = ros.filter_twist({"linear_x": 1.8, "angular_z": 0.1})
    assert safe_twist.status in ("Clamped", "EmergencyStop")
    assert safe_twist.linear_x in (pytest.approx(0.4), 0.0)

    mav = MAVLinkVelocityGuard(obstacle_dist_m=0.8)
    safe_mav = mav.filter_setpoint_ned(vx=2.5, vy=0.0, vz=0.0)
    assert safe_mav["status"] in ("Clamped", "EmergencyStop")
    assert safe_mav["vx"] <= 0.4
