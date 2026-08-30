#!/usr/bin/env python3
"""Generate the deterministic fixture for grid-atlas-qc.

Builds a synthetic grid atlas: an NxN array of per-square ice-thickness
estimates (nm), classified against fixed thresholds. Seed is fixed so
re-running this script reproduces the committed fixtures/sample/input.json
exactly.
"""
import json
import random
from pathlib import Path

SEED = 0
GRID_N = 5
THICKNESS_RANGE_NM = (15.0, 220.0)
GOOD_RANGE_NM = (30.0, 120.0)
MARGINAL_RANGE_NM = (20.0, 180.0)


def classify(thickness: float) -> str:
    if GOOD_RANGE_NM[0] <= thickness <= GOOD_RANGE_NM[1]:
        return "good"
    if MARGINAL_RANGE_NM[0] <= thickness <= MARGINAL_RANGE_NM[1]:
        return "marginal"
    return "bad"


def main() -> None:
    rng = random.Random(SEED)
    thicknesses = [
        round(rng.uniform(*THICKNESS_RANGE_NM), 1) for _ in range(GRID_N * GRID_N)
    ]
    labels = [classify(t) for t in thicknesses]
    score = round(labels.count("good") / len(labels), 4)

    fixture = {
        "grid_n": GRID_N,
        "thickness_nm": thicknesses,
        "good_range_nm": list(GOOD_RANGE_NM),
        "marginal_range_nm": list(MARGINAL_RANGE_NM),
        "ground_truth": {"labels": labels, "score": score},
    }
    out = Path(__file__).parent / "sample" / "input.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(fixture, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
