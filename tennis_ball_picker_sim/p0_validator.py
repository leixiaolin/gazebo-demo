"""Static P0 validator for the tennis ball picker Gazebo demo."""

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from tennis_ball_picker_sim.scenario import build_scenario
from tennis_ball_picker_sim.scatter import COURT_HALF_LENGTH, COURT_HALF_WIDTH


REQUIRED_FILES = [
    "package.xml",
    "worlds/tennis_court.sdf",
    "models/ball_picker/ball_picker.sdf",
    "models/ball_picker/model.config",
    "models/tennis_ball/tennis_ball.sdf",
    "models/tennis_ball/model.config",
    "launch/p0_demo.launch.py",
    "launch/tennis_court.launch.py",
    "config/hard_court_50.yaml",
]


REQUIRED_WORLD_FEATURES = {
    "hard_tennis_court",
    "court_lines",
    "net",
    "perimeter_fence",
}


REQUIRED_ROBOT_STRINGS = {
    "pickup_mouth_collision",
    "left_pickup_guide_collision",
    "right_pickup_guide_collision",
    "gz-sim-diff-drive-system",
    "/ball_picker/cmd_vel",
    "/ball_picker/odom",
    "/ball_picker/front_camera/image",
    "/ball_picker/front_camera/camera_info",
    "/ball_picker/scan",
    "/ball_picker/imu",
}


REQUIRED_BOUNDARY_COLLISIONS = {
    "net_collision",
    "net_post_east_collision",
    "net_post_west_collision",
    "fence_north_collision",
    "fence_south_collision",
    "fence_east_collision",
    "fence_west_collision",
}


REQUIRED_EXEC_DEPENDS = {
    "ament_index_python",
    "geometry_msgs",
    "launch",
    "launch_ros",
    "nav_msgs",
    "rclpy",
    "ros_gz_bridge",
    "ros_gz_sim",
    "rosgraph_msgs",
    "sensor_msgs",
}


def _parse_xml(path):
    ET.parse(path)


def _record_check(checks, name, ok, detail):
    checks.append({"name": name, "ok": ok, "detail": detail})


def validate_p0(root, ball_count=50, seed=42):
    """Return a JSON-serializable static validation report."""
    root = Path(root)
    failures = []
    checks = []

    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        exists = path.exists()
        _record_check(checks, f"file:{relative_path}", exists, str(path))
        if not exists:
            failures.append(f"missing file: {relative_path}")

    parsed_xml = {}
    xml_files = [
        "worlds/tennis_court.sdf",
        "models/ball_picker/ball_picker.sdf",
        "models/ball_picker/model.config",
        "models/tennis_ball/tennis_ball.sdf",
        "models/tennis_ball/model.config",
        "package.xml",
    ]
    for relative_path in xml_files:
        path = root / relative_path
        if path.exists():
            try:
                parsed_xml[relative_path] = ET.parse(path)
                _record_check(checks, f"xml:{relative_path}", True, "parsed")
            except ET.ParseError as exc:
                _record_check(checks, f"xml:{relative_path}", False, str(exc))
                failures.append(f"invalid XML: {relative_path}: {exc}")

    world_path = root / "worlds" / "tennis_court.sdf"
    robot_path = root / "models" / "ball_picker" / "ball_picker.sdf"
    launch_path = root / "launch" / "p0_demo.launch.py"

    world_text = world_path.read_text(encoding="utf-8")
    robot_text = robot_path.read_text(encoding="utf-8")
    launch_text = launch_path.read_text(encoding="utf-8")

    for feature in REQUIRED_WORLD_FEATURES:
        ok = feature in world_text
        _record_check(checks, f"world_feature:{feature}", ok, feature)
        if not ok:
            failures.append(f"world missing feature: {feature}")
    for token in REQUIRED_ROBOT_STRINGS:
        ok = token in robot_text
        _record_check(checks, f"robot_token:{token}", ok, token)
        if not ok:
            failures.append(f"robot missing token: {token}")

    world_xml = parsed_xml.get("worlds/tennis_court.sdf")
    if world_xml is not None:
        collision_names = {
            collision.attrib["name"]
            for collision in world_xml.findall(".//collision")
        }
        missing_collisions = REQUIRED_BOUNDARY_COLLISIONS - collision_names
        _record_check(
            checks,
            "world_boundary_collisions",
            not missing_collisions,
            sorted(REQUIRED_BOUNDARY_COLLISIONS),
        )
        for collision in sorted(missing_collisions):
            failures.append(f"world missing boundary collision: {collision}")
    else:
        _record_check(
            checks,
            "world_boundary_collisions",
            False,
            "worlds/tennis_court.sdf XML unavailable",
        )

    package_xml = parsed_xml.get("package.xml")
    if package_xml is not None:
        exec_depends = {
            element.text
            for element in package_xml.findall(".//exec_depend")
            if element.text
        }
        missing_depends = REQUIRED_EXEC_DEPENDS - exec_depends
        _record_check(
            checks,
            "package:exec_depends",
            not missing_depends,
            sorted(REQUIRED_EXEC_DEPENDS),
        )
        for dependency in sorted(missing_depends):
            failures.append(f"package.xml missing exec_depend: {dependency}")
    else:
        _record_check(
            checks,
            "package:exec_depends",
            False,
            "package.xml unavailable",
        )

    launch_requirements = {
        'DeclareLaunchArgument("ball_count", default_value="50")': "default 50 balls",
        'DeclareLaunchArgument("seed", default_value="42")': "default seed 42",
        'DeclareLaunchArgument("headless", default_value="false")': "headless option",
        'DeclareLaunchArgument("manifest_output", default_value="")': "manifest output option",
    }
    for token, detail in launch_requirements.items():
        ok = token in launch_text
        _record_check(checks, f"launch:{detail}", ok, token)
        if not ok:
            failures.append(f"p0 launch missing {detail}")

    manifest = build_scenario(ball_count, seed)
    ball_total_ok = len(manifest["balls"]) == ball_count
    _record_check(
        checks,
        "scenario:ball_count",
        ball_total_ok,
        f"{len(manifest['balls'])}/{ball_count}",
    )
    if not ball_total_ok:
        failures.append(
            f"scenario generated {len(manifest['balls'])} balls, expected {ball_count}"
        )

    balls_inside = all(
        -COURT_HALF_LENGTH < ball["x"] < COURT_HALF_LENGTH
        and -COURT_HALF_WIDTH < ball["y"] < COURT_HALF_WIDTH
        for ball in manifest["balls"]
    )
    _record_check(checks, "scenario:balls_inside_court", balls_inside, "court bounds")
    if not balls_inside:
        failures.append("scenario contains balls outside the tennis court bounds")

    min_squared_distance = min(
        (
            (first["x"] - second["x"]) ** 2 + (first["y"] - second["y"]) ** 2
            for index, first in enumerate(manifest["balls"])
            for second in manifest["balls"][index + 1 :]
        ),
        default=float("inf"),
    )
    separated = min_squared_distance >= 0.34**2
    _record_check(checks, "scenario:ball_separation", separated, ">= 0.34 m")
    if not separated:
        failures.append("scenario contains balls closer than 0.34 m")

    return {
        "ok": not failures,
        "failures": failures,
        "checks": checks,
        "root": str(root),
        "scenario": {
            "ball_count": manifest["ball_count"],
            "seed": manifest["seed"],
            "world": manifest["world"],
            "first_ball": manifest["balls"][0] if manifest["balls"] else None,
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--ball-count", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)

    report = validate_p0(args.root, ball_count=args.ball_count, seed=args.seed)
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
