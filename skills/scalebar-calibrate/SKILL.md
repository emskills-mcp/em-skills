---
name: scalebar-calibrate
slug: scalebar-calibrate
technique: SEM
category: Calibration
kind: SKILL.md
summary: Magnification calibration against certified cross-grating standards
description: >
  Calibrates magnification and pixel size against certified cross-grating standards, producing a drift-corrected calibration record suitable for audit trails.
org: emskills-mcp
repo: emskills-mcp/em-skills
version: 1.0.2
license: MIT
runtime: node 20
tool_call: calibrate_scale
tags:
  - magnification
  - standard
  - audit
---

# scalebar-calibrate

## Scope
Calibrates magnification and pixel size against certified cross-grating standards, producing a drift-corrected calibration record suitable for audit trails.

Expects standard SEM data products (image stacks, spectra or session
directories as appropriate) with pixel size / dispersion recorded in the file
metadata. Out of scope: acquisition scheduling, sample preparation, and any
analysis outside the calibration stage of the workflow.

## Safety
Read-only — no instrument control. The skill reads data from disk and returns results; it never moves the stage, changes dose, or alters column settings.

## Usage
```json
{
  "tool": "calibrate_scale",
  "arguments": {
    "input": "/data/sem/session-001",
    "output": "/data/sem/session-001/calibrate_scale"
  }
}
```

Returns a JSON object with `ok`, a `result` payload carrying the primary
measurement or map, and `diagnostics` with per-item confidence. Units are SI
unless stated otherwise in the result schema.

## Reproducibility
Runtime: `node 20`. Pin dependencies in `requirements.txt` / `package.json`
and run with a fixed seed. Reviewers can reproduce the reported numbers with:

```bash
cd skills/scalebar-calibrate
npm install && node verify.js --fixture fixtures/sample --seed 0
```
