#!/usr/bin/env python3
"""Reproducibility check for align_tilt_series.

Extracts an intensity-weighted centroid position from each projection in
fixtures/sample/input.json, fits the ideal sinogram trajectory
x(theta) = x0*cos(theta) + z0*sin(theta) to those centroids by least squares
(fiducial-free, since the fit itself absorbs the smooth trajectory and the
residuals are the per-projection misalignment), and checks the recovered
trajectory and shifts against the fixture's ground truth.
"""
import argparse
import json
import math
from pathlib import Path

SHIFT_MEAN_ABS_ERROR_TOLERANCE = 0.6
TRAJECTORY_TOLERANCE = 0.5


def centroid(pixels, profile, window=8):
    peak_idx = max(range(len(profile)), key=lambda i: profile[i])
    lo, hi = max(0, peak_idx - window), min(len(profile), peak_idx + window + 1)
    local_pixels = pixels[lo:hi]
    local_profile = profile[lo:hi]
    baseline = min(local_profile)
    weights = [v - baseline for v in local_profile]
    total = sum(weights)
    if total == 0:
        return float(pixels[peak_idx])
    return sum(p * w for p, w in zip(local_pixels, weights)) / total


def fit_trajectory(cos_vals, sin_vals, positions):
    scc = sum(c * c for c in cos_vals)
    sss = sum(s * s for s in sin_vals)
    scs = sum(c * s for c, s in zip(cos_vals, sin_vals))
    scy = sum(c * y for c, y in zip(cos_vals, positions))
    ssy = sum(s * y for s, y in zip(sin_vals, positions))
    det = scc * sss - scs * scs
    x0 = (scy * sss - ssy * scs) / det
    z0 = (scc * ssy - scs * scy) / det
    return x0, z0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()  # --seed accepted for CLI symmetry; unused (fully deterministic)

    data = json.loads((Path(args.fixture) / "input.json").read_text())
    pixels = data["pixels"]
    angles_deg = data["angles_deg"]
    projections = data["projections"]
    truth = data["ground_truth"]

    positions = [centroid(pixels, profile) for profile in projections]

    cos_vals = [math.cos(math.radians(a)) for a in angles_deg]
    sin_vals = [math.sin(math.radians(a)) for a in angles_deg]
    x0, z0 = fit_trajectory(cos_vals, sin_vals, positions)

    fitted = [x0 * c + z0 * s for c, s in zip(cos_vals, sin_vals)]
    shifts = [p - f for p, f in zip(positions, fitted)]

    shift_errors = [abs(s - t) for s, t in zip(shifts, truth["shifts_px"])]
    mean_abs_shift_error = sum(shift_errors) / len(shift_errors)
    trajectory_error = math.hypot(x0 - truth["x0"], z0 - truth["z0"])

    ok = (
        mean_abs_shift_error <= SHIFT_MEAN_ABS_ERROR_TOLERANCE
        and trajectory_error <= TRAJECTORY_TOLERANCE
    )

    print(json.dumps({
        "ok": ok,
        "result": {"x0": round(x0, 3), "z0": round(z0, 3), "shifts_px": [round(s, 3) for s in shifts]},
        "diagnostics": {
            "mean_abs_shift_error": round(mean_abs_shift_error, 4),
            "trajectory_error": round(trajectory_error, 4),
        },
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
