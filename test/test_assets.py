from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


def test_required_simulation_assets_exist():
    required_paths = [
        ROOT / "worlds" / "tennis_court.sdf",
        ROOT / "models" / "ball_picker" / "ball_picker.sdf",
        ROOT / "models" / "ball_picker" / "model.config",
        ROOT / "models" / "tennis_ball" / "tennis_ball.sdf",
        ROOT / "models" / "tennis_ball" / "model.config",
        ROOT / "launch" / "tennis_court.launch.py",
        ROOT / "launch" / "p0_demo.launch.py",
        ROOT / "launch" / "bridge.launch.py",
        ROOT / "launch" / "teleop_demo.launch.py",
        ROOT / "launch" / "autonomy_demo.launch.py",
        ROOT / "config" / "hard_court_50.yaml",
        ROOT / "scripts" / "runtime_p0_smoke_test.sh",
    ]

    for path in required_paths:
        assert path.exists(), path


def test_sdf_and_model_config_files_are_valid_xml():
    xml_paths = [
        ROOT / "worlds" / "tennis_court.sdf",
        ROOT / "models" / "ball_picker" / "ball_picker.sdf",
        ROOT / "models" / "ball_picker" / "model.config",
        ROOT / "models" / "tennis_ball" / "tennis_ball.sdf",
        ROOT / "models" / "tennis_ball" / "model.config",
        ROOT / "package.xml",
    ]

    for path in xml_paths:
        ET.parse(path)


def test_package_declares_runtime_message_dependencies():
    package_xml = ET.parse(ROOT / "package.xml")
    exec_depends = {
        element.text
        for element in package_xml.findall(".//exec_depend")
    }

    assert {
        "geometry_msgs",
        "nav_msgs",
        "rosgraph_msgs",
        "sensor_msgs",
    } <= exec_depends


def test_robot_has_drive_plugin_and_pickup_geometry():
    robot_xml = ET.parse(ROOT / "models" / "ball_picker" / "ball_picker.sdf")
    robot_text = ET.tostring(robot_xml.getroot(), encoding="unicode")
    collision_names = {
        collision.attrib["name"]
        for collision in robot_xml.findall(".//collision")
    }

    assert "gz-sim-diff-drive-system" in robot_text
    assert "/ball_picker/cmd_vel" in robot_text
    assert "/ball_picker/odom" in robot_text
    assert "pickup_mouth" in robot_text
    assert "hopper_visual" in robot_text
    assert {
        "pickup_mouth_collision",
        "left_pickup_guide_collision",
        "right_pickup_guide_collision",
    } <= collision_names


def test_robot_drive_wheels_are_oriented_for_ground_traction():
    robot_xml = ET.parse(ROOT / "models" / "ball_picker" / "ball_picker.sdf")
    model = robot_xml.find(".//model")
    assert model is not None

    model_pose = [float(value) for value in model.findtext("pose").split()]
    assert model_pose[2] == 0.025

    for joint_name in ["left_wheel_joint", "right_wheel_joint"]:
        axis = robot_xml.find(f".//joint[@name='{joint_name}']/axis/xyz")
        assert axis is not None
        assert axis.text.strip() == "0 1 0"

    for link_name in ["left_wheel", "right_wheel"]:
        link = robot_xml.find(f".//link[@name='{link_name}']")
        assert link is not None
        link_pose = [float(value) for value in link.findtext("pose").split()]
        radius = float(link.findtext(".//collision/geometry/cylinder/radius"))
        collision_pose = [
            float(value) for value in link.findtext(".//collision/pose").split()
        ]
        visual_pose = [float(value) for value in link.findtext(".//visual/pose").split()]

        assert link_pose[2] == radius
        assert link_pose[3:6] == [0.0, 0.0, 0.0]
        assert collision_pose[3:6] == [1.5708, 0.0, 0.0]
        assert visual_pose[3:6] == [1.5708, 0.0, 0.0]


def test_robot_has_core_sensors_and_ros_bridge_topics():
    robot_xml = ET.parse(ROOT / "models" / "ball_picker" / "ball_picker.sdf")
    sensor_names = {
        sensor.attrib["name"]
        for sensor in robot_xml.findall(".//sensor")
    }
    bridge_text = (ROOT / "launch" / "bridge.launch.py").read_text()

    assert {"front_rgb_camera", "front_lidar", "imu"} <= sensor_names

    for topic in [
        "/ball_picker/front_camera/image",
        "/ball_picker/front_camera/camera_info",
        "/ball_picker/scan",
        "/ball_picker/imu",
    ]:
        assert topic in ET.tostring(robot_xml.getroot(), encoding="unicode")
        assert topic in bridge_text


def test_launch_files_support_manifest_output():
    for launch_name in [
        "tennis_court.launch.py",
        "p0_demo.launch.py",
        "teleop_demo.launch.py",
        "autonomy_demo.launch.py",
    ]:
        launch_text = (ROOT / "launch" / launch_name).read_text()
        assert "manifest_output" in launch_text


def test_smoke_test_uses_p0_entrypoint_and_validator():
    script_text = (ROOT / "scripts" / "build_and_smoke_test.sh").read_text()
    runtime_text = (ROOT / "scripts" / "runtime_p0_smoke_test.sh").read_text()
    workflow_text = (ROOT / ".github" / "workflows" / "ros-gazebo-smoke.yml").read_text()

    for text in [script_text, workflow_text]:
        assert "validate_p0_demo" in text or "p0_validator" in text
        assert "runtime_p0_smoke_test.sh" in text

    assert "validate_p0_demo" in runtime_text or "p0_validator" in runtime_text
    assert "p0_demo.launch.py" in runtime_text
    assert "manifest_output:=" in runtime_text
    assert "p0_seed_${SEED}.json" in runtime_text
    for topic in ["/clock", "/ball_picker/odom"]:
        assert topic in runtime_text


def test_world_contains_tennis_court_features():
    world_xml = ET.parse(ROOT / "worlds" / "tennis_court.sdf")
    world_text = ET.tostring(world_xml.getroot(), encoding="unicode")

    for feature in [
        "hard_tennis_court",
        "court_lines",
        "net",
        "perimeter_fence",
        "net_post_east",
        "net_post_west",
        "service_line_north",
        "center_service_line",
    ]:
        assert feature in world_text


def test_world_has_physical_boundaries():
    world_xml = ET.parse(ROOT / "worlds" / "tennis_court.sdf")
    collision_names = {
        collision.attrib["name"]
        for collision in world_xml.findall(".//collision")
    }

    assert {
        "net_collision",
        "net_post_east_collision",
        "net_post_west_collision",
        "fence_north_collision",
        "fence_south_collision",
        "fence_east_collision",
        "fence_west_collision",
    } <= collision_names


def test_world_loads_system_plugins_required_by_robot():
    world_xml = ET.parse(ROOT / "worlds" / "tennis_court.sdf")
    plugins = {
        plugin.attrib["name"]: plugin.attrib["filename"]
        for plugin in world_xml.findall(".//plugin")
    }

    assert plugins["gz::sim::systems::Physics"] == "gz-sim-physics-system"
    assert plugins["gz::sim::systems::UserCommands"] == "gz-sim-user-commands-system"
    assert plugins["gz::sim::systems::Sensors"] == "gz-sim-sensors-system"
    assert plugins["gz::sim::systems::Imu"] == "gz-sim-imu-system"
