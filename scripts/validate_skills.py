#!/usr/bin/env python3
"""Validate skills/ against the registry contract documented in README.md.

Usage: python3 scripts/validate_skills.py [--strict]

Exits non-zero if any error-level finding is present. Warnings never fail
the run unless --strict is passed.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
README = ROOT / "README.md"

RUNTIME_TOOLING = {
    "python": {"verify": "verify.py", "deps": "requirements.txt"},
    "node": {"verify": "verify.js", "deps": "package.json"},
}

REQUIRED_FRONTMATTER_KEYS = [
    "name", "slug", "technique", "category", "kind", "summary",
    "license", "version", "runtime", "tool_call",
]
REQUIRED_BODY_SECTIONS = ["## Scope", "## Safety", "## Usage"]

ALLOWED_TECHNIQUES = {"SEM", "TEM", "STEM", "EDS", "EELS", "cryo-EM", "FIB"}
KNOWN_LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "GPL-3.0", "ISC"}

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TOOL_CALL_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


class Findings:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def load_frontmatter(text: str, findings: Findings, where: str) -> tuple[dict, str] | tuple[None, None]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        findings.error(f"{where}: missing or malformed YAML front-matter block")
        return None, None
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        findings.error(f"{where}: front-matter is not valid YAML ({e})")
        return None, None
    if not isinstance(fm, dict):
        findings.error(f"{where}: front-matter did not parse to a mapping")
        return None, None
    return fm, m.group(2)


def validate_skill(skill_dir: Path, findings: Findings, seen_slugs: dict, seen_names: dict) -> None:
    where = f"skills/{skill_dir.name}"
    manifest = skill_dir / "SKILL.md"
    if not manifest.exists():
        findings.error(f"{where}: missing SKILL.md")
        return

    text = manifest.read_text()
    fm, body = load_frontmatter(text, findings, where)
    if fm is None:
        return

    for key in REQUIRED_FRONTMATTER_KEYS:
        if key not in fm or fm[key] in (None, ""):
            findings.error(f"{where}: front-matter missing required key '{key}'")

    slug = fm.get("slug")
    name = fm.get("name")

    if slug is not None and slug != skill_dir.name:
        findings.error(f"{where}: slug '{slug}' does not match folder name '{skill_dir.name}'")
    if slug is not None and not SLUG_RE.match(str(slug)):
        findings.error(f"{where}: slug '{slug}' is not lowercase-kebab-case")
    if name is not None and name != slug:
        findings.warn(f"{where}: name '{name}' differs from slug '{slug}'")

    if slug is not None:
        if slug in seen_slugs:
            findings.error(f"{where}: duplicate slug '{slug}' also used by {seen_slugs[slug]}")
        else:
            seen_slugs[slug] = where
    if name is not None:
        if name in seen_names:
            findings.error(f"{where}: duplicate name '{name}' also used by {seen_names[name]}")
        else:
            seen_names[name] = where

    technique = fm.get("technique")
    if technique is not None and technique not in ALLOWED_TECHNIQUES:
        findings.error(f"{where}: technique '{technique}' not in {sorted(ALLOWED_TECHNIQUES)}")

    version = fm.get("version")
    if version is not None and not SEMVER_RE.match(str(version)):
        findings.error(f"{where}: version '{version}' is not semver (X.Y.Z)")

    license_ = fm.get("license")
    if license_ is not None and license_ not in KNOWN_LICENSES:
        findings.warn(f"{where}: license '{license_}' not in common SPDX set {sorted(KNOWN_LICENSES)} (check spelling)")

    tool_call = fm.get("tool_call")
    if tool_call is not None and not TOOL_CALL_RE.match(str(tool_call)):
        findings.error(f"{where}: tool_call '{tool_call}' should be snake_case")

    tags = fm.get("tags")
    if tags is not None and (not isinstance(tags, list) or not all(isinstance(t, str) for t in tags)):
        findings.error(f"{where}: tags must be a list of strings")

    for section in REQUIRED_BODY_SECTIONS:
        if section not in body:
            findings.error(f"{where}: body missing required section '{section}'")

    # Usage section JSON block should match the example and tool_call
    usage_json = None
    m = re.search(r"## Usage\s*\n```json\s*\n(.*?)\n```", body, re.DOTALL)
    if m:
        try:
            usage_json = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            findings.error(f"{where}: Usage JSON block is invalid JSON ({e})")
    else:
        findings.warn(f"{where}: Usage section has no fenced json block")

    if usage_json is not None and tool_call is not None:
        if usage_json.get("tool") != tool_call:
            findings.error(
                f"{where}: Usage JSON tool '{usage_json.get('tool')}' != tool_call '{tool_call}'"
            )

    # examples/invoke.json
    example_path = skill_dir / "examples" / "invoke.json"
    if not example_path.exists():
        findings.error(f"{where}: missing examples/invoke.json")
    else:
        try:
            example = json.loads(example_path.read_text())
        except json.JSONDecodeError as e:
            findings.error(f"{where}: examples/invoke.json is invalid JSON ({e})")
            example = None
        if example is not None:
            if "tool" not in example or "arguments" not in example:
                findings.error(f"{where}: examples/invoke.json must have 'tool' and 'arguments' keys")
            elif tool_call is not None and example["tool"] != tool_call:
                findings.error(
                    f"{where}: examples/invoke.json tool '{example['tool']}' != tool_call '{tool_call}'"
                )
            if "arguments" in example and not isinstance(example["arguments"], dict):
                findings.error(f"{where}: examples/invoke.json 'arguments' must be an object")

    # fixtures/ referenced by examples or Reproducibility must actually exist and be non-empty
    if "fixtures/" in text:
        fixtures_dir = skill_dir / "fixtures"
        if not fixtures_dir.exists():
            findings.error(f"{where}: references fixtures/ but no fixtures/ directory exists in this skill")
        elif not any(fixtures_dir.rglob("*")):
            findings.error(f"{where}: fixtures/ directory exists but is empty")
        elif not (fixtures_dir / "sample" / "input.json").exists():
            findings.warn(f"{where}: fixtures/ exists but has no fixtures/sample/input.json")

    # Reproducibility tooling must exist for the declared runtime
    runtime = str(fm.get("runtime", "")).split()[0] if fm.get("runtime") else None
    tooling = RUNTIME_TOOLING.get(runtime)
    if runtime is not None and tooling is None:
        findings.warn(f"{where}: runtime '{runtime}' has no known verify/deps convention in this validator")
    elif tooling is not None:
        if not (skill_dir / tooling["verify"]).exists():
            findings.error(f"{where}: missing {tooling['verify']} (required for runtime '{runtime}')")
        if not (skill_dir / tooling["deps"]).exists():
            findings.error(f"{where}: missing {tooling['deps']} (required for runtime '{runtime}')")


def run_reproducibility(skill_dir: Path, findings: Findings) -> None:
    """Actually execute the skill's Reproducibility bash block from repo root."""
    where = f"skills/{skill_dir.name}"
    manifest = skill_dir / "SKILL.md"
    if not manifest.exists():
        return
    text = manifest.read_text()
    m = re.search(r"## Reproducibility\b.*?```bash\s*\n(.*?)\n```", text, re.DOTALL)
    if not m:
        findings.error(f"{where}: no fenced bash block found under ## Reproducibility")
        return
    script = m.group(1)
    proc = subprocess.run(
        ["bash", "-c", script], cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0:
        tail = "\n".join((proc.stdout + proc.stderr).splitlines()[-15:])
        findings.error(f"{where}: reproducibility command exited {proc.returncode}:\n{tail}")


def validate_readme_index(skill_slugs: set[str], findings: Findings) -> None:
    if not README.exists():
        findings.error("README.md is missing")
        return
    text = README.read_text()
    listed = set(re.findall(r"\[`([a-z0-9-]+)`\]\(skills/([a-z0-9-]+)/SKILL\.md\)", text))
    listed_slugs = {a for a, b in listed if a == b}
    # also catch mismatched link text vs path
    for link_text, link_path in re.findall(r"\[`([a-z0-9-]+)`\]\(skills/([a-z0-9-]+)/SKILL\.md\)", text):
        if link_text != link_path:
            findings.error(f"README.md: link text '{link_text}' does not match link path 'skills/{link_path}/SKILL.md'")

    missing_from_readme = skill_slugs - listed_slugs
    extra_in_readme = listed_slugs - skill_slugs
    for slug in sorted(missing_from_readme):
        findings.error(f"README.md: skill '{slug}' exists but is not listed in the ## Skills index")
    for slug in sorted(extra_in_readme):
        findings.error(f"README.md: index lists '{slug}' but no such skill directory exists")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument(
        "--run", action="store_true",
        help="also execute each skill's Reproducibility command and require it to exit 0",
    )
    args = parser.parse_args()

    findings = Findings()
    seen_slugs: dict[str, str] = {}
    seen_names: dict[str, str] = {}

    if not SKILLS_DIR.exists():
        print("skills/ directory not found", file=sys.stderr)
        return 1

    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    for skill_dir in skill_dirs:
        validate_skill(skill_dir, findings, seen_slugs, seen_names)

    validate_readme_index({p.name for p in skill_dirs}, findings)

    if args.run:
        print("Executing each skill's Reproducibility command (--run)...")
        for skill_dir in skill_dirs:
            run_reproducibility(skill_dir, findings)

    total = len(skill_dirs)
    print(f"Validated {total} skill(s) under skills/\n")

    if findings.errors:
        print(f"ERRORS ({len(findings.errors)}):")
        for e in findings.errors:
            print(f"  - {e}")
        print()
    if findings.warnings:
        print(f"WARNINGS ({len(findings.warnings)}):")
        for w in findings.warnings:
            print(f"  - {w}")
        print()

    if not findings.errors and not findings.warnings:
        print("All checks passed cleanly.")

    if findings.errors or (args.strict and findings.warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
