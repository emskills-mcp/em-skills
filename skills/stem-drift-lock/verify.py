#!/usr/bin/env python3
"""Reproducibility check for lock_drift.

Estimates the (dx, dy) drift of each frame relative to the first (reference)
frame in fixtures/sample/input.json by brute-force normalized-SSD patch
matching over a candidate shift range, and checks the recovered trajectory
against the fixture's ground truth.
"""
import argparse
import json
from pathlib import Path

SEARCH_RANGE = 6


def estimate_shift(reference, frame, crop_size, search_range):
    best_shift, best_score = (0, 0), float("inf")
    for dy in range(-search_range, search_range + 1):
        for dx in range(-search_range, search_range + 1):
            total, count = 0.0, 0
            for y in range(crop_size):
                ry = y + dy
                if not (0 <= ry < crop_size):
                    continue
                for x in range(crop_size):
                    rx = x + dx
                    if not (0 <= rx < crop_size):
                        continue
                    total += (frame[y][x] - reference[ry][rx]) ** 2
                    count += 1
            if count == 0:
                continue
            score = total / count
            if score < best_score:
                best_score, best_shift = score, (dx, dy)
    return best_shift


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()  # --seed accepted for CLI symmetry; unused (fully deterministic)

    data = json.loads((Path(args.fixture) / "input.json").read_text())
    frames = data["frames"]
    crop_size = data["crop_size"]
    truth = data["ground_truth"]["shifts"]

    reference = frames[0]
    estimated = [[0, 0]] + [
        list(estimate_shift(reference, frame, crop_size, SEARCH_RANGE)) for frame in frames[1:]
    ]

    ok = estimated == truth

    print(json.dumps({
        "ok": ok,
        "result": {"shifts": estimated},
        "diagnostics": {"expected_shifts": truth},
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
