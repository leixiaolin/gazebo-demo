"""Bridge the ball picker Gazebo topics into ROS 2."""

from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    return LaunchDescription(
        [
            ExecuteProcess(
                cmd=[
                    "ros2",
                    "run",
                    "ros_gz_bridge",
                    "parameter_bridge",
                    "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
                    "/ball_picker/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
                    "/ball_picker/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
                    "/ball_picker/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
                    "/ball_picker/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
                    "/ball_picker/front_camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
                    "/ball_picker/front_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
                ],
                output="screen",
            )
        ]
    )
