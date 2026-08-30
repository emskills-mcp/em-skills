#!/usr/bin/env python3
"""Reproducibility check for reconstruct_relief.

Recovers x/y gradient estimates from opposing quadrant-pair differences in
fixtures/sample/input.json, reconstructs the relief map by path integration
(down the first column, then along each row), and checks it against the
fixture's ground truth (relative to the origin pixel) within tolerance.
"""
import argparse
import json
from pathlib import Path

RMS_TOLERANCE = 0.2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()  # --seed accepted for CLI symmetry; unused (fully deterministic)

    data = json.loads((Path(args.fixture) / "input.json").read_text())
    w, h = data["width"], data["height"]
    gain = data["gain"]
    a, b, c, d = data["quadrant_a"], data["quadrant_b"], data["quadrant_c"], data["quadrant_d"]
    truth = data["ground_truth"]["relief"]

    dzdx = [[(a[y][x] - b[y][x]) / gain for x in range(w)] for y in range(h)]
    dzdy = [[(c[y][x] - d[y][x]) / gain for x in range(w)] for y in range(h)]

    z_col0 = [0.0] * h
    for y in range(1, h):
        z_col0[y] = z_col0[y - 1] + dzdy[y - 1][0]

    relief = [[0.0] * w for _ in range(h)]
    for y in range(h):
        relief[y][0] = z_col0[y]
        for x in range(1, w):
            relief[y][x] = relief[y][x - 1] + dzdx[y][x - 1]

    sq_errors = [(relief[y][x] - truth[y][x]) ** 2 for y in range(h) for x in range(w)]
    rms_error = (sum(sq_errors) / len(sq_errors)) ** 0.5
    ok = rms_error <= RMS_TOLERANCE

    print(json.dumps({
        "ok": ok,
        "result": {"relief": [[round(v, 4) for v in row] for row in relief]},
        "diagnostics": {"rms_error_vs_fixture": round(rms_error, 5)},
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
