#!/usr/bin/env python3
"""Reproducibility check for nuscope_verify.

Verifies the three fixture files with NUScope and checks that the intact file
is reported signed (data, calibration, metadata, history and hash chain all
intact, signature valid), and that the two modified copies are reported
tampered with exactly the right part flagged. Prints the tool-style result
and exits 0 on success.
"""
import argparse
import json
import os
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="fixtures/sample")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()  # --seed accepted for CLI symmetry; verification is deterministic

    # an empty identity folder: the verdicts must not depend on who runs the check
    os.environ["EMDATABRIDGE_HOME"] = tempfile.mkdtemp(prefix="emskills-verify-")
    import nuscope as ns

    fx = Path(args.fixture)
    data = json.loads((fx / "input.json").read_text())
    reports, checks = {}, {}
    for name in data["files"]:
        r = ns.verify(fx / name)
        truth = data["ground_truth"][name]
        failed = sorted(k for k, v in r.checks.items() if not v)
        reports[name] = {"status": r.status, "failed_checks": failed, "seal": r.seal_id,
                         "signed_by": [s["name"] for s in r.signatures if s["valid"]]}
        checks[name] = r.status == truth["status"] and failed == truth["failed_checks"] and (
            "signer" not in truth or reports[name]["signed_by"] == [truth["signer"]])
    result = {"ok": all(checks.values()), "result": reports,
              "diagnostics": {"checks": checks, "nuscope": ns.__version__}}
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
