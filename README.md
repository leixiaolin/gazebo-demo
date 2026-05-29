# Tennis Ball Picker Gazebo Demo

本仓库是一个用于网球拾取机器人的 ROS 2 + Gazebo Sim MVP：

- 带场线、球网、围栏、光照和摩擦设置的硬地网球场世界
- 带碰撞体的实体球网、网柱和场地围栏，用于把机器人和网球限制在球场区域内
- 简化的差速驱动拾球机器人，包含实体拾球口、导向板、储球仓、相机和激光雷达
- 可通过 ROS 2 launch 参数复现的随机网球散布场景

## 环境要求

请安装支持 Gazebo Sim 集成的 ROS 2 发行版，以及 `ros_gz_sim`。
本项目的 launch 文件面向现代 Gazebo Sim 栈，而不是 Gazebo Classic。

推荐环境：

- Ubuntu 22.04
- ROS 2 Humble
- 通过 `ros-humble-ros-gz` 安装 Gazebo Fortress

安装 ROS 2 后，典型的 Ubuntu 依赖安装命令如下：

```bash
sudo apt install ros-${ROS_DISTRO}-ros-gz ros-${ROS_DISTRO}-ros-gz-bridge
```

检查环境：

```bash
bash scripts/ros_setup_check.sh
```

## 构建

在包含本 package 的 workspace 根目录中运行：

```bash
colcon build --symlink-install
source install/setup.bash
```

## 运行

启动球场、机器人和 50 个随机散布的网球：

```bash
ros2 launch tennis_ball_picker_sim p0_demo.launch.py
```

在比较算法或记录实验时，可以使用确定性 seed：

```bash
ros2 launch tennis_ball_picker_sim p0_demo.launch.py ball_count:=50 seed:=20260528
```

启动 Gazebo 的同时保存同一份场景 manifest：

```bash
ros2 launch tennis_ball_picker_sim p0_demo.launch.py \
  ball_count:=50 \
  seed:=20260528 \
  manifest_output:=runs/hard_court_seed_20260528.json
```

快速进行可视化检查：

```bash
ros2 launch tennis_ball_picker_sim p0_demo.launch.py ball_count:=12 seed:=7
```

启动包含 ROS-Gazebo bridge 的完整手动驾驶 demo：

```bash
ros2 launch tennis_ball_picker_sim teleop_demo.launch.py
```

启动最近网球自主驾驶 demo：

```bash
ros2 launch tennis_ball_picker_sim autonomy_demo.launch.py ball_count:=50 seed:=42
```

运行仅服务端的 smoke test：

```bash
ros2 launch tennis_ball_picker_sim p0_demo.launch.py ball_count:=5 seed:=7 headless:=true
```

## 测试

运行用于验证确定性网球放置的 Python 测试：

```bash
python3 -m pytest test
```

在不启动 Gazebo 的情况下运行静态 P0 校验器：

```bash
ros2 run tennis_ball_picker_sim validate_p0_demo --root .
```

校验器会检查默认 P0 launch 参数、必需资源、XML 有效性、球场边界碰撞体、机器人 topic，以及默认 50 球场景的边界和间距。

在不启动 Gazebo 的情况下打印确定性网球放置 manifest：

```bash
ros2 run tennis_ball_picker_sim print_ball_scenario --ball-count 50 --seed 42
```

在不启动 Gazebo 的情况下保存 manifest：

```bash
ros2 run tennis_ball_picker_sim print_ball_scenario \
  --ball-count 50 \
  --seed 20260528 \
  --output runs/hard_court_seed_20260528.json
```

## P0 验收

在不启动 Gazebo 的情况下运行静态 P0 校验器：

```bash
ros2 run tennis_ball_picker_sim validate_p0_demo --root .
```

运行 headless 运行时 P0 smoke test：

```bash
bash scripts/runtime_p0_smoke_test.sh
```

运行时 smoke test 会以 50 个球、`seed:=42`、`headless:=true` 启动 `p0_demo.launch.py`，并写入 `runs/p0_seed_42.json`。如果 `ros_gz_bridge` 可用，它还会检查 ROS graph 上是否出现 `/clock` 和 `/ball_picker/odom`。

手动运行 GUI P0 demo：

```bash
ros2 launch tennis_ball_picker_sim p0_demo.launch.py \
  ball_count:=50 \
  seed:=42 \
  manifest_output:=runs/p0_seed_42.json
```

构建并运行完整测试链：

```bash
bash scripts/build_and_smoke_test.sh
```

## 遥操作接口

机器人 SDF 包含一个 Gazebo DiffDrive plugin，监听：

```text
/ball_picker/cmd_vel
```

它会在以下 topic 发布里程计：

```text
/ball_picker/odom
```

添加 ROS 侧遥操作、Nav2 或自主拾取控制器时，请使用 `ros_gz_bridge` 桥接这些 topic。

随附的 bridge launch 会映射：

```text
/clock
/ball_picker/cmd_vel
/ball_picker/odom
/ball_picker/front_camera/image
/ball_picker/front_camera/camera_info
/ball_picker/scan
/ball_picker/imu
```

运行 `teleop_demo.launch.py` 后，可以从 ROS 2 teleop 或控制器节点向 `/ball_picker/cmd_vel` 发送速度命令。

机器人 SDF 包含前置 RGB 相机、前置 2D LiDAR 和 IMU，因此后续阶段可以在不改变基础仿真入口的前提下，添加类似颜色/深度感知的网球检测、避障和状态估计。
world 会加载 Gazebo Sensors 和 IMU systems，所以这些传感器 topic 会由相同的 `tennis_court.launch.py` 和 `teleop_demo.launch.py` 入口产生。

## 自主 Demo

`autonomy_demo.launch.py` 会运行同一套确定性网球场景，并启动 `nearest_ball_driver`。该 driver 订阅 `/ball_picker/odom`，从基于 seed 的场景 manifest 中选择最近且尚未到达的网球，并向 `/ball_picker/cmd_vel` 发布保守的速度命令。

这有意保持为一个简单的接口 smoke test，而不是最终的拾球规划器：它用于证明机器人、bridge、里程计、命令 topic 和随机网球 manifest 已经连通。

## MVP 范围

这是仿真计划中的 P0 基础。它证明环境、机器人资源和随机网球分布可以被可复现地启动。拾球成功逻辑、检测、Nav2、评估报告以及 sim-to-real 标定仍属于后续阶段。
