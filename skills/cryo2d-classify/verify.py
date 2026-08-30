#!/usr/bin/env python3
"""Reproducibility check for 2d_classify.

Runs a minimal k-means (k=2) 2D classification over the particle stack in
fixtures/sample/input.json and checks recovered labels against the fixture's
ground truth, up to a global label permutation.
"""
import argparse
import json
import random
from pathlib import Path


def kmeans(vectors, k, seed, iterations=25):
    rng = random.Random(seed)
    centroids = [list(v) for v in rng.sample(vectors, k)]
    labels = [0] * len(vectors)
    for _ in range(iterations):
        changed = False
        for i, v in enumerate(vectors):
            dists = [sum((a - b) ** 2 for a, b in zip(v, c)) for c in centroids]
            new_label = dists.index(min(dists))
            if new_label != labels[i]:
                changed = True
            labels[i] = new_label
        for c_idx in range(k):
            members = [v for v, l in zip(vectors, labels) if l == c_idx]
            if members:
                centroids[c_idx] = [sum(vals) / len(members) for vals in zip(*members)]
        if not changed:
            break
    return labels, centroids


def per_item_confidence(vectors, centroids):
    diagnostics = []
    for v in vectors:
        dists = sorted(sum((a - b) ** 2 for a, b in zip(v, c)) for c in centroids)
        best, second = dists[0], dists[1]
        diagnostics.append(round(1 - best / second, 4) if second > 0 else 1.0)
    return diagnostics


def label_accuracy(pred, truth):
    direct = sum(p == t for p, t in zip(pred, truth)) / len(truth)
    swapped = sum((1 - p) == t for p, t in zip(pred, truth)) / len(truth)
    return max(direct, swapped)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    data = json.loads((Path(args.fixture) / "input.json").read_text())
    vectors = data["particles"]
    truth = data["ground_truth"]["labels"]
    k = data["ground_truth"]["n_classes"]

    labels, centroids = kmeans(vectors, k, args.seed)
    diagnostics = per_item_confidence(vectors, centroids)
    accuracy = label_accuracy(labels, truth)
    ok = accuracy == 1.0

    print(json.dumps({
        "ok": ok,
        "result": {"labels": labels, "n_classes": k},
        "diagnostics": {"per_item_confidence": diagnostics, "accuracy_vs_fixture": accuracy},
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
