"""ROS 2 node that drives the robot toward the nearest deterministic ball."""

import math

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node

from tennis_ball_picker_sim.nearest_ball_policy import (
    RobotPose,
    command_toward_ball,
    nearest_ball,
    wrap_angle,
)
from tennis_ball_picker_sim.scenario import build_scenario


def _yaw_from_quaternion(quaternion):
    siny_cosp = 2.0 * (
        quaternion.w * quaternion.z + quaternion.x * quaternion.y
    )
    cosy_cosp = 1.0 - 2.0 * (
        quaternion.y * quaternion.y + quaternion.z * quaternion.z
    )
    return math.atan2(siny_cosp, cosy_cosp)


class NearestBallDriver(Node):
    """A small demo controller for validating the robot command interface."""

    def __init__(self):
        super().__init__("nearest_ball_driver")
        self.declare_parameter("ball_count", 50)
        self.declare_parameter("seed", 42)
        self.declare_parameter("reached_radius", 0.22)

        ball_count = self.get_parameter("ball_count").value
        seed = self.get_parameter("seed").value
        self._balls = build_scenario(ball_count, seed)["balls"]
        self._reached_radius = self.get_parameter("reached_radius").value
        self._latest_pose = None
        self._log_counter = 0

        self._publisher = self.create_publisher(Twist, "/ball_picker/cmd_vel", 10)
        self.create_subscription(Odometry, "/ball_picker/odom", self._on_odom, 10)
        self.create_timer(0.1, self._on_timer)

        self.get_logger().info(
            f"Driving toward nearest ball from deterministic scenario seed={seed}, count={ball_count}"
        )

    def _on_odom(self, msg):
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        self._latest_pose = RobotPose(
            x=position.x,
            y=position.y,
            yaw=_yaw_from_quaternion(orientation),
        )

    def _on_timer(self):
        if self._latest_pose is None:
            return

        target = nearest_ball(
            self._latest_pose,
            self._balls,
            reached_radius=self._reached_radius,
        )
        twist = Twist()

        if target is not None:
            command = command_toward_ball(self._latest_pose, target)
            twist.linear.x = command.linear_x
            twist.angular.z = command.angular_z

            self._log_counter += 1
            if self._log_counter >= 10:
                self._log_counter = 0
                target_name = target.get("name", "unknown")
                dx = target["x"] - self._latest_pose.x
                dy = target["y"] - self._latest_pose.y
                distance = math.hypot(dx, dy)
                target_heading = math.atan2(dy, dx)
                heading_error = wrap_angle(target_heading - self._latest_pose.yaw)
                mode = "aligning" if twist.linear.x == 0.0 else "driving"
                self.get_logger().info(
                    f"mode={mode} pos=({self._latest_pose.x:.2f}, {self._latest_pose.y:.2f}) "
                    f"yaw={math.degrees(self._latest_pose.yaw):.1f}deg "
                    f"target={target_name}({target['x']:.2f}, {target['y']:.2f}) "
                    f"target_heading={math.degrees(target_heading):.1f}deg "
                    f"heading_error={math.degrees(heading_error):.1f}deg "
                    f"distance={distance:.2f}m "
                    f"cmd=(linear={twist.linear.x:.2f}, angular={twist.angular.z:.2f})"
                )

        self._publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = NearestBallDriver()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
