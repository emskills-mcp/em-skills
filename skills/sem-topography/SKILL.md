---
name: sem-topography
slug: sem-topography
technique: SEM
category: Reconstruction
kind: SKILL.md
summary: 3D surface relief reconstruction from four-quadrant backscattered stacks
description: >
  Reconstructs 3D surface relief from four-quadrant backscattered electron stacks, returning a height field with per-pixel confidence and roughness statistics.
org: emskills-mcp
repo: emskills-mcp/em-skills
version: 2.4.0
license: MIT
runtime: python 3.10
tool_call: reconstruct_relief
tags:
  - bse
  - height
  - roughness
---

# sem-topography

## Scope
Reconstructs 3D surface relief from four-quadrant backscattered electron stacks, returning a height field with per-pixel confidence and roughness statistics.

Expects standard SEM data products (image stacks, spectra or session
directories as appropriate) with pixel size / dispersion recorded in the file
metadata. Out of scope: acquisition scheduling, sample preparation, and any
analysis outside the reconstruction stage of the workflow.

## Safety
Read-only — no instrument control. The skill reads data from disk and returns results; it never moves the stage, changes dose, or alters column settings.

## Usage
```json
{
  "tool": "reconstruct_relief",
  "arguments": {
    "input": "/data/sem/session-001",
    "output": "/data/sem/session-001/reconstruct_relief"
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
cd skills/sem-topography
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
