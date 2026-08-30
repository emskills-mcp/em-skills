#!/usr/bin/env python3
"""Generate the deterministic fixture for fib-mill-seg.

Builds a synthetic binary mill-region mask: one filled rectangle (the mill
volume) plus a few isolated single-pixel noise specks well clear of it, on a
2D grid. Seed is fixed so re-running this script reproduces the committed
fixtures/sample/input.json exactly.
"""
import json
import random
from pathlib import Path

SEED = 0
GRID_W = 30
GRID_H = 30
RECT = (10, 8, 23, 21)  # x0, y0, x1, y1 inclusive
N_NOISE_SPECKS = 4
BUFFER = 3


def in_buffer(x, y, rect, buffer):
    x0, y0, x1, y1 = rect
    return (x0 - buffer <= x <= x1 + buffer) and (y0 - buffer <= y <= y1 + buffer)


def main() -> None:
    rng = random.Random(SEED)
    mask = [[0] * GRID_W for _ in range(GRID_H)]
    x0, y0, x1, y1 = RECT
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            mask[y][x] = 1

    placed = 0
    while placed < N_NOISE_SPECKS:
        x, y = rng.randrange(GRID_W), rng.randrange(GRID_H)
        if mask[y][x] == 0 and not in_buffer(x, y, RECT, BUFFER):
            mask[y][x] = 1
            placed += 1

    width = x1 - x0 + 1
    height = y1 - y0 + 1
    ground_truth = {
        "bbox": [x0, y0, x1, y1],
        "area": width * height,
        "centroid": [x0 + (width - 1) / 2, y0 + (height - 1) / 2],
    }

    fixture = {"grid_w": GRID_W, "grid_h": GRID_H, "mask": mask, "ground_truth": ground_truth}
    out = Path(__file__).parent / "sample" / "input.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(fixture) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
