#!/usr/bin/env python3
"""Reproducibility check for pick_particles.

Detects local intensity maxima (8-neighborhood) above a threshold in the
micrograph from fixtures/sample/input.json, suppresses near-duplicate
detections within a minimum separation, and checks the picks against the
fixture's ground truth positions (matched by nearest neighbor).
"""
import argparse
import json
import math
from pathlib import Path

THRESHOLD_ABOVE_BACKGROUND = 30.0
MIN_PEAK_SEPARATION_PX = 8
MATCH_TOLERANCE_PX = 3.0


def local_maxima(image, w, h, threshold):
    candidates = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            v = image[y][x]
            if v <= threshold:
                continue
            neighbors = [
                image[y + dy][x + dx]
                for dy in (-1, 0, 1) for dx in (-1, 0, 1) if not (dx == 0 and dy == 0)
            ]
            if v >= max(neighbors):
                candidates.append((x, y, v))
    return candidates


def suppress(candidates, min_separation):
    picks = []
    for x, y, v in sorted(candidates, key=lambda c: -c[2]):
        if all(math.hypot(x - px, y - py) >= min_separation for px, py, _ in picks):
            picks.append((x, y, v))
    return picks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()  # --seed accepted for CLI symmetry; unused (fully deterministic)

    data = json.loads((Path(args.fixture) / "input.json").read_text())
    image = data["image"]
    w, h = data["width"], data["height"]
    background = sorted(v for row in image for v in row)[len(image) * len(image[0]) // 4]
    truth_positions = data["ground_truth"]["positions"]

    candidates = local_maxima(image, w, h, background + THRESHOLD_ABOVE_BACKGROUND)
    picks = suppress(candidates, MIN_PEAK_SEPARATION_PX)

    matched = 0
    remaining = list(truth_positions)
    for x, y, _ in picks:
        best = min(remaining, key=lambda p: math.hypot(p[0] - x, p[1] - y), default=None)
        if best is not None and math.hypot(best[0] - x, best[1] - y) <= MATCH_TOLERANCE_PX:
            matched += 1
            remaining.remove(best)

    ok = matched == len(truth_positions) and len(picks) == len(truth_positions)

    print(json.dumps({
        "ok": ok,
        "result": {"positions": [[x, y] for x, y, _ in picks], "n_particles": len(picks)},
        "diagnostics": {"matched_to_ground_truth": matched, "expected_n_particles": len(truth_positions)},
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
