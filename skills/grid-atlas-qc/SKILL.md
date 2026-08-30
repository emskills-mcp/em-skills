---
name: grid-atlas-qc
slug: grid-atlas-qc
technique: cryo-EM
category: Image acquisition
kind: MCP server
summary: Ice-thickness estimation and automated grid-square quality triage
description: >
  Scores grid squares and foil holes from an atlas montage, estimating ice thickness and contamination to produce a ranked acquisition queue for automated data collection.
org: emskills-mcp
repo: emskills-mcp/em-skills
version: 1.5.0
license: MIT
runtime: python 3.11
tool_call: score_atlas
tags:
  - atlas
  - ice
  - triage
---

# grid-atlas-qc

## Scope
Scores grid squares and foil holes from an atlas montage, estimating ice thickness and contamination to produce a ranked acquisition queue for automated data collection.

Expects standard cryo-EM data products (image stacks, spectra or session
directories as appropriate) with pixel size / dispersion recorded in the file
metadata. Out of scope: acquisition scheduling, sample preparation, and any
analysis outside the image acquisition stage of the workflow.

## Safety
Read-only analysis of an existing atlas montage — no instrument control. Downstream queueing must be confirmed by an operator.

## Usage
```json
{
  "tool": "score_atlas",
  "arguments": {
    "input": "/data/cryo-em/session-001",
    "output": "/data/cryo-em/session-001/score_atlas"
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
cd skills/grid-atlas-qc
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
