---
name: sem-particle-size
slug: sem-particle-size
technique: SEM
category: Segmentation
kind: MCP server
summary: Particle sizing in calibrated nm from any NUANCE SEM file, with provenance
description: >
  Finds particles in an SEM image and measures area, equivalent diameter, Feret, aspect ratio and
  circularity in nm, using the pixel size read from the instrument's own metadata (Thermo Fisher, Zeiss,
  Hitachi, JEOL, Gatan and 40+ formats via NUScope). The result table carries a hash-chained history of
  how it was made.
org: NUANCE-IT
repo: NUANCE-IT/NUScope
version: 1.0.0
license: MIT
runtime: python 3.11
tool_call: nuscope_analyze
tags:
  - particles
  - morphometry
  - calibration
  - provenance
  - nuscope
---

# sem-particle-size

## Scope
Measures particles (or any bright or dark features) in a single SEM image in physical units. The pixel size
comes from the file's own metadata, so results are in nm without manual calibration, and burned-in data bars
are removed before analysis. Options: `method` (`otsu` threshold), `dark` (dark features), `min_area_nm2`,
`exclude_border`, and `separate` (watershed split of touching particles).

Served by the [NUScope](https://github.com/NUANCE-IT/NUScope) plugin of
[NUANCE-MCP](https://github.com/NUANCE-IT/NUANCE-MCP) (`pip install nuance-mcp nuscope`). The plugin also saves
every acquisition as a sealed NUScope file that this tool can analyze. Out of scope: acquisition, 3D
(see `fib-phase-fractions`), and phase identification.

## Safety
Read-only: no instrument control. The tool reads a file and returns a table. It never moves the stage, changes
the beam, or overwrites the input. Image results of other `nuscope_analyze` operations are written as new
files next to the input.

## Usage
```json
{
  "tool": "nuscope_analyze",
  "arguments": {
    "path": "/data/sem/sample11.tif",
    "op": "particles",
    "params": {"min_area_nm2": 2000, "separate": false}
  }
}
```

Returns `rows` (particle count), `columns`, `head` (first rows), `describe` (summary statistics per column)
and `area_fraction`. Lengths are in nm, areas in nm², angles in degrees.

## Reproducibility
Runtime: `python 3.11`. The fixture is a 256 × 256 Thermo Fisher-style SEM TIFF (10 nm pixels in its INI
metadata) with 12 disks of known size, made by `fixtures/generate.py` (seed 0). The check recovers the count,
the calibration and every diameter within 3 %:

```bash
cd skills/sem-particle-size
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
