#!/usr/bin/env python3
"""Reproducibility check for tomo_phase_fractions.

Builds a NUScope-TOMO volume from the fixture labels (with their voxel size),
computes per-phase volume fraction, sampling standard error (from the
covariance integral range) and surface density, exactly as the
tomo_phase_fractions tool does, and checks the fractions against the exact
voxel counts and that the errors and surface densities are finite and
positive. Prints the tool-style result and exits 0 on success.
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
from nuscope_tomo import Volume, VoxelSize
from nuscope_tomo.cohort import summarize


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()  # --seed accepted for CLI symmetry; the computation is deterministic

    fx = Path(args.fixture)
    data = json.loads((fx / "input.json").read_text())
    truth = data["ground_truth"]
    vol = Volume(np.load(fx / data["labels"]), VoxelSize(*data["voxel_nm"]), name="labels", kind="labels",
                 meta={"classes": data["classes"]})
    rows = summarize(vol)["phases"].to_dict(orient="records")
    got = {r["name"]: r for r in rows}

    checks = {
        "fractions exact": all(abs(got[k]["fraction"] - v) < 1e-6 for k, v in truth["fractions"].items()),
        "standard errors finite and positive": all(math.isfinite(r["fraction_se"]) and r["fraction_se"] > 0
                                                   for r in rows),
        "surface density positive": all(r["sv_um-1"] > 0 for r in rows),
        "volume": abs(rows[0]["volume_um3"] - truth["volume_um3"]) < 1e-9,
    }
    result = {
        "ok": all(checks.values()),
        "result": {"voxel_nm": data["voxel_nm"], "volume_um3": rows[0]["volume_um3"],
                   "phases": [{k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()}
                              for r in rows]},
        "diagnostics": {"checks": checks},
    }
    print(json.dumps(result, indent=2, default=float))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
