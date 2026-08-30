#!/usr/bin/env python3
"""Generate the deterministic fixture for lattice-dspacing.

Builds a synthetic 1D lattice-fringe intensity profile: evenly spaced
Gaussian peaks (with small per-peak position jitter) at a known d-spacing,
plus background and noise. Seed is fixed so re-running this script
reproduces the committed fixtures/sample/input.json exactly.
"""
import json
import math
import random
from pathlib import Path

SEED = 0
PROFILE_LEN_PX = 220
TRUE_SPACING_PX = 12.3
PHASE_PX = 6.0
PEAK_SIGMA_PX = 1.4
JITTER_SIGMA_PX = 0.25
PEAK_HEIGHT = 100.0
NOISE_SIGMA = 4.0


def gaussian(x, mu, sigma):
    return math.exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def main() -> None:
    rng = random.Random(SEED)
    peak_centers = []
    center = PHASE_PX
    while center < PROFILE_LEN_PX:
        peak_centers.append(center + rng.gauss(0, JITTER_SIGMA_PX))
        center += TRUE_SPACING_PX

    intensity = []
    for x in range(PROFILE_LEN_PX):
        signal = 20.0 + sum(PEAK_HEIGHT * gaussian(x, c, PEAK_SIGMA_PX) for c in peak_centers)
        intensity.append(round(signal + rng.gauss(0, NOISE_SIGMA), 2))

    fixture = {
        "intensity": intensity,
        "pixel_size_note": "profile index == pixel position",
        "ground_truth": {"d_spacing_px": TRUE_SPACING_PX, "n_peaks": len(peak_centers)},
    }
    out = Path(__file__).parent / "sample" / "input.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(fixture, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
