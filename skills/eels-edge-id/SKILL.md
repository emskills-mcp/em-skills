---
name: eels-edge-id
slug: eels-edge-id
technique: EELS
category: Spectrum analysis
kind: MCP server
summary: Core-loss edge identification and oxidation-state fingerprinting
description: >
  Identifies core-loss edges in EELS spectra, fits fine structure, and fingerprints oxidation states against a reference library. Returns candidate assignments with confidence intervals.
org: emskills-mcp
repo: emskills-mcp/em-skills
version: 1.2.7
license: BSD-3-Clause
runtime: python 3.11
tool_call: identify_edges
tags:
  - core-loss
  - elnes
  - oxidation
---

# eels-edge-id

## Scope
Identifies core-loss edges in EELS spectra, fits fine structure, and fingerprints oxidation states against a reference library. Returns candidate assignments with confidence intervals.

Expects standard EELS data products (image stacks, spectra or session
directories as appropriate) with pixel size / dispersion recorded in the file
metadata. Out of scope: acquisition scheduling, sample preparation, and any
analysis outside the spectrum analysis stage of the workflow.

## Safety
Read-only — no instrument control. The skill reads data from disk and returns results; it never moves the stage, changes dose, or alters column settings.

## Usage
```json
{
  "tool": "identify_edges",
  "arguments": {
    "input": "/data/eels/session-001",
    "output": "/data/eels/session-001/identify_edges"
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
cd skills/eels-edge-id
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
