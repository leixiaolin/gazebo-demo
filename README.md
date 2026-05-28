# Tennis Ball Picker Gazebo Demo

This repository contains a ROS 2 + Gazebo Sim MVP for a tennis ball picking robot:

- a hard tennis court world with lines, net, perimeter fence, lighting, and friction settings
- physical net, net posts, and perimeter fence collisions to keep the robot and balls inside the court area
- a simplified differential-drive ball picker robot with a physical pickup mouth, guide plates, hopper, camera, and lidar
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
ros2 launch tennis_ball_picker_sim p0_demo.launch.py
```

Use a deterministic seed when comparing algorithms or recording experiments:

```bash
ros2 launch tennis_ball_picker_sim p0_demo.launch.py ball_count:=50 seed:=20260528
```

Save the same manifest while launching Gazebo:

```bash
ros2 launch tennis_ball_picker_sim p0_demo.launch.py \
  ball_count:=50 \
  seed:=20260528 \
  manifest_output:=runs/hard_court_seed_20260528.json
```

For quick visual checks:

```bash
ros2 launch tennis_ball_picker_sim p0_demo.launch.py ball_count:=12 seed:=7
```

Launch the complete manual-driving demo with ROS-Gazebo bridges:

```bash
ros2 launch tennis_ball_picker_sim teleop_demo.launch.py
```

Launch the nearest-ball autonomy demo:

```bash
ros2 launch tennis_ball_picker_sim autonomy_demo.launch.py ball_count:=50 seed:=42
```

For a server-only smoke test:

```bash
ros2 launch tennis_ball_picker_sim p0_demo.launch.py ball_count:=5 seed:=7 headless:=true
```

## Test

Run the Python tests for deterministic ball placement:

```bash
python3 -m pytest test
```

Run the static P0 validator without launching Gazebo:

```bash
ros2 run tennis_ball_picker_sim validate_p0_demo --root .
```

The validator checks the default P0 launch arguments, required assets, XML validity, court boundary collisions, robot topics, and default 50-ball scenario bounds/separation.

Print the deterministic ball placement manifest without launching Gazebo:

```bash
ros2 run tennis_ball_picker_sim print_ball_scenario --ball-count 50 --seed 42
```

Save the manifest without launching Gazebo:

```bash
ros2 run tennis_ball_picker_sim print_ball_scenario \
  --ball-count 50 \
  --seed 20260528 \
  --output runs/hard_court_seed_20260528.json
```

## P0 Acceptance

Run the static P0 validator without starting Gazebo:

```bash
ros2 run tennis_ball_picker_sim validate_p0_demo --root .
```

Run the headless runtime P0 smoke test:

```bash
bash scripts/runtime_p0_smoke_test.sh
```

The runtime smoke test launches `p0_demo.launch.py` with 50 balls, `seed:=42`, `headless:=true`, and writes `runs/p0_seed_42.json`. If `ros_gz_bridge` is available, it also checks that `/clock` and `/ball_picker/odom` appear on the ROS graph.

Run the GUI P0 demo manually:

```bash
ros2 launch tennis_ball_picker_sim p0_demo.launch.py \
  ball_count:=50 \
  seed:=42 \
  manifest_output:=runs/p0_seed_42.json
```

Build and run the full test chain:

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

The included bridge launch maps:

```text
/clock
/ball_picker/cmd_vel
/ball_picker/odom
/ball_picker/front_camera/image
/ball_picker/front_camera/camera_info
/ball_picker/scan
/ball_picker/imu
```

After running `teleop_demo.launch.py`, send velocity commands to `/ball_picker/cmd_vel` from ROS 2 teleop or a controller node.

The robot SDF includes a front RGB camera, a front 2D LiDAR, and an IMU so the next stages can add color/depth-inspired ball detection, obstacle avoidance, and state estimation without changing the base simulation entry point.
The world loads Gazebo Sensors and IMU systems, so these sensor topics are produced by the same `tennis_court.launch.py` and `teleop_demo.launch.py` entry points.

## Autonomy Demo

`autonomy_demo.launch.py` runs the same deterministic ball scenario and starts `nearest_ball_driver`. The driver subscribes to `/ball_picker/odom`, selects the nearest unreached ball from the seed-based scenario manifest, and publishes conservative velocity commands to `/ball_picker/cmd_vel`.

This is intentionally a simple interface smoke test rather than a final pickup planner: it proves the robot, bridge, odometry, command topic, and random-ball manifest are wired together.

## MVP Scope

This is the P0 foundation from the simulation plan. It proves that the environment, robot asset, and randomized ball distribution can be launched reproducibly. Pickup success logic, detection, Nav2, evaluation reports, and sim-to-real calibration remain later stages.
