import math

from tennis_ball_picker_sim.nearest_ball_policy import (
    RobotPose,
    command_toward_ball,
    nearest_ball,
    wrap_angle,
)


def test_nearest_ball_selects_closest_unreached_ball():
    robot = RobotPose(x=0.0, y=0.0, yaw=0.0)
    balls = [
        {"name": "far", "x": 3.0, "y": 0.0},
        {"name": "near", "x": 0.8, "y": 0.0},
        {"name": "already_reached", "x": 0.05, "y": 0.0},
    ]

    assert nearest_ball(robot, balls)["name"] == "near"


def test_nearest_ball_returns_none_when_all_targets_reached():
    robot = RobotPose(x=1.0, y=1.0, yaw=0.0)
    balls = [{"name": "done", "x": 1.05, "y": 1.03}]

    assert nearest_ball(robot, balls, reached_radius=0.2) is None


def test_nearest_ball_skips_targets_inside_default_pickup_radius():
    robot = RobotPose(x=0.0, y=0.0, yaw=0.0)
    balls = [
        {"name": "inside_pickup_radius", "x": 0.24, "y": 0.0},
        {"name": "next_target", "x": 0.8, "y": 0.0},
    ]

    assert nearest_ball(robot, balls)["name"] == "next_target"


def test_command_rotates_before_driving_when_heading_error_is_large():
    robot = RobotPose(x=0.0, y=0.0, yaw=0.0)
    ball = {"x": 0.0, "y": 2.0}

    command = command_toward_ball(robot, ball)

    assert command.linear_x == 0.0
    assert command.angular_z > 0.0


def test_command_drives_forward_when_aligned():
    robot = RobotPose(x=0.0, y=0.0, yaw=0.0)
    ball = {"x": 2.0, "y": 0.0}

    command = command_toward_ball(robot, ball)

    assert 0.0 < command.linear_x <= 0.45
    assert abs(command.angular_z) < 1e-9


def test_wrap_angle_keeps_values_inside_pi_range():
    assert -math.pi <= wrap_angle(4.0) <= math.pi
    assert -math.pi <= wrap_angle(-4.0) <= math.pi
