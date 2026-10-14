#!/usr/bin/env python3
"""Reproducibility check for nuscope_analyze (op = particles) on an SEM image.

Loads the fixture TIFF with NUScope, which reads the pixel size from the
Thermo Fisher metadata, measures the particles in nm, and checks the count,
the calibration and every equivalent diameter against the fixture's ground
truth (each within 3 %). Prints the tool-style result and exits 0 on success.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import nuscope as ns
from nuscope import analyze as an


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()  # --seed accepted for CLI symmetry; the analysis is deterministic

    fx = Path(args.fixture)
    data = json.loads((fx / "input.json").read_text())
    truth = data["ground_truth"]

    ds = ns.load(fx / data["image"])
    table = an.particles(ds, **data["arguments"]["params"])
    got = sorted(table["eq_diameter_nm"].tolist())

    checks = {
        "pixel size read from file": abs(ds.pixel_size_nm - truth["pixel_size_nm"]) < 1e-9,
        "particle count": len(got) == truth["count"],
        "diameters within 3 %": len(got) == truth["count"] and all(
            abs(g - t) / t < 0.03 for g, t in zip(got, truth["eq_diameter_nm"])),
        # the table carries its own provenance: read -> particles, with the parameters used, hash-chained
        "history recorded": [a.op for a in table.attrs["provenance"].activities][-1] == "analyze.particles"
        and table.attrs["provenance"].check_chain()[0],
    }
    result = {
        "ok": all(checks.values()),
        "result": {"count": len(got), "median_eq_diameter_nm": round(float(np.median(got)), 3) if got else None,
                   "area_fraction": round(float(table.attrs.get("area_fraction", 0.0)), 4),
                   "units": table.attrs.get("units")},
        "diagnostics": {"checks": checks, "truth_median_nm": truth["median_eq_diameter_nm"],
                        "nuscope": ns.__version__},
    }
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
