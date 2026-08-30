#!/usr/bin/env python3
"""Reproducibility check for identify_edges.

Fits a power-law background from the pre-edge window of the spectrum in
fixtures/sample/input.json (log-log linear regression), subtracts it,
locates the first sustained rise above the pre-edge noise floor as the edge
onset, matches it to the nearest reference core-loss edge, and checks the
result against the fixture's ground truth.
"""
import argparse
import json
import math
from pathlib import Path

PRE_EDGE_FRACTION = 0.15
ONSET_SIGMA_THRESHOLD = 5.0
SUSTAIN_POINTS = 5
MATCH_TOLERANCE_EV = 10.0


def linreg(xs, ys):
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    var = sum((x - mean_x) ** 2 for x in xs)
    slope = cov / var
    intercept = mean_y - slope * mean_x
    return slope, intercept


def fit_power_law_background(energies, counts, n_pre):
    log_e = [math.log(e) for e in energies[:n_pre]]
    log_i = [math.log(max(c, 1e-6)) for c in counts[:n_pre]]
    slope, intercept = linreg(log_e, log_i)  # ln(I) = intercept + slope*ln(E)
    return lambda e: math.exp(intercept) * e ** slope


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()  # --seed accepted for CLI symmetry; unused (fully deterministic)

    data = json.loads((Path(args.fixture) / "input.json").read_text())
    energies = data["energies_ev"]
    counts = data["counts"]
    reference_edges = data["reference_edges_ev"]
    truth = data["ground_truth"]

    n_pre = int(len(energies) * PRE_EDGE_FRACTION)
    background = fit_power_law_background(energies, counts, n_pre)
    residual = [c - background(e) for e, c in zip(energies, counts)]

    pre_residual = residual[:n_pre]
    noise_std = (sum((r - sum(pre_residual) / n_pre) ** 2 for r in pre_residual) / n_pre) ** 0.5
    threshold = ONSET_SIGMA_THRESHOLD * noise_std

    onset_ev = None
    for i in range(n_pre, len(residual) - SUSTAIN_POINTS):
        if all(residual[i + k] > threshold for k in range(SUSTAIN_POINTS)):
            onset_ev = energies[i]
            break

    matched_edge, matched_dist = None, MATCH_TOLERANCE_EV
    if onset_ev is not None:
        for name, edge_ev in reference_edges.items():
            dist = abs(onset_ev - edge_ev)
            if dist <= matched_dist:
                matched_edge, matched_dist = name, dist

    ok = (
        matched_edge == truth["edge"]
        and onset_ev is not None
        and abs(onset_ev - truth["onset_ev"]) <= MATCH_TOLERANCE_EV
    )

    print(json.dumps({
        "ok": ok,
        "result": {"edge": matched_edge, "onset_ev": onset_ev},
        "diagnostics": {"noise_std": round(noise_std, 3), "expected": truth},
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
