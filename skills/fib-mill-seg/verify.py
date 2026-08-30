#!/usr/bin/env python3
"""Reproducibility check for plan_liftout.

Labels connected components (4-connectivity flood fill) in the binary mask
from fixtures/sample/input.json, picks the largest as the mill volume,
computes its bounding box/area/centroid, derives a rectangular lift-out path
from the bbox corners, and checks the geometry against the fixture's ground
truth.
"""
import argparse
import json
from pathlib import Path


def connected_components(mask, w, h):
    visited = [[False] * w for _ in range(h)]
    components = []
    for sy in range(h):
        for sx in range(w):
            if mask[sy][sx] == 0 or visited[sy][sx]:
                continue
            stack = [(sx, sy)]
            visited[sy][sx] = True
            pixels = []
            while stack:
                x, y = stack.pop()
                pixels.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and mask[ny][nx] == 1 and not visited[ny][nx]:
                        visited[ny][nx] = True
                        stack.append((nx, ny))
            components.append(pixels)
    return components


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()  # --seed accepted for CLI symmetry; unused (fully deterministic)

    data = json.loads((Path(args.fixture) / "input.json").read_text())
    mask = data["mask"]
    w, h = data["grid_w"], data["grid_h"]
    truth = data["ground_truth"]

    components = connected_components(mask, w, h)
    largest = max(components, key=len)

    xs = [x for x, _ in largest]
    ys = [y for _, y in largest]
    bbox = [min(xs), min(ys), max(xs), max(ys)]
    area = len(largest)
    centroid = [sum(xs) / area, sum(ys) / area]
    liftout_path = [
        [bbox[0], bbox[1]], [bbox[2], bbox[1]], [bbox[2], bbox[3]], [bbox[0], bbox[3]], [bbox[0], bbox[1]],
    ]

    ok = bbox == truth["bbox"] and area == truth["area"] and centroid == truth["centroid"]

    print(json.dumps({
        "ok": ok,
        "result": {"bbox": bbox, "area": area, "centroid": centroid, "liftout_path": liftout_path},
        "diagnostics": {"n_components": len(components), "expected": truth},
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
