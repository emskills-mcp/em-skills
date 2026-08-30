---
name: fib-mill-seg
slug: fib-mill-seg
technique: FIB
category: Segmentation
kind: MCP server
summary: Mill-volume segmentation and lift-out path planning for serial sectioning
description: >
  Segments the mill volume from live FIB imagery and plans a lift-out path for serial-sectioning workflows, including lamella thickness targets and redeposition avoidance.
org: emskills-mcp
repo: emskills-mcp/em-skills
version: 0.8.3
license: MIT
runtime: python 3.11
tool_call: plan_liftout
tags:
  - lamella
  - liftout
  - planning
---

# fib-mill-seg

## Scope
Segments the mill volume from live FIB imagery and plans a lift-out path for serial-sectioning workflows, including lamella thickness targets and redeposition avoidance.

Expects standard FIB data products (image stacks, spectra or session
directories as appropriate) with pixel size / dispersion recorded in the file
metadata. Out of scope: acquisition scheduling, sample preparation, and any
analysis outside the segmentation stage of the workflow.

## Safety
Plans ion-beam milling paths. Milling and stage moves are **destructive**; this skill only emits a plan — a human must confirm before any FIB current is applied.

## Usage
```json
{
  "tool": "plan_liftout",
  "arguments": {
    "input": "/data/fib/session-001",
    "output": "/data/fib/session-001/plan_liftout"
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
cd skills/fib-mill-seg
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
