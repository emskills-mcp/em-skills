---
name: tem-view-twin
slug: tem-view-twin
technique: TEM
category: Simulation
kind: SKILL.md
summary: Physics-based TEM digital twin that simulates calibrated images, diffraction, spectra and holograms
description: >
  Runs the TEM-view digital twin (Seeing with Electrons) headlessly: wave-optical imaging with the
  contrast transfer function, electron diffraction, STEM and 4D-STEM, CBED and the Ronchigram, EDS and
  EELS, off-axis and in-line holography, with cryo and heating holders. Returns NumPy data with
  calibrations from metadata, so other skills can be tested on known ground truth. A live mode lets an
  agent drive an open exhibit and answer a visitor's spoken questions (temview-mcp).
org: Advanced-EM
repo: Advanced-EM/TEM-view
version: 1.0.0
license: MIT
runtime: node 20
tool_call: simulate_tem
tags:
  - simulation
  - digital-twin
  - diffraction
  - ctf
  - training
  - voice
---

# tem-view-twin

## Scope
Simulates what a transmission electron microscope records. The simulator covers ten modes: TEM, STEM, 4D-STEM,
SAED, CBED, EDS, EELS, the Ronchigram, and off-axis and in-line holography. Six specimens are built in: gold
nanoparticles on carbon, silicon, an SrTiO₃ grain boundary, graphene, the UiO-66 MOF, and proteins in vitreous
ice.

Settings: accelerating voltage, defocus, aberration corrector, dose, thickness, holder and temperature.

The output is a NumPy `.npz` with `metadata.json`, which carries the calibrations (Å per pixel, Å⁻¹ per pixel,
eV per channel), the optics (wavelength, Cs, focal spread) and the full state. The data is simulated: use it to
build, test and teach analysis workflows on known ground truth, not as a measurement of a real specimen.
Instrument-specific behavior can be set with an instrument profile (TEM-view's digital-twin profile).

The MCP server [`temview-mcp`](https://github.com/Advanced-EM/TEM-view/tree/main/tools/temview-mcp) exposes
two kinds of tools:
- `simulate`: this skill's tool.
- Live tools for an open exhibit: `exhibit_set`, `exhibit_acquire`, `exhibit_say`, and
  `exhibit_wait_for_voice`, which waits for a visitor's spoken question.

## Safety
Simulation only. The twin never touches a real instrument. In live mode it changes only the simulator a
visitor has open, after they click *Connect agent*, and it refuses changes while a recorded training task is
running. Voice commands are push-to-talk; the exhibit records only what a command did, never audio or
transcripts of questions.

## Usage
```json
{
  "tool": "simulate_tem",
  "arguments": {
    "mode": "diff",
    "specimen": "au",
    "kV": 300,
    "defocus_nm": 0,
    "out": "/data/sim/au-saed.npz"
  }
}
```

Returns a JSON object with `ok`, a `result` carrying the output path, array shapes, calibration and optics,
and `diagnostics` with the simulator version. Lengths in the metadata are in Å or nm as labeled, and energies
in eV.

## Reproducibility
Runtime: `node 20`. The simulator is pinned to a TEM-view commit in `package.json`. The check simulates a
selected-area diffraction pattern of gold at 200 and 300 kV. It then indexes the (111), (200) and (220) rings
from the radial profile, using only the calibration in the metadata, and must recover each spacing within 2.5 %
and the fcc lattice constant (4.0782 Å) within 1 %. Reviewers can reproduce the numbers with:

```bash
cd skills/tem-view-twin
npm install --no-fund --no-audit && node verify.js --fixture fixtures/sample --seed 0
```
