#!/usr/bin/env python3
"""Generate the deterministic fixture for sem-particle-size.

A 256 x 256 SEM image (uint8, 10 nm pixels) written the way a Thermo Fisher
SEM writes it: a TIFF with the instrument's INI metadata in tag 34682, so the
pixel size (PixelWidth = 1e-08 m) is read from the file, not passed by hand.
It holds 12 bright, separated disks of known radius (6-11 px) on a noisy
background. Ground truth: the number of particles and their equivalent
diameters in nm. Seed is fixed: re-running reproduces the committed files.
"""
import json
from pathlib import Path

import numpy as np
import tifffile

SEED = 0
SIZE = 256
PIXEL_NM = 10.0
INI = """[User]
Date=05/14/2024
Time=10:12:34 AM
User=fixture

[System]
Type=SEM
SystemType=Quanta FEG 650

[Beam]
HV=5000

[EBeam]
HV=5000
WD=0.0101

[Scan]
Dwelltime=3e-05
PixelWidth=1e-08
PixelHeight=1e-08
"""


def main() -> None:
    rng = np.random.default_rng(SEED)
    img = rng.normal(40, 6, (SIZE, SIZE))
    yy, xx = np.mgrid[:SIZE, :SIZE]
    centres, radii = [], []
    while len(centres) < 12:
        r = int(rng.integers(6, 12))
        cy, cx = rng.integers(r + 6, SIZE - r - 6, 2)
        if all((cy - y) ** 2 + (cx - x) ** 2 > (r + q + 6) ** 2 for (y, x), q in zip(centres, radii)):
            centres.append((int(cy), int(cx)))
            radii.append(r)
            img[(yy - cy) ** 2 + (xx - cx) ** 2 <= r * r] += 140
    out = Path(__file__).parent / "sample"
    out.mkdir(exist_ok=True)
    tifffile.imwrite(out / "sem.tif", np.clip(img, 0, 255).astype(np.uint8),
                     extratags=[(34682, "s", 0, INI, False)])
    # equivalent diameter of each digital disk, from its exact pixel count
    areas = [int(((yy - cy) ** 2 + (xx - cx) ** 2 <= r * r).sum()) for (cy, cx), r in zip(centres, radii)]
    diam = sorted(2 * np.sqrt(a / np.pi) * PIXEL_NM for a in areas)
    (out / "input.json").write_text(json.dumps({
        "image": "sem.tif",
        "arguments": {"op": "particles", "params": {"min_area_nm2": 2000}},
        "ground_truth": {"count": 12, "pixel_size_nm": PIXEL_NM,
                         "eq_diameter_nm": [round(d, 3) for d in diam],
                         "median_eq_diameter_nm": round(float(np.median(diam)), 3)},
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
