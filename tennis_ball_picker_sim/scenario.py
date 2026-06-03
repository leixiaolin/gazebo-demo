"""Command-line helpers for inspecting deterministic ball scenarios."""

import argparse
import json
from pathlib import Path

from tennis_ball_picker_sim.scatter import BALL_RADIUS, sample_ball_positions


ROBOT_SPAWN = {
    "x": 0.0,
    "y": -4.75,
    "z": 0.0,
    "yaw_rad": 1.5708,
}


def build_scenario(count, seed):
    """Return a JSON-serializable deterministic scenario description."""
    positions = sample_ball_positions(count, seed)
    return {
        "ball_count": count,
        "world": "tennis_court",
        "seed": seed,
        "ball_radius_m": BALL_RADIUS,
        "robot_spawn": ROBOT_SPAWN,
        "balls": [
            {
                "name": f"tennis_ball_{index:02d}",
                "x": point.x,
                "y": point.y,
                "z": BALL_RADIUS + 0.015,
                "yaw_rad": 0.0,
            }
            for index, point in enumerate(positions)
        ],
    }


def write_scenario(path, count, seed):
    """Write a deterministic scenario manifest to a JSON file."""
    output_path = Path(path)
    manifest = build_scenario(count, seed)
    text = json.dumps(manifest, indent=2, sort_keys=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text + "\n", encoding="utf-8")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ball-count", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON file path for saving the manifest.",
    )
    args = parser.parse_args(argv)

    if args.output:
        write_scenario(args.output, args.ball_count, args.seed)
    else:
        manifest = build_scenario(args.ball_count, args.seed)
        text = json.dumps(manifest, indent=2, sort_keys=True)
        print(text)


if __name__ == "__main__":
    main()
