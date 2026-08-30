#!/usr/bin/env python3
"""Generate the deterministic fixture for edax-phase-map.

Builds a synthetic EDS spectrum (counts vs. energy) as a small bremsstrahlung
background plus Gaussian characteristic lines for a known set of elements,
with additive noise. Seed is fixed so re-running this script reproduces the
committed fixtures/sample/input.json exactly.
"""
import json
import math
import random
from pathlib import Path

SEED = 0
E_MAX_KEV = 10.0
N_CHANNELS = 1000
LINE_SIGMA_KEV = 0.06
NOISE_SIGMA = 3.0

# Reference characteristic lines used both to generate and (in verify.py) to
# identify elements: energy in keV, relative peak height in counts.
ELEMENT_LINES = {
    "O": 0.525,
    "Si": 1.740,
    "Fe": 6.403,
}
PRESENT_ELEMENTS = ["O", "Si", "Fe"]
PEAK_HEIGHT = 400.0


def gaussian(x, mu, sigma):
    return math.exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def main() -> None:
    rng = random.Random(SEED)
    energies = [E_MAX_KEV * (i + 0.5) / N_CHANNELS for i in range(N_CHANNELS)]
    counts = []
    for e in energies:
        background = 15.0 + 8.0 * math.exp(-e / 4.0)
        signal = sum(
            PEAK_HEIGHT * gaussian(e, ELEMENT_LINES[el], LINE_SIGMA_KEV)
            for el in PRESENT_ELEMENTS
        )
        counts.append(round(max(0.0, background + signal + rng.gauss(0, NOISE_SIGMA)), 2))

    fixture = {
        "energies_kev": energies,
        "counts": counts,
        "reference_lines_kev": ELEMENT_LINES,
        "ground_truth": {"elements": sorted(PRESENT_ELEMENTS)},
    }
    out = Path(__file__).parent / "sample" / "input.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(fixture, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
