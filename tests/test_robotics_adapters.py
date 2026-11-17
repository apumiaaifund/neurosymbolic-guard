import pytest
from neurosymbolic_guard.robotics_adapters import MavlinkVelocityTarget, RoboticsProtocolGuard, Ros2Twist

def test_ros2_and_mavlink_adapters():
    g = RoboticsProtocolGuard()
    st, v1 = g.filter_ros2_twist(Ros2Twist(linear_x=1.8, angular_z=0.1), distance_to_human_m=1.2, distance_to_obstacle_m=5.0, floor_friction_coeff=0.8, battery_pct=80.0)
    assert v1.status in ("Clamped", "EmergencyStop")
    assert st.linear_x in (pytest.approx(0.4), 0.0)
    sm, v2 = g.filter_mavlink_target(MavlinkVelocityTarget(vx=2.5), distance_to_human_m=10.0, distance_to_obstacle_m=0.8)
    assert v2.status in ("Clamped", "EmergencyStop")
    assert sm.vx < 2.5
