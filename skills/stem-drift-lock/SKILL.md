---
name: stem-drift-lock
slug: stem-drift-lock
technique: STEM
category: Alignment & drift
kind: MCP server
summary: Closed-loop drift correction for long atomic-resolution acquisitions
description: >
  Estimates specimen drift between scan frames and issues stage/scan-shift corrections, keeping atomic-resolution STEM acquisitions locked over multi-hour sessions.
org: emskills-mcp
repo: emskills-mcp/em-skills
version: 0.6.1
license: MIT
runtime: python 3.11
tool_call: lock_drift
tags:
  - drift
  - scan-shift
  - haadf
---

# stem-drift-lock

## Scope
Estimates specimen drift between scan frames and issues stage/scan-shift corrections, keeping atomic-resolution STEM acquisitions locked over multi-hour sessions.

Expects standard STEM data products (image stacks, spectra or session
directories as appropriate) with pixel size / dispersion recorded in the file
metadata. Out of scope: acquisition scheduling, sample preparation, and any
analysis outside the alignment & drift stage of the workflow.

## Safety
Issues stage and scan-shift corrections to the microscope. Limit corrections to the configured maximum step; abort on tracking loss rather than driving the stage blind.

## Usage
```json
{
  "tool": "lock_drift",
  "arguments": {
    "input": "/data/stem/session-001",
    "output": "/data/stem/session-001/lock_drift"
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
cd skills/stem-drift-lock
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
