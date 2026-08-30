---
name: particle-picker
slug: particle-picker
technique: cryo-EM
category: Segmentation
kind: MCP server
summary: Template-free particle picking tuned for low signal-to-noise micrographs
description: >
  Template-free particle picking with a denoising front-end for low signal-to-noise micrographs. Emits coordinate star files and per-pick confidence.
org: emskills-mcp
repo: emskills-mcp/em-skills
version: 2.0.0
license: MIT
runtime: python 3.11
tool_call: pick_particles
tags:
  - picking
  - denoise
  - star
---

# particle-picker

## Scope
Template-free particle picking with a denoising front-end for low signal-to-noise micrographs. Emits coordinate star files and per-pick confidence.

Expects standard cryo-EM data products (image stacks, spectra or session
directories as appropriate) with pixel size / dispersion recorded in the file
metadata. Out of scope: acquisition scheduling, sample preparation, and any
analysis outside the segmentation stage of the workflow.

## Safety
Read-only — no instrument control. The skill reads data from disk and returns results; it never moves the stage, changes dose, or alters column settings.

## Usage
```json
{
  "tool": "pick_particles",
  "arguments": {
    "input": "/data/cryo-em/session-001",
    "output": "/data/cryo-em/session-001/pick_particles"
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
cd skills/particle-picker
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
