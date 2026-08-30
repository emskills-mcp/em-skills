#!/usr/bin/env python3
"""Generate the deterministic fixture for ctf-fitter.

Builds a synthetic radial power spectrum from a simplified (defocus-only,
no spherical aberration) CTF model at a known defocus, with a Gaussian
envelope and small additive noise. Seed is fixed so re-running this script
reproduces the committed fixtures/sample/input.json exactly.
"""
import json
import math
import random
from pathlib import Path

SEED = 0
WAVELENGTH_ANGSTROM = 0.0197  # ~300 kV electrons
ENVELOPE_ALPHA = 40.0
TRUE_DEFOCUS_ANGSTROM = 18000.0  # 1.8 um, typical underfocus
N_BINS = 120
S_MAX = 0.5  # 1/Angstrom
NOISE_SIGMA = 0.01


def ctf(s: float, defocus: float) -> float:
    return -math.sin(math.pi * WAVELENGTH_ANGSTROM * defocus * s * s)


def main() -> None:
    rng = random.Random(SEED)
    s_values = [S_MAX * (i + 1) / N_BINS for i in range(N_BINS)]
    power = []
    for s in s_values:
        envelope = math.exp(-ENVELOPE_ALPHA * s * s)
        signal = (ctf(s, TRUE_DEFOCUS_ANGSTROM) ** 2) * envelope
        power.append(round(signal + rng.gauss(0, NOISE_SIGMA), 6))

    fixture = {
        "wavelength_angstrom": WAVELENGTH_ANGSTROM,
        "envelope_alpha": ENVELOPE_ALPHA,
        "s_values": s_values,
        "power_spectrum": power,
        "ground_truth": {"defocus_angstrom": TRUE_DEFOCUS_ANGSTROM},
    }
    out = Path(__file__).parent / "sample" / "input.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(fixture, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
