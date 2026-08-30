---
name: tomo-align
slug: tomo-align
technique: TEM
category: Tilt series / tomography
kind: SKILL.md
summary: Fiducial-free tilt-series alignment with confidence-weighted reconstruction
description: >
  Aligns tilt series without fiducials using patch tracking, then reconstructs a 3D volume with per-voxel confidence maps for downstream segmentation.
org: emskills-mcp
repo: emskills-mcp/em-skills
version: 3.0.4
license: Apache-2.0
runtime: python 3.10
tool_call: align_tilt_series
tags:
  - tomography
  - patch-track
  - 3d
---

# tomo-align

## Scope
Aligns tilt series without fiducials using patch tracking, then reconstructs a 3D volume with per-voxel confidence maps for downstream segmentation.

Expects standard TEM data products (image stacks, spectra or session
directories as appropriate) with pixel size / dispersion recorded in the file
metadata. Out of scope: acquisition scheduling, sample preparation, and any
analysis outside the tilt series / tomography stage of the workflow.

## Safety
Read-only — no instrument control. The skill reads data from disk and returns results; it never moves the stage, changes dose, or alters column settings.

## Usage
```json
{
  "tool": "align_tilt_series",
  "arguments": {
    "input": "/data/tem/session-001",
    "output": "/data/tem/session-001/align_tilt_series"
  }
}
```

Returns a JSON object with `ok`, a `result` payload carrying the primary
measurement or map, and `diagnostics` with per-item confidence. Units are SI
unless stated otherwise in the result schema.

## Reproducibility
Runtime: `python 3.10`. Pin dependencies in `requirements.txt` / `package.json`
and run with a fixed seed. Reviewers can reproduce the reported numbers with:

```bash
cd skills/tomo-align
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
