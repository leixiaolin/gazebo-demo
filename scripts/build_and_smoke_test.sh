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
python3 -m tennis_ball_picker_sim.p0_validator --root .
colcon build --symlink-install

# shellcheck disable=SC1091
source install/setup.bash
RUNTIME_SECONDS="${RUNTIME_SECONDS:-25}" bash "${SCRIPT_DIR}/runtime_p0_smoke_test.sh"
