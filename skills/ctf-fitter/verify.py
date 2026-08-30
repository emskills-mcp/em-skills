#!/usr/bin/env python3
"""Reproducibility check for fit_ctf.

Grid-searches defocus (the actual unknown; wavelength and envelope are
treated as known calibration inputs, as in real CTF fitting) to minimize
squared error against the observed power spectrum in fixtures/sample/input.json,
then checks the recovered defocus against the fixture's ground truth.
"""
import argparse
import json
import math
from pathlib import Path


def ctf(s: float, wavelength: float, defocus: float) -> float:
    return -math.sin(math.pi * wavelength * defocus * s * s)


def model_spectrum(s_values, wavelength, envelope_alpha, defocus):
    out = []
    for s in s_values:
        envelope = math.exp(-envelope_alpha * s * s)
        out.append((ctf(s, wavelength, defocus) ** 2) * envelope)
    return out


def sse(observed, predicted):
    return sum((o - p) ** 2 for o, p in zip(observed, predicted))


def grid_search(s_values, wavelength, envelope_alpha, observed, lo, hi, steps, seed):
    best_defocus, best_err = None, math.inf
    # `seed` has no effect on this deterministic grid search; accepted for
    # CLI symmetry with the other skills' verify scripts.
    del seed
    for i in range(steps + 1):
        defocus = lo + (hi - lo) * i / steps
        predicted = model_spectrum(s_values, wavelength, envelope_alpha, defocus)
        err = sse(observed, predicted)
        if err < best_err:
            best_defocus, best_err = defocus, err
    return best_defocus, best_err


def refine(s_values, wavelength, envelope_alpha, observed, center, span, seed):
    lo, hi = center - span, center + span
    for _ in range(4):
        center, _ = grid_search(s_values, wavelength, envelope_alpha, observed, lo, hi, 50, seed)
        span /= 10
        lo, hi = center - span, center + span
    return center


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    data = json.loads((Path(args.fixture) / "input.json").read_text())
    s_values = data["s_values"]
    observed = data["power_spectrum"]
    wavelength = data["wavelength_angstrom"]
    envelope_alpha = data["envelope_alpha"]
    truth = data["ground_truth"]["defocus_angstrom"]

    coarse, _ = grid_search(s_values, wavelength, envelope_alpha, observed, 1000, 40000, 400, args.seed)
    estimated = refine(s_values, wavelength, envelope_alpha, observed, coarse, 2000, args.seed)

    rel_error = abs(estimated - truth) / truth
    ok = rel_error < 0.01

    print(json.dumps({
        "ok": ok,
        "result": {"defocus_angstrom": round(estimated, 2)},
        "diagnostics": {"relative_error_vs_fixture": round(rel_error, 5)},
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
