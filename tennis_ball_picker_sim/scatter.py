"""Utilities for reproducible tennis ball scattering on a court."""

from dataclasses import dataclass
import random


COURT_HALF_LENGTH = 23.77 / 2.0
COURT_HALF_WIDTH = 10.97 / 2.0
BALL_RADIUS = 0.0335


@dataclass(frozen=True)
class BallPosition:
    """A sampled ball position in the Gazebo world frame."""

    x: float
    y: float


def sample_ball_positions(count, seed, min_separation=0.34):
    """Sample non-overlapping tennis ball positions within the court lines."""
    rng = random.Random(seed)
    positions = []
    attempts = 0

    while len(positions) < count and attempts < count * 200:
        attempts += 1
        x = rng.uniform(-COURT_HALF_LENGTH + 0.45, COURT_HALF_LENGTH - 0.45)
        y = rng.uniform(-COURT_HALF_WIDTH + 0.45, COURT_HALF_WIDTH - 0.45)

        # Keep the initial robot staging area and the net line readable.
        if -1.0 < x < 1.0 and y < -3.9:
            continue
        if abs(x) < 0.35:
            continue

        too_close = any(
            (x - point.x) ** 2 + (y - point.y) ** 2 < min_separation**2
            for point in positions
        )
        if too_close:
            continue
        positions.append(BallPosition(x=x, y=y))

    if len(positions) < count:
        raise RuntimeError(
            f"Could only place {len(positions)} of {count} requested balls"
        )

    return positions
