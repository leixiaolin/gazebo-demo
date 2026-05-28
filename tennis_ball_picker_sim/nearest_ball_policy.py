"""Minimal navigation policy for approaching deterministic tennis balls."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class RobotPose:
    """Planar robot pose in the world frame."""

    x: float
    y: float
    yaw: float


@dataclass(frozen=True)
class VelocityCommand:
    """Planar velocity command."""

    linear_x: float
    angular_z: float


def wrap_angle(angle):
    """Wrap an angle to [-pi, pi]."""
    return math.atan2(math.sin(angle), math.cos(angle))


def nearest_ball(robot_pose, balls, reached_radius=0.22):
    """Return the nearest unreached ball dictionary from a scenario manifest."""
    candidates = []
    for ball in balls:
        dx = ball["x"] - robot_pose.x
        dy = ball["y"] - robot_pose.y
        distance = math.hypot(dx, dy)
        if distance > reached_radius:
            candidates.append((distance, ball))

    if not candidates:
        return None

    return min(candidates, key=lambda item: item[0])[1]


def command_toward_ball(
    robot_pose,
    ball,
    max_linear_speed=0.45,
    max_angular_speed=1.2,
    heading_tolerance=0.25,
):
    """Compute a conservative cmd_vel command toward a ball."""
    dx = ball["x"] - robot_pose.x
    dy = ball["y"] - robot_pose.y
    distance = math.hypot(dx, dy)
    target_heading = math.atan2(dy, dx)
    heading_error = wrap_angle(target_heading - robot_pose.yaw)

    angular_z = max(-max_angular_speed, min(max_angular_speed, 1.8 * heading_error))
    if abs(heading_error) > heading_tolerance:
        linear_x = 0.0
    else:
        linear_x = min(max_linear_speed, 0.7 * distance)

    return VelocityCommand(linear_x=linear_x, angular_z=angular_z)
