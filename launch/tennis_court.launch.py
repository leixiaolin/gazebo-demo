"""Launch a tennis court in Gazebo and scatter tennis balls reproducibly."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.substitutions import FindPackageShare

from tennis_ball_picker_sim.scatter import BALL_RADIUS, sample_ball_positions


def _spawn_entities(context):
    package_share = Path(get_package_share_directory("tennis_ball_picker_sim"))
    world_name = LaunchConfiguration("world_name").perform(context)
    ball_count = int(LaunchConfiguration("ball_count").perform(context))
    seed = int(LaunchConfiguration("seed").perform(context))

    robot_file = package_share / "models" / "ball_picker" / "ball_picker.sdf"
    ball_file = package_share / "models" / "tennis_ball" / "tennis_ball.sdf"
    positions = sample_ball_positions(ball_count, seed)

    actions = [
        ExecuteProcess(
            cmd=[
                "ros2",
                "run",
                "ros_gz_sim",
                "create",
                "-world",
                world_name,
                "-name",
                "ball_picker",
                "-file",
                str(robot_file),
                "-x",
                "0.0",
                "-y",
                "-4.75",
                "-z",
                "0.08",
                "-Y",
                "1.5708",
            ],
            output="screen",
        )
    ]

    for index, position in enumerate(positions):
        actions.append(
            ExecuteProcess(
                cmd=[
                    "ros2",
                    "run",
                    "ros_gz_sim",
                    "create",
                    "-world",
                    world_name,
                    "-name",
                    f"tennis_ball_{index:02d}",
                    "-file",
                    str(ball_file),
                    "-x",
                    f"{position.x:.3f}",
                    "-y",
                    f"{position.y:.3f}",
                    "-z",
                    f"{BALL_RADIUS + 0.015:.3f}",
                ],
                output="screen",
            )
        )

    return actions


def generate_launch_description():
    world_file = PathJoinSubstitution(
        [FindPackageShare("tennis_ball_picker_sim"), "worlds", "tennis_court.sdf"]
    )
    gz_launch = PathJoinSubstitution(
        [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("ball_count", default_value="50"),
            DeclareLaunchArgument("seed", default_value="42"),
            DeclareLaunchArgument("headless", default_value="false"),
            DeclareLaunchArgument("world_name", default_value="tennis_court"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(gz_launch),
                launch_arguments={
                    "gz_args": [
                        PythonExpression(
                            [
                                "'-r -s ' if '",
                                LaunchConfiguration("headless"),
                                "' == 'true' else '-r '",
                            ]
                        ),
                        world_file,
                    ]
                }.items(),
            ),
            TimerAction(period=3.0, actions=[OpaqueFunction(function=_spawn_entities)]),
        ]
    )
