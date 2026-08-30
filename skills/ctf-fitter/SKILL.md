---
name: ctf-fitter
slug: ctf-fitter
technique: TEM
category: Calibration
kind: SKILL.md
summary: Per-tilt CTF estimation and refinement with amorphous-carbon reference subtraction
description: >
  Per-tilt contrast transfer function estimation and refinement for TEM diffraction patterns. Handles amorphous-carbon reference subtraction, astigmatism fitting, and defocus drift across a tilt series.
org: emskills-mcp
repo: emskills-mcp/em-skills
version: 3.1.2
license: Apache-2.0
runtime: python 3.11
tool_call: fit_ctf
tags:
  - ctf
  - defocus
  - tilt
---

# ctf-fitter

## Scope
Per-tilt contrast transfer function estimation and refinement for TEM diffraction patterns. Handles amorphous-carbon reference subtraction, astigmatism fitting, and defocus drift across a tilt series.

Expects standard TEM data products (image stacks, spectra or session
directories as appropriate) with pixel size / dispersion recorded in the file
metadata. Out of scope: acquisition scheduling, sample preparation, and any
analysis outside the calibration stage of the workflow.

## Safety
Read-only — no instrument control. The skill reads data from disk and returns results; it never moves the stage, changes dose, or alters column settings.

## Usage
```json
{
  "tool": "fit_ctf",
  "arguments": {
    "input": "/data/tem/session-001",
    "output": "/data/tem/session-001/fit_ctf"
  }
}
```

Returns a JSON object with `ok`, a `result` payload carrying the primary
measurement or map, and `diagnostics` with per-item confidence. Units are SI
unless stated otherwise in the result schema.

## Reproducibility
Runtime: `python 3.11`. Pin dependencies in `requirements.txt` / `package.json`
and run with a fixed seed. Reviewers can reproduce the reported numbers with:

```bash
cd skills/ctf-fitter
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
