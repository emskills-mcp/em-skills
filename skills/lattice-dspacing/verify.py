#!/usr/bin/env python3
"""Reproducibility check for fit_lattice.

Finds fringe peaks in the 1D intensity profile from fixtures/sample/input.json
(local maxima above a background-relative threshold, deduplicated by minimum
separation), averages the consecutive peak-to-peak spacing, and checks the
recovered d-spacing against the fixture's ground truth.
"""
import argparse
import json
from pathlib import Path

MIN_PEAK_SEPARATION_PX = 5
THRESHOLD_ABOVE_BASELINE = 25.0
RELATIVE_SPACING_TOLERANCE = 0.05


def find_peaks(intensity, threshold, min_separation):
    baseline = sorted(intensity)[len(intensity) // 4]  # rough low-percentile background estimate
    candidates = [
        i for i in range(1, len(intensity) - 1)
        if intensity[i] > baseline + threshold
        and intensity[i] >= intensity[i - 1]
        and intensity[i] >= intensity[i + 1]
    ]
    peaks = []
    for i in candidates:
        if peaks and i - peaks[-1] < min_separation:
            if intensity[i] > intensity[peaks[-1]]:
                peaks[-1] = i
        else:
            peaks.append(i)
    return peaks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()  # --seed accepted for CLI symmetry; unused (fully deterministic)

    data = json.loads((Path(args.fixture) / "input.json").read_text())
    intensity = data["intensity"]
    truth = data["ground_truth"]

    peaks = find_peaks(intensity, THRESHOLD_ABOVE_BASELINE, MIN_PEAK_SEPARATION_PX)
    spacings = [b - a for a, b in zip(peaks, peaks[1:])]
    mean_spacing = sum(spacings) / len(spacings)
    variance = sum((s - mean_spacing) ** 2 for s in spacings) / len(spacings)
    std_spacing = variance ** 0.5
    confidence = round(max(0.0, 1 - std_spacing / mean_spacing), 4)

    rel_error = abs(mean_spacing - truth["d_spacing_px"]) / truth["d_spacing_px"]
    ok = rel_error <= RELATIVE_SPACING_TOLERANCE and abs(len(peaks) - truth["n_peaks"]) <= 1

    print(json.dumps({
        "ok": ok,
        "result": {"d_spacing_px": round(mean_spacing, 3), "n_peaks": len(peaks)},
        "diagnostics": {"confidence": confidence, "relative_error_vs_fixture": round(rel_error, 5)},
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
