#!/usr/bin/env python3
"""Generate the deterministic fixture for sem-topography.

Builds a synthetic height map (two Gaussian bumps), derives the four
backscattered quadrant images from its x/y gradients (opposing quadrant
pairs encode +/- gradient, the standard four-quadrant shape-from-shading
setup), and adds noise. Seed is fixed so re-running this script reproduces
the committed fixtures/sample/input.json exactly.
"""
import json
import math
import random
from pathlib import Path

SEED = 0
W, H = 12, 12
AMBIENT = 100.0
GAIN = 40.0
NOISE_SIGMA = 0.8


def height(x: float, y: float) -> float:
    bump1 = 3.0 * math.exp(-(((x - 4) ** 2 + (y - 4) ** 2)) / (2 * 2.5 ** 2))
    bump2 = 2.0 * math.exp(-(((x - 8) ** 2 + (y - 8) ** 2)) / (2 * 1.8 ** 2))
    return bump1 + bump2


def main() -> None:
    rng = random.Random(SEED)
    z = [[height(x, y) for x in range(W)] for y in range(H)]

    dzdx = [[0.0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W - 1):
            dzdx[y][x] = z[y][x + 1] - z[y][x]
        dzdx[y][W - 1] = dzdx[y][W - 2]

    dzdy = [[0.0] * W for _ in range(H)]
    for y in range(H - 1):
        for x in range(W):
            dzdy[y][x] = z[y + 1][x] - z[y][x]
    for x in range(W):
        dzdy[H - 1][x] = dzdy[H - 2][x]

    def quad(sign_grid, other_axis_sign=0.0):
        return [
            [round(AMBIENT + 0.5 * GAIN * sign_grid[y][x] + rng.gauss(0, NOISE_SIGMA), 3) for x in range(W)]
            for y in range(H)
        ]

    quadrant_a = quad(dzdx)  # looking +x
    quadrant_b = quad([[-v for v in row] for row in dzdx])  # looking -x
    quadrant_c = quad(dzdy)  # looking +y
    quadrant_d = quad([[-v for v in row] for row in dzdy])  # looking -y

    z0 = z[0][0]
    z_relative = [[round(v - z0, 4) for v in row] for row in z]

    fixture = {
        "width": W,
        "height": H,
        "gain": GAIN,
        "quadrant_a": quadrant_a,
        "quadrant_b": quadrant_b,
        "quadrant_c": quadrant_c,
        "quadrant_d": quadrant_d,
        "ground_truth": {"relief": z_relative},
    }
    out = Path(__file__).parent / "sample" / "input.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(fixture) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
