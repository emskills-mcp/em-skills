#!/usr/bin/env python3
"""Generate the fixture for provenance-verify.

Makes three NUScope files from one small synthetic SEM image (64 x 64, 10 nm):

* intact.h5            sealed and signed with a throwaway key made for this fixture
                       (in a temporary folder, deleted afterwards: never a personal key);
* pixel_changed.h5     the same file with one pixel changed after sealing;
* metadata_changed.h5  the same file with the beam voltage edited after sealing.

Ground truth: what verification must report for each. Seals contain timestamps and the
throwaway key is random, so re-running produces new bytes with the same verdicts.
"""
import json
import os
import shutil
import tempfile
from pathlib import Path

import h5py
import numpy as np

SEED = 0


def main() -> None:
    out = Path(__file__).parent / "sample"
    out.mkdir(exist_ok=True)
    home = tempfile.mkdtemp(prefix="emskills-fixture-")
    os.environ["EMDATABRIDGE_HOME"] = home          # isolate: never read or write a personal identity
    os.environ["NUSCOPE_HOME"] = home
    try:
        import nuscope as ns
        from EMDataBridge import identity
        identity.create("em-skills fixture key")
        rng = np.random.default_rng(SEED)
        img = (rng.normal(100, 5, (64, 64)) + 80 * (np.indices((64, 64)).sum(0) % 16 < 8)).astype(np.float32)
        ds = ns.Dataset.from_array(img, pixel_size_nm=10.0, name="fixture")
        ds.metadata["beam"]["voltage_kV"] = 5.0
        ds.metadata["technique"] = "SEM"
        intact = ns.save(ds, out / "intact.h5", overwrite=True)
        shutil.copy(intact, out / "pixel_changed.h5")
        with h5py.File(out / "pixel_changed.h5", "r+") as f:
            f["entry/data/data"][10, 10] += 1
        shutil.copy(intact, out / "metadata_changed.h5")
        with h5py.File(out / "metadata_changed.h5", "r+") as f:
            n = f["entry/nuscope"]
            m = json.loads(n["metadata"][()])
            m["beam"]["voltage_kV"] = 30.0
            del n["metadata"]
            n["metadata"] = json.dumps(m)
    finally:
        shutil.rmtree(home, ignore_errors=True)
    (out / "input.json").write_text(json.dumps({
        "files": ["intact.h5", "pixel_changed.h5", "metadata_changed.h5"],
        "ground_truth": {
            "intact.h5": {"status": "signed", "failed_checks": [], "signer": "em-skills fixture key"},
            "pixel_changed.h5": {"status": "tampered", "failed_checks": ["data"]},
            "metadata_changed.h5": {"status": "tampered", "failed_checks": ["metadata"]},
        },
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
