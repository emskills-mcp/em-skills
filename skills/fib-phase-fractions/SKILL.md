---
name: fib-phase-fractions
slug: fib-phase-fractions
technique: FIB
category: Segmentation
kind: MCP server
summary: Phase volume fractions of a FIB-SEM volume with sampling error bars
description: >
  Computes the volume fraction and surface density of every phase in a segmented FIB-SEM (slice-and-view)
  volume, in physical units from the voxel size, with a sampling standard error estimated from the
  covariance integral range: how much the fraction could change with another field of view of the same size.
org: NUANCE-IT
repo: NUANCE-IT/NUScope-TOMO
version: 1.0.0
license: MIT
runtime: python 3.11
tool_call: tomo_phase_fractions
tags:
  - fib-sem
  - slice-and-view
  - volume-fraction
  - representative-volume
  - uncertainty
  - nuscope-tomo
---

# fib-phase-fractions

## Scope
Answers "how much of each phase is there, and how sure are we?" for a labelled volume (`.zarr`) written by a
NUScope-TOMO recipe, e.g. `volumes/phases.zarr`. For each phase it returns the volume fraction, its sampling
standard error, the surface density S/V (1/µm) and its error, and the analysed volume (µm³). Label 0 is treated
as background and left out. Anisotropic voxels (slice thickness ≠ pixel size) are handled.

Served by the [NUScope-TOMO](https://github.com/NUANCE-IT/NUScope-TOMO) plugin of
[NUANCE-MCP](https://github.com/NUANCE-IT/NUANCE-MCP) (`pip install nuance-mcp nuscope-tomo`, version 0.3.2 or
later for this tool). An agent can follow it with `tomo_project`, `tomo_table` and `tomo_run` to inspect a
project or re-run its recipe. Out of scope: segmentation itself (done by the recipe), and acquisition.

## Safety
Read-only: no instrument control. The tool reads a labelled volume and returns numbers. It never moves the stage,
mills, or changes the beam, and never writes into the project.

## Usage
```json
{
  "tool": "tomo_phase_fractions",
  "arguments": {
    "labels": "/data/fib/sample335/volumes/phases.zarr"
  }
}
```

Returns `voxel_nm`, `volume_um3` and `phases`, a list of `{phase, name, fraction, fraction_se, sv_um-1, sv_se,
volume_um3}`. A fraction is reported to ±2 × `fraction_se` (95 %); if that is too wide, the analysed volume is
too small for the microstructure.

## Reproducibility
Runtime: `python 3.11`. `fixtures/generate.py` builds a 24 × 48 × 48 labelled volume (20 nm slices, 10 nm
pixels) of matrix, particle and pore spheres (seed 0). The check recovers the exact voxel-count fractions and
requires finite, positive errors and surface densities:

```bash
cd skills/fib-phase-fractions
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
