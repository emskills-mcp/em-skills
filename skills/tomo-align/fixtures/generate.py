#!/usr/bin/env python3
"""Generate the deterministic fixture for tomo-align.

Builds a synthetic fiducial-free tilt series: a single compact feature whose
ideal projected position traces x(theta) = x0*cos(theta) + z0*sin(theta), a
known per-projection alignment shift added on top (simulating stage/beam
drift), rendered as a 1D Gaussian-peak intensity profile with noise. Seed is
fixed so re-running this script reproduces the committed
fixtures/sample/input.json exactly.
"""
import json
import math
import random
from pathlib import Path

SEED = 0
N_ANGLES = 31
ANGLE_RANGE_DEG = 60.0
X0 = 3.0
Z0 = -2.0
SHIFT_SIGMA_PX = 1.0
PIXELS = list(range(-25, 26))
PEAK_SIGMA_PX = 2.0
PEAK_HEIGHT = 50.0
BACKGROUND = 5.0
NOISE_SIGMA = 1.0


def ideal_position(theta_rad: float) -> float:
    return X0 * math.cos(theta_rad) + Z0 * math.sin(theta_rad)


def main() -> None:
    rng = random.Random(SEED)
    angles_deg = [
        -ANGLE_RANGE_DEG + 2 * ANGLE_RANGE_DEG * i / (N_ANGLES - 1) for i in range(N_ANGLES)
    ]

    projections = []
    applied_shifts = []
    for angle_deg in angles_deg:
        theta = math.radians(angle_deg)
        shift = round(rng.gauss(0, SHIFT_SIGMA_PX), 3)
        applied_shifts.append(shift)
        center = ideal_position(theta) + shift
        profile = [
            round(BACKGROUND + PEAK_HEIGHT * math.exp(-((p - center) ** 2) / (2 * PEAK_SIGMA_PX ** 2)) + rng.gauss(0, NOISE_SIGMA), 3)
            for p in PIXELS
        ]
        projections.append(profile)

    fixture = {
        "pixels": PIXELS,
        "angles_deg": angles_deg,
        "projections": projections,
        "ground_truth": {"x0": X0, "z0": Z0, "shifts_px": applied_shifts},
    }
    out = Path(__file__).parent / "sample" / "input.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(fixture) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
