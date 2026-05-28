#!/usr/bin/env bash
set -euo pipefail

if [[ -f /opt/ros/jazzy/setup.bash ]]; then
  # shellcheck disable=SC1091
  source /opt/ros/jazzy/setup.bash
elif [[ -n "${ROS_DISTRO:-}" && -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]]; then
  # shellcheck disable=SC1090
  source "/opt/ros/${ROS_DISTRO}/setup.bash"
fi

missing=()
for command_name in ros2 colcon gz; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    missing+=("${command_name}")
  fi
done

for package_name in ros_gz_sim ros_gz_bridge; do
  if ! ros2 pkg prefix "${package_name}" >/dev/null 2>&1; then
    missing+=("ROS package ${package_name}")
  fi
done

if (( ${#missing[@]} > 0 )); then
  printf 'Missing required tools/packages:\n' >&2
  printf '  - %s\n' "${missing[@]}" >&2
  exit 1
fi

printf 'ROS_DISTRO=%s\n' "${ROS_DISTRO:-unknown}"
ros2 pkg prefix ros_gz_sim
gz sim --versions
