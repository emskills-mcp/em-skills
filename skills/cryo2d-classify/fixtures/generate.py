#!/usr/bin/env python3
"""Generate the deterministic fixture for cryo2d-classify.

Two synthetic particle templates (horizontal vs. vertical bar) with small
additive Gaussian noise. Seed is fixed so re-running this script reproduces
the committed fixtures/sample/input.json exactly.
"""
import json
import random
from pathlib import Path

SEED = 0
GRID = 8
N_PER_CLASS = 6
NOISE_SIGMA = 0.05


def template(kind: str) -> list[float]:
    grid = [[0.0] * GRID for _ in range(GRID)]
    mid = GRID // 2
    if kind == "horizontal":
        for x in range(GRID):
            grid[mid][x] = 1.0
            grid[mid - 1][x] = 1.0
    else:
        for y in range(GRID):
            grid[y][mid] = 1.0
            grid[y][mid - 1] = 1.0
    return [v for row in grid for v in row]


def main() -> None:
    rng = random.Random(SEED)
    particles = []
    labels = []
    for label, kind in enumerate(("horizontal", "vertical")):
        base = template(kind)
        for _ in range(N_PER_CLASS):
            particles.append([v + rng.gauss(0, NOISE_SIGMA) for v in base])
            labels.append(label)

    order = list(range(len(particles)))
    rng.shuffle(order)
    particles = [particles[i] for i in order]
    labels = [labels[i] for i in order]

    fixture = {
        "particles": particles,
        "grid_size": GRID,
        "ground_truth": {"n_classes": 2, "labels": labels},
    }
    out = Path(__file__).parent / "sample" / "input.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(fixture, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
