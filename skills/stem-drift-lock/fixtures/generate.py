#!/usr/bin/env python3
"""Generate the deterministic fixture for stem-drift-lock.

Builds a small sequence of synthetic frames cropped from a shared,
asymmetric synthetic scene (a few distinct Gaussian features, so there is no
translational ambiguity), each crop offset by a known applied (dx, dy) drift
relative to the first (reference) frame, plus noise. Seed is fixed so
re-running this script reproduces the committed fixtures/sample/input.json
exactly.
"""
import json
import math
import random
from pathlib import Path

SEED = 0
CROP = 20
BASE_OFFSET = 15
NOISE_SIGMA = 2.0
FEATURES = [  # (cx, cy, sigma, height) in canvas coordinates
    (18.0, 11.0, 2.5, 90.0),
    (30.0, 25.0, 3.0, 70.0),
    (9.0, 30.0, 2.0, 60.0),
    (34.0, 8.0, 1.8, 50.0),
]
APPLIED_SHIFTS = [(0, 0), (2, -1), (-3, 2), (1, 3), (-2, -2), (4, 0)]


def canvas(x: float, y: float) -> float:
    value = 10.0
    for cx, cy, sigma, height in FEATURES:
        value += height * math.exp(-(((x - cx) ** 2 + (y - cy) ** 2)) / (2 * sigma * sigma))
    return value


def crop(rng, dx: int, dy: int):
    return [
        [round(canvas(x + BASE_OFFSET + dx, y + BASE_OFFSET + dy) + rng.gauss(0, NOISE_SIGMA), 3) for x in range(CROP)]
        for y in range(CROP)
    ]


def main() -> None:
    rng = random.Random(SEED)
    frames = [crop(rng, dx, dy) for dx, dy in APPLIED_SHIFTS]

    fixture = {
        "crop_size": CROP,
        "frames": frames,
        "ground_truth": {"shifts": [[dx, dy] for dx, dy in APPLIED_SHIFTS]},
    }
    out = Path(__file__).parent / "sample" / "input.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(fixture) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
