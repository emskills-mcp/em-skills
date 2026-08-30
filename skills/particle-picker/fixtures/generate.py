#!/usr/bin/env python3
"""Generate the deterministic fixture for particle-picker.

Builds a synthetic 2D micrograph: a handful of well-separated Gaussian
"particles" over a noisy background. Seed is fixed so re-running this script
reproduces the committed fixtures/sample/input.json exactly.
"""
import json
import math
import random
from pathlib import Path

SEED = 0
W, H = 60, 60
N_PARTICLES = 8
MIN_SEPARATION_PX = 10
PARTICLE_SIGMA_PX = 2.5
PARTICLE_HEIGHT = 80.0
BACKGROUND = 20.0
NOISE_SIGMA = 6.0
MARGIN = 6


def place_particles(rng, n, w, h, margin, min_sep):
    positions = []
    attempts = 0
    while len(positions) < n and attempts < 10000:
        attempts += 1
        x = rng.uniform(margin, w - margin)
        y = rng.uniform(margin, h - margin)
        if all(math.hypot(x - px, y - py) >= min_sep for px, py in positions):
            positions.append((x, y))
    return positions


def main() -> None:
    rng = random.Random(SEED)
    positions = place_particles(rng, N_PARTICLES, W, H, MARGIN, MIN_SEPARATION_PX)

    image = []
    for y in range(H):
        row = []
        for x in range(W):
            signal = sum(
                PARTICLE_HEIGHT * math.exp(-((x - px) ** 2 + (y - py) ** 2) / (2 * PARTICLE_SIGMA_PX ** 2))
                for px, py in positions
            )
            row.append(round(BACKGROUND + signal + rng.gauss(0, NOISE_SIGMA), 2))
        image.append(row)

    fixture = {
        "width": W,
        "height": H,
        "image": image,
        "ground_truth": {
            "positions": [[round(x, 2), round(y, 2)] for x, y in positions],
            "n_particles": len(positions),
        },
    }
    out = Path(__file__).parent / "sample" / "input.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(fixture) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
