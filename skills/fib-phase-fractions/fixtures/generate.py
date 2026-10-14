#!/usr/bin/env python3
"""Generate the deterministic fixture for fib-phase-fractions.

A labelled FIB-SEM volume (24 x 48 x 48 voxels, 20 nm slices, 10 nm pixels),
as segmentation would produce it: 1 = matrix, 2 = particles (randomly placed
spheres), 0 = pores (smaller spheres). The ground truth fractions are the exact
voxel counts. Seed is fixed: re-running reproduces the committed files.
"""
import json
from pathlib import Path

import numpy as np

SEED = 0
SHAPE = (24, 48, 48)
VOXEL_NM = (20.0, 10.0, 10.0)


def spheres(rng, lab, value, n, rmin, rmax):
    z, y, x = np.indices(SHAPE)
    for _ in range(n):
        c = [rng.uniform(0, s) for s in SHAPE]
        r = rng.uniform(rmin, rmax)
        # distances in nm, so spheres are round in physical space despite anisotropic voxels
        d2 = sum(((g - cc) * v) ** 2 for g, cc, v in zip((z, y, x), c, VOXEL_NM))
        lab[d2 <= (r * 10) ** 2] = value


def main() -> None:
    rng = np.random.default_rng(SEED)
    lab = np.ones(SHAPE, np.uint8)
    spheres(rng, lab, 2, 14, 6, 11)
    spheres(rng, lab, 0, 10, 2, 4)
    out = Path(__file__).parent / "sample"
    out.mkdir(exist_ok=True)
    np.save(out / "labels.npy", lab)
    n = lab.size
    (out / "input.json").write_text(json.dumps({
        "labels": "labels.npy", "voxel_nm": VOXEL_NM,
        "classes": {"1": "matrix", "2": "particles"},
        "ground_truth": {"fractions": {"matrix": round(float((lab == 1).sum() / n), 6),
                                       "particles": round(float((lab == 2).sum() / n), 6)},
                         "volume_um3": round(n * np.prod(VOXEL_NM) / 1e9, 9)},
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
