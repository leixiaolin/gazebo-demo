#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

if [[ -f /opt/ros/jazzy/setup.bash ]]; then
  # shellcheck disable=SC1091
  source /opt/ros/jazzy/setup.bash
elif [[ -n "${ROS_DISTRO:-}" && -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]]; then
  # shellcheck disable=SC1090
  source "/opt/ros/${ROS_DISTRO}/setup.bash"
fi

"${SCRIPT_DIR}/ros_setup_check.sh"

python3 -m pytest test
colcon build --symlink-install

# shellcheck disable=SC1091
source install/setup.bash

set +e
timeout --signal=INT 25s ros2 launch tennis_ball_picker_sim tennis_court.launch.py \
  ball_count:=5 seed:=7 headless:=true
launch_status=$?
set -e

if [[ "${launch_status}" -ne 0 && "${launch_status}" -ne 124 && "${launch_status}" -ne 130 ]]; then
  exit "${launch_status}"
fi

printf 'Headless Gazebo smoke test completed with status %s\n' "${launch_status}"
