---
name: lattice-dspacing
slug: lattice-dspacing
technique: STEM
category: Reconstruction
kind: SKILL.md
summary: Bayesian d-spacing measurement and lattice fitting from HRSTEM images
description: >
  Measures d-spacings and fits atomic lattices from high-resolution STEM images using Bayesian inference, reporting posterior intervals for each lattice parameter.
org: emskills-mcp
repo: emskills-mcp/em-skills
version: 1.4.3
license: BSD-3-Clause
runtime: python 3.10
tool_call: fit_lattice
tags:
  - lattice
  - dspacing
  - bayesian
---

# lattice-dspacing

## Scope
Measures d-spacings and fits atomic lattices from high-resolution STEM images using Bayesian inference, reporting posterior intervals for each lattice parameter.

Expects standard STEM data products (image stacks, spectra or session
directories as appropriate) with pixel size / dispersion recorded in the file
metadata. Out of scope: acquisition scheduling, sample preparation, and any
analysis outside the reconstruction stage of the workflow.

## Safety
Read-only — no instrument control. The skill reads data from disk and returns results; it never moves the stage, changes dose, or alters column settings.

## Usage
```json
{
  "tool": "fit_lattice",
  "arguments": {
    "input": "/data/stem/session-001",
    "output": "/data/stem/session-001/fit_lattice"
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
cd skills/lattice-dspacing
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
