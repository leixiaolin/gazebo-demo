#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

BALL_COUNT="${BALL_COUNT:-50}"
SEED="${SEED:-42}"
RUNTIME_SECONDS="${RUNTIME_SECONDS:-25}"
TOPIC_WAIT_SECONDS="${TOPIC_WAIT_SECONDS:-10}"
RUNS_DIR="${RUNS_DIR:-${REPO_ROOT}/runs}"
MANIFEST_OUTPUT="${MANIFEST_OUTPUT:-${RUNS_DIR}/p0_seed_${SEED}.json}"

cd "${REPO_ROOT}"

source_setup() {
  local setup_file="$1"
  set +u
  # shellcheck disable=SC1090
  source "${setup_file}"
  set -u
}

if [[ -f /opt/ros/jazzy/setup.bash ]]; then
  source_setup /opt/ros/jazzy/setup.bash
elif [[ -n "${ROS_DISTRO:-}" && -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]]; then
  source_setup "/opt/ros/${ROS_DISTRO}/setup.bash"
fi

if [[ -f install/setup.bash ]]; then
  source_setup install/setup.bash
fi

if ! command -v ros2 >/dev/null 2>&1; then
  printf 'ros2 command was not found. Build/source a ROS 2 workspace before running runtime smoke test.\n' >&2
  exit 1
fi

mkdir -p "${RUNS_DIR}"

if ros2 pkg prefix tennis_ball_picker_sim >/dev/null 2>&1; then
  ros2 run tennis_ball_picker_sim validate_p0_demo --root .
else
  python3 -m tennis_ball_picker_sim.p0_validator --root .
fi

P0_LOG="${RUNS_DIR}/runtime_p0_launch.log"
BRIDGE_LOG="${RUNS_DIR}/runtime_p0_bridge.log"
TOPICS_LOG="${RUNS_DIR}/runtime_p0_topics.txt"

p0_pid=""
bridge_pid=""

cleanup() {
  for pid in "${bridge_pid}" "${p0_pid}"; do
    if [[ -n "${pid}" ]] && kill -0 "${pid}" >/dev/null 2>&1; then
      kill -INT "${pid}" >/dev/null 2>&1 || true
      wait "${pid}" >/dev/null 2>&1 || true
    fi
  done
}
trap cleanup EXIT

ros2 launch tennis_ball_picker_sim p0_demo.launch.py \
  ball_count:="${BALL_COUNT}" \
  seed:="${SEED}" \
  headless:=true \
  manifest_output:="${MANIFEST_OUTPUT}" \
  >"${P0_LOG}" 2>&1 &
p0_pid=$!

if ros2 pkg prefix ros_gz_bridge >/dev/null 2>&1; then
  ros2 launch tennis_ball_picker_sim bridge.launch.py >"${BRIDGE_LOG}" 2>&1 &
  bridge_pid=$!
fi

sleep "${TOPIC_WAIT_SECONDS}"

if ! kill -0 "${p0_pid}" >/dev/null 2>&1; then
  wait "${p0_pid}" || launch_status=$?
  printf 'P0 launch exited before topic checks. See %s\n' "${P0_LOG}" >&2
  exit "${launch_status:-1}"
fi

if [[ -n "${bridge_pid}" ]]; then
  ros2 topic list >"${TOPICS_LOG}" || true
  for topic in /clock /ball_picker/odom; do
    if ! grep -Fxq "${topic}" "${TOPICS_LOG}"; then
      printf 'Expected ROS topic %s was not listed. See %s and %s\n' "${topic}" "${TOPICS_LOG}" "${BRIDGE_LOG}" >&2
      exit 1
    fi
  done
else
  printf 'ros_gz_bridge package not found; skipping ROS topic presence checks.\n'
fi

end_time=$((SECONDS + RUNTIME_SECONDS - TOPIC_WAIT_SECONDS))
while kill -0 "${p0_pid}" >/dev/null 2>&1 && (( SECONDS < end_time )); do
  sleep 1
done

if kill -0 "${p0_pid}" >/dev/null 2>&1; then
  kill -INT "${p0_pid}" >/dev/null 2>&1 || true
fi

set +e
wait "${p0_pid}"
launch_status=$?
set -e
p0_pid=""

if [[ "${launch_status}" -ne 0 && "${launch_status}" -ne 124 && "${launch_status}" -ne 130 && "${launch_status}" -ne 143 ]]; then
  printf 'P0 launch exited with status %s. See %s\n' "${launch_status}" "${P0_LOG}" >&2
  exit "${launch_status}"
fi

if [[ ! -f "${MANIFEST_OUTPUT}" ]]; then
  printf 'Expected manifest was not written: %s\n' "${MANIFEST_OUTPUT}" >&2
  exit 1
fi

printf 'Runtime P0 smoke test completed. Manifest: %s\n' "${MANIFEST_OUTPUT}"
