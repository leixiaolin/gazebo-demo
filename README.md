# Tennis Ball Picker Gazebo Demo

This repository contains a ROS 2 + Gazebo Sim MVP for a tennis ball picking robot:

- a hard tennis court world with lines, net, perimeter fence, lighting, and friction settings
- a simplified differential-drive ball picker robot with pickup mouth, hopper, camera, and lidar placeholders
- reproducible random tennis ball scattering through ROS 2 launch arguments

## Requirements

Install a ROS 2 distribution that supports Gazebo Sim integration, plus `ros_gz_sim`.
The launch file targets the modern Gazebo Sim stack rather than Gazebo Classic.

Recommended stack:

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic through `ros-jazzy-ros-gz`

Typical Ubuntu setup after ROS 2 is installed:

```bash
sudo apt install ros-${ROS_DISTRO}-ros-gz ros-${ROS_DISTRO}-ros-gz-bridge
```

Check the environment:

```bash
bash scripts/ros_setup_check.sh
```

## Docker

If you do not want to install ROS 2 and Gazebo directly on the host, build the included container:

```bash
docker compose -f docker/compose.yaml build
docker compose -f docker/compose.yaml run --rm sim
```

For Docker Compose v1, use:

```bash
docker-compose -f docker/compose.yaml build
docker-compose -f docker/compose.yaml run --rm sim
```

Inside the container:

```bash
bash scripts/build_and_smoke_test.sh
```

## Build

From the workspace root that contains this package:

```bash
colcon build --symlink-install
source install/setup.bash
```

## Run

Launch the court, robot, and 50 randomly scattered tennis balls:

```bash
ros2 launch tennis_ball_picker_sim tennis_court.launch.py
```

Use a deterministic seed when comparing algorithms or recording experiments:

```bash
ros2 launch tennis_ball_picker_sim tennis_court.launch.py ball_count:=50 seed:=20260528
```

For quick visual checks:

```bash
ros2 launch tennis_ball_picker_sim tennis_court.launch.py ball_count:=12 seed:=7
```

For a server-only smoke test:

```bash
ros2 launch tennis_ball_picker_sim tennis_court.launch.py ball_count:=5 seed:=7 headless:=true
```

## Test

Run the Python tests for deterministic ball placement:

```bash
python3 -m pytest test
```

Build and run a short headless Gazebo smoke test:

```bash
bash scripts/build_and_smoke_test.sh
```

## Teleoperation Hook

The robot SDF includes a Gazebo DiffDrive plugin listening on:

```text
/ball_picker/cmd_vel
```

It publishes odometry on:

```text
/ball_picker/odom
```

Bridge these topics with `ros_gz_bridge` when adding ROS-side teleoperation, Nav2, or an autonomous pickup controller.

## MVP Scope

This is the P0 foundation from the simulation plan. It proves that the environment, robot asset, and randomized ball distribution can be launched reproducibly. Pickup success logic, detection, Nav2, evaluation reports, and sim-to-real calibration remain later stages.
