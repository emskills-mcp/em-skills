---
name: provenance-verify
slug: provenance-verify
technique: SEM
category: Data integrity
kind: MCP server
summary: Check that a microscopy file is unchanged since it was sealed, and who signed it
description: >
  Verifies the cryptographic seal of a NUScope file (.h5, .nxs, .zarr, .tif): SHA-256 of the data,
  calibration, metadata (including the DataCite DOI of the instrument that collected it) and the
  hash-chained processing history, plus every Ed25519 signature with the signer's ORCID iD. Reports
  exactly which part changed if the file was modified.
org: NUANCE-IT
repo: NUANCE-IT/NUScope
version: 1.0.0
license: MIT
runtime: python 3.11
tool_call: nuscope_verify
tags:
  - provenance
  - integrity
  - signature
  - orcid
  - datacite
  - nuscope
---

# provenance-verify

## Scope
Before an agent trusts, analyzes or publishes a dataset, it should know the file is the one that was
recorded. This skill checks a NUScope file's seal and reports `signed`, `sealed` (intact, not signed),
`tampered` (with the failing parts: data, calibration, metadata, history, history chain) or `unsealed`.
It also lists the signers (name, ORCID iD, key, role, whether you trust the key) and the instrument DOIs the
seal covers. The technique is SEM for the registry, but the check works the same for TEM, STEM, EDS, EELS and
FIB-SEM files.

Served by the [NUScope](https://github.com/NUANCE-IT/NUScope) plugin of
[NUANCE-MCP](https://github.com/NUANCE-IT/NUANCE-MCP). With NUScope installed, every acquisition the server makes
is saved as a sealed, signed file. Out of scope: judging whether the measurement itself was right. A seal proves
the file is unchanged since sealing, not that the data are correct.

## Safety
Read-only: the tool only reads the file and returns a report. It never modifies data, signs anything or
contacts a network service.

## Usage
```json
{
  "tool": "nuscope_verify",
  "arguments": {
    "path": "/data/sem/2026-10-13/sample11.h5"
  }
}
```

Returns `status`, `ok`, `checks` (one boolean per part), `signatures` (name, orcid, fingerprint, role,
signed_at, valid, trusted), `instruments` (DOIs), `identifiers` (dataset DOIs), `seal_id` and `problems`.

## Reproducibility
Runtime: `python 3.11`. `fixtures/generate.py` writes one sealed, signed file (throwaway fixture key) and
two copies modified after sealing (one pixel; the beam voltage). The check requires the intact file to verify
and each modified copy to be flagged in exactly the right part:

```bash
cd skills/provenance-verify
pip install -r requirements.txt && python3 verify.py --fixture fixtures/sample --seed 0
```
