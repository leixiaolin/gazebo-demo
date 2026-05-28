from tennis_ball_picker_sim.p0_validator import validate_p0


def test_validate_p0_reports_success_for_workspace_root():
    report = validate_p0(".", ball_count=50, seed=42)

    assert report["ok"] is True
    assert report["failures"] == []
    assert all(check["ok"] for check in report["checks"])
    assert report["scenario"]["ball_count"] == 50
    assert report["scenario"]["seed"] == 42
    assert report["scenario"]["world"] == "tennis_court"
    assert report["scenario"]["first_ball"]["name"] == "tennis_ball_00"

    check_names = {check["name"] for check in report["checks"]}
    assert "launch:default 50 balls" in check_names
    assert "launch:default seed 42" in check_names
    assert "world_boundary_collisions" in check_names
    assert "package:exec_depends" in check_names
    assert "scenario:balls_inside_court" in check_names
    assert "scenario:ball_separation" in check_names
