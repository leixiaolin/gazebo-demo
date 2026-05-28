import json

from tennis_ball_picker_sim.scenario import build_scenario, main, write_scenario


def test_scenario_manifest_matches_requested_count_and_seed():
    manifest = build_scenario(12, 7)

    assert manifest["ball_count"] == 12
    assert manifest["seed"] == 7
    assert manifest["world"] == "tennis_court"
    assert manifest["robot_spawn"]["y"] == -4.75
    assert len(manifest["balls"]) == 12
    assert manifest["balls"][0]["name"] == "tennis_ball_00"
    assert {"x", "y", "z", "yaw_rad"} <= set(manifest["balls"][0])


def test_scenario_manifest_is_reproducible():
    assert build_scenario(8, 99) == build_scenario(8, 99)


def test_scenario_cli_can_write_manifest_file(tmp_path):
    output_path = tmp_path / "scenario" / "seed_7.json"

    main(["--ball-count", "3", "--seed", "7", "--output", str(output_path)])

    manifest = json.loads(output_path.read_text(encoding="utf-8"))
    assert manifest == build_scenario(3, 7)


def test_write_scenario_returns_written_manifest(tmp_path):
    output_path = tmp_path / "manifest.json"

    manifest = write_scenario(output_path, 4, 11)

    assert manifest == build_scenario(4, 11)
    assert json.loads(output_path.read_text(encoding="utf-8")) == manifest
