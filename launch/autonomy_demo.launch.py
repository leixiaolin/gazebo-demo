"""Launch the court scenario, bridges, and a nearest-ball demo driver."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def _package_launch_file(name):
    return PathJoinSubstitution(
        [FindPackageShare("tennis_ball_picker_sim"), "launch", name]
    )


def generate_launch_description():
    ball_count = LaunchConfiguration("ball_count")
    seed = LaunchConfiguration("seed")
    headless = LaunchConfiguration("headless")
    manifest_output = LaunchConfiguration("manifest_output")

    return LaunchDescription(
        [
            DeclareLaunchArgument("ball_count", default_value="50"),
            DeclareLaunchArgument("seed", default_value="42"),
            DeclareLaunchArgument("headless", default_value="false"),
            DeclareLaunchArgument("manifest_output", default_value=""),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(_package_launch_file("tennis_court.launch.py")),
                launch_arguments={
                    "ball_count": ball_count,
                    "seed": seed,
                    "headless": headless,
                    "manifest_output": manifest_output,
                }.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(_package_launch_file("bridge.launch.py"))
            ),
            Node(
                package="tennis_ball_picker_sim",
                executable="nearest_ball_driver",
                name="nearest_ball_driver",
                output="screen",
                parameters=[
                    {
                        "ball_count": ball_count,
                        "seed": seed,
                    }
                ],
            ),
        ]
    )
