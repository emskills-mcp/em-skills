---
name: edax-phase-map
slug: edax-phase-map
technique: EDS
category: Spectrum analysis
kind: MCP server
summary: Phase mapping from dispersive spectra with peak deconvolution and ZAF correction
description: >
  Super-resolution phase mapping from energy dispersive spectra. Performs automatic peak deconvolution, background subtraction, and ZAF quantification, returning per-pixel elemental fractions plus a labelled phase map.
org: emskills-mcp
repo: emskills-mcp/em-skills
version: 1.9.0
license: MIT
runtime: python 3.10
tool_call: phase_map
tags:
  - eds
  - quant
  - zaf
---

# edax-phase-map

## Scope
Super-resolution phase mapping from energy dispersive spectra. Performs automatic peak deconvolution, background subtraction, and ZAF quantification, returning per-pixel elemental fractions plus a labelled phase map.

Expects standard EDS data products (image stacks, spectra or session
directories as appropriate) with pixel size / dispersion recorded in the file
metadata. Out of scope: acquisition scheduling, sample preparation, and any
analysis outside the spectrum analysis stage of the workflow.

## Safety
Read-only — no instrument control. The skill reads data from disk and returns results; it never moves the stage, changes dose, or alters column settings.

## Usage
```json
{
  "tool": "phase_map",
  "arguments": {
    "input": "/data/eds/session-001",
    "output": "/data/eds/session-001/phase_map"
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
cd skills/edax-phase-map
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
