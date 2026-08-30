#!/usr/bin/env python3
"""Reproducibility check for score_atlas.

Classifies each grid square's ice thickness in fixtures/sample/input.json
into good/marginal/bad against the fixture's stated thresholds, computes the
overall atlas score (fraction of good squares), and checks both against the
fixture's ground truth.
"""
import argparse
import json
from pathlib import Path


def classify(thickness, good_range, marginal_range):
    if good_range[0] <= thickness <= good_range[1]:
        return "good"
    if marginal_range[0] <= thickness <= marginal_range[1]:
        return "marginal"
    return "bad"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()  # --seed accepted for CLI symmetry; unused (fully deterministic)

    data = json.loads((Path(args.fixture) / "input.json").read_text())
    thicknesses = data["thickness_nm"]
    good_range = data["good_range_nm"]
    marginal_range = data["marginal_range_nm"]
    truth = data["ground_truth"]

    labels = [classify(t, good_range, marginal_range) for t in thicknesses]
    score = round(labels.count("good") / len(labels), 4)

    ok = labels == truth["labels"] and score == truth["score"]

    print(json.dumps({
        "ok": ok,
        "result": {"labels": labels, "score": score},
        "diagnostics": {
            "n_good": labels.count("good"),
            "n_marginal": labels.count("marginal"),
            "n_bad": labels.count("bad"),
        },
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
