---
name: cryo2d-classify
slug: cryo2d-classify
technique: cryo-EM
category: Segmentation
kind: MCP server
summary: Reference-free 2D classification of particle micrographs with a motion-correction pre-pass
description: >
  Reference-free 2D classification of cryo-EM particle micrographs. Includes motion correction, contrast transfer estimation, and clustering with configurable binning and angular sampling. Exposes a typed MCP toolset for batch runs against a session directory.
org: emskills-mcp
repo: emskills-mcp/em-skills
version: 2.4.1
license: MIT
runtime: python 3.11
tool_call: 2d_classify
tags:
  - 2d
  - cluster
  - ctf
---

# cryo2d-classify

## Scope
Reference-free 2D classification of cryo-EM particle micrographs. Includes motion correction, contrast transfer estimation, and clustering with configurable binning and angular sampling. Exposes a typed MCP toolset for batch runs against a session directory.

Expects standard cryo-EM data products (image stacks, spectra or session
directories as appropriate) with pixel size / dispersion recorded in the file
metadata. Out of scope: acquisition scheduling, sample preparation, and any
analysis outside the segmentation stage of the workflow.

## Safety
Read-only — no instrument control. The skill reads data from disk and returns results; it never moves the stage, changes dose, or alters column settings.

## Usage
```json
{
  "tool": "2d_classify",
  "arguments": {
    "input": "/data/cryo-em/session-001",
    "output": "/data/cryo-em/session-001/2d_classify"
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
cd skills/cryo2d-classify
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
