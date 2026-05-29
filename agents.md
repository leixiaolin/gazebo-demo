# Agents Guide

This repository is a ROS 2 + Gazebo Sim MVP for a tennis ball picking robot. Treat it as a reproducible simulation foundation first: the court, robot asset, seeded ball scenarios, topic bridges, and smoke-testable launch files are the main contract.

## Project Shape

- Package name: `tennis_ball_picker_sim`
- Runtime stack: ROS 2, Gazebo Sim, `ros_gz_sim`, `ros_gz_bridge`
- Python package: deterministic scenarios, ball scattering, static P0 validation, and a minimal nearest-ball autonomy driver
- Assets: SDF worlds and models under `worlds/` and `models/`
- Launch entry points live in `launch/`
- Tests live in `test/`

## Core Contracts

Keep these stable unless the task explicitly changes the acceptance target:

- `p0_demo.launch.py` defaults to `ball_count:=50`, `seed:=42`, `headless:=false`, and `manifest_output:=`.
- The deterministic ball manifest is produced by `tennis_ball_picker_sim.scenario.build_scenario`.
- Ball placement must stay reproducible for the same seed, inside court bounds, separated by at least `0.34 m`, clear of the initial robot staging area, and clear of the net line.
- The robot command topic is `/ball_picker/cmd_vel`.
- The robot odometry topic is `/ball_picker/odom`.
- Bridge coverage should preserve `/clock`, odometry, command velocity, camera, lidar, and IMU topics.
- `validate_p0_demo --root .` is the static gate for required assets, XML validity, launch defaults, topic tokens, boundary collisions, dependencies, and default scenario sanity.

## Development Workflow

Before editing, inspect the existing file and nearby tests. This repo is small, so prefer narrow changes over new abstractions.

Useful commands:

```bash
python3 -m pytest test
ros2 run tennis_ball_picker_sim validate_p0_demo --root .
bash scripts/build_and_smoke_test.sh
bash scripts/runtime_p0_smoke_test.sh
```

Use the ROS/Gazebo commands only in an environment where ROS 2 and Gazebo Sim are installed. If that stack is unavailable, still run the pure Python tests when possible and state what could not be verified.

## Editing Rules

- Keep Python code simple and deterministic.
- Prefer standard library modules already in use unless a ROS dependency is required.
- Preserve SDF/XML validity when editing assets.
- Do not rename launch arguments, topics, models, or package entry points casually; tests and README examples depend on them.
- When changing a default seed, count, court dimension, model path, or topic, update README, tests, and `p0_validator.py` together.
- Keep generated run outputs out of version control unless a task explicitly asks for a committed fixture.

## Simulation Boundaries

This project does not yet prove real pickup performance. Gazebo is being used to validate system wiring, repeatable scenarios, interface contracts, and early autonomy flow. Do not represent the current nearest-ball driver as a production planner, and do not treat SDF contact behavior as a calibrated mechanical pickup model.

Future work should make success criteria explicit before implementation: pickup plugin semantics, detection pipeline, Nav2 integration, metrics, rosbag recording, sim-to-real calibration, and physical rig validation are separate milestones.


## 任务完成报告

对非纯问答的开发任务，最终回复必须包含：

- `本轮完成度:X%`
- 本轮主目标是否完成
- 已执行的验证
- 剩余缺口
- `下一刀`

如果任务属于路线图、长期任务或多阶段目标，还要包含：

- `整体目标完成度:Y%`
- 百分比计算依据
