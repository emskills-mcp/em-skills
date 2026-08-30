#!/usr/bin/env python3
"""Generate the deterministic fixture for eels-edge-id.

Builds a synthetic EELS spectrum as a power-law background plus one
ionization edge (a smoothed step with a slowly decaying post-edge tail) at a
known onset energy, with shot-noise-like additive noise. Seed is fixed so
re-running this script reproduces the committed fixtures/sample/input.json
exactly.
"""
import json
import math
import random
from pathlib import Path

SEED = 0
E_START_EV = 200.0
E_END_EV = 600.0
N_CHANNELS = 400
BACKGROUND_A = 5.0e6
BACKGROUND_EXPONENT = 3.0
EDGE_WIDTH_EV = 3.0
EDGE_JUMP = 1500.0
POST_EDGE_DECAY_EV = 100.0
NOISE_FACTOR = 0.03

# Reference core-loss edge onsets (eV), used both to generate and (in
# verify.py) to identify the edge.
REFERENCE_EDGES_EV = {"C K": 284.0, "N K": 400.0, "O K": 532.0}
TRUE_EDGE = "C K"


def background(e: float) -> float:
    return BACKGROUND_A * e ** (-BACKGROUND_EXPONENT)


def edge_signal(e: float, onset: float) -> float:
    step = 1.0 / (1.0 + math.exp(-(e - onset) / (EDGE_WIDTH_EV / 4)))
    tail = math.exp(-max(0.0, e - onset) / POST_EDGE_DECAY_EV)
    return EDGE_JUMP * step * tail


def main() -> None:
    rng = random.Random(SEED)
    onset = REFERENCE_EDGES_EV[TRUE_EDGE]
    energies = [E_START_EV + (E_END_EV - E_START_EV) * i / (N_CHANNELS - 1) for i in range(N_CHANNELS)]
    counts = []
    for e in energies:
        value = background(e) + edge_signal(e, onset)
        noisy = value + rng.gauss(0, NOISE_FACTOR * math.sqrt(max(value, 1.0)))
        counts.append(round(max(0.0, noisy), 2))

    fixture = {
        "energies_ev": energies,
        "counts": counts,
        "reference_edges_ev": REFERENCE_EDGES_EV,
        "ground_truth": {"edge": TRUE_EDGE, "onset_ev": onset},
    }
    out = Path(__file__).parent / "sample" / "input.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(fixture, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
