#!/usr/bin/env python3
"""Reproducibility check for phase_map.

Subtracts a rolling-minimum background from the EDS spectrum in
fixtures/sample/input.json, finds local-maximum peaks above a noise
threshold, matches each to the nearest reference characteristic line, and
checks the identified element set against the fixture's ground truth.
"""
import argparse
import json
from pathlib import Path

MATCH_TOLERANCE_KEV = 0.05
MIN_PEAK_HEIGHT = 30.0
BACKGROUND_WINDOW = 25


def rolling_min(values, window):
    half = window // 2
    out = []
    for i in range(len(values)):
        lo, hi = max(0, i - half), min(len(values), i + half + 1)
        out.append(min(values[lo:hi]))
    return out


def find_peaks(energies, signal, min_height):
    peaks = []
    for i in range(1, len(signal) - 1):
        if signal[i] > min_height and signal[i] >= signal[i - 1] and signal[i] >= signal[i + 1]:
            peaks.append((energies[i], signal[i]))
    return peaks


def match_element(energy, reference_lines):
    best_el, best_dist = None, MATCH_TOLERANCE_KEV
    for el, line_energy in reference_lines.items():
        dist = abs(energy - line_energy)
        if dist <= best_dist:
            best_el, best_dist = el, dist
    return best_el


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()  # --seed accepted for CLI symmetry; unused (fully deterministic)

    data = json.loads((Path(args.fixture) / "input.json").read_text())
    energies = data["energies_kev"]
    counts = data["counts"]
    reference_lines = data["reference_lines_kev"]
    truth = set(data["ground_truth"]["elements"])

    background = rolling_min(counts, BACKGROUND_WINDOW)
    net = [c - b for c, b in zip(counts, background)]
    peaks = find_peaks(energies, net, MIN_PEAK_HEIGHT)

    identified = {}
    for energy, height in peaks:
        el = match_element(energy, reference_lines)
        if el and (el not in identified or height > identified[el][1]):
            identified[el] = (round(energy, 3), round(height, 1))

    ok = set(identified.keys()) == truth

    print(json.dumps({
        "ok": ok,
        "result": {"elements": sorted(identified.keys()), "peaks": identified},
        "diagnostics": {"n_peaks_found": len(peaks), "expected_elements": sorted(truth)},
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
