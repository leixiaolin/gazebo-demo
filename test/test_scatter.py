from tennis_ball_picker_sim.scatter import (
    COURT_HALF_LENGTH,
    COURT_HALF_WIDTH,
    sample_ball_positions,
)


def test_scatter_is_reproducible():
    first = sample_ball_positions(50, 20260528)
    second = sample_ball_positions(50, 20260528)

    assert first == second


def test_scatter_stays_inside_court_and_clear_of_spawn_area():
    positions = sample_ball_positions(50, 42)

    assert len(positions) == 50
    for position in positions:
        assert -COURT_HALF_LENGTH < position.x < COURT_HALF_LENGTH
        assert -COURT_HALF_WIDTH < position.y < COURT_HALF_WIDTH
        assert not (-1.0 < position.x < 1.0 and position.y < -3.9)
        assert abs(position.x) >= 0.35


def test_scatter_keeps_balls_separated():
    positions = sample_ball_positions(50, 7)

    for index, first in enumerate(positions):
        for second in positions[index + 1 :]:
            squared_distance = (first.x - second.x) ** 2 + (first.y - second.y) ** 2
            assert squared_distance >= 0.34**2
