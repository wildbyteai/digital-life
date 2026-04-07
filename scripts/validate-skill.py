#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SLUG_RE = re.compile(r"^[a-z0-9_]+$")
CONTRACT_PATH = "profiles/contracts/skill-contract.json"

REQUIRED_ROOT_FILES = [
    "README.md",
    "SKILL.md",
    "LICENSE",
    "VERSION",
    "CHANGELOG.md",
    ".gitignore",
    ".gitattributes",
    "agents/openai.yaml",
    "assets/digital-life-small.svg",
    "assets/digital-life-large.svg",
    "profiles/README.md",
    "profiles/history/.gitkeep",
    CONTRACT_PATH,
    "prompts/persona_builder.md",
    "prompts/evolution.md",
    "examples/README.md",
    "examples/legacy_audit_demo.json",
    "examples/legacy_audit_demo.md",
    "examples/ai_clone_demo.json",
    "examples/ai_clone_demo.md",
    "examples/past_life_demo.json",
    "examples/past_life_demo.md",
    "examples/cringe_archaeology_demo.json",
    "examples/cringe_archaeology_demo.md",
    "examples/epitaph_demo.json",
    "examples/epitaph_demo.md",
    "scripts/profile-manager.py",
    "scripts/validate-skill.py",
]

EXAMPLE_JSON_FILES = [
    "examples/legacy_audit_demo.json",
    "examples/ai_clone_demo.json",
    "examples/past_life_demo.json",
    "examples/cringe_archaeology_demo.json",
    "examples/epitaph_demo.json",
]

GITIGNORE_RULES = [
    "profiles/*.json",
    "profiles/*.md",
    "!profiles/README.md",
    "profiles/history/*",
    "!profiles/history/.gitkeep",
]


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    errors: list[str] = []

    for relative_path in REQUIRED_ROOT_FILES:
        if not (root / relative_path).exists():
            errors.append(f"Missing file or directory: {relative_path}")

    contract: dict = {}
    contract_file = root / CONTRACT_PATH
    if contract_file.exists():
        try:
            contract = json.loads(contract_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            errors.append(f"Invalid JSON contract: {CONTRACT_PATH}")

    skills = contract.get("skills") if isinstance(contract, dict) else None
    if not isinstance(skills, list) or not skills:
        errors.append("Contract must contain a non-empty 'skills' list")
        skills = []

    seen_slugs: set[str] = set()
    required_contract_keys = {
        "slug",
        "display_name",
        "triggers",
        "prompt_path",
        "layer0_path",
        "reference_path",
        "template_path",
        "required_top_level_keys",
    }

    for item in skills:
        if not isinstance(item, dict):
            errors.append("Contract skill item must be an object")
            continue

        missing_keys = sorted(k for k in required_contract_keys if k not in item)
        if missing_keys:
            errors.append(f"Contract skill item missing keys: {', '.join(missing_keys)}")
            continue

        slug = str(item["slug"])
        if not SLUG_RE.match(slug):
            errors.append(f"Invalid skill slug: {slug}")
            continue
        if slug in seen_slugs:
            errors.append(f"Duplicate skill slug in contract: {slug}")
            continue
        seen_slugs.add(slug)

        triggers = item.get("triggers")
        if not isinstance(triggers, list) or not triggers:
            errors.append(f"Skill '{slug}' must define non-empty triggers list")

        required_keys = item.get("required_top_level_keys")
        if not isinstance(required_keys, list) or not required_keys:
            errors.append(f"Skill '{slug}' must define required_top_level_keys list")

        for path_key in ("prompt_path", "layer0_path", "reference_path", "template_path"):
            relative_path = str(item[path_key])
            if not (root / relative_path).exists():
                errors.append(f"Missing file or directory: {relative_path}")

        template_path = root / str(item["template_path"])
        if template_path.exists():
            try:
                template = json.loads(template_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                errors.append(f"Invalid JSON template: {template_path.as_posix()}")
                continue

            if template.get("skill") != slug:
                errors.append(f"Template skill field mismatch: {template_path.as_posix()} -> {template.get('skill')}")

            if isinstance(required_keys, list):
                for key in required_keys:
                    if key not in template:
                        errors.append(
                            f"Required key '{key}' missing in template: {template_path.as_posix()}"
                        )

    for relative_path in EXAMPLE_JSON_FILES:
        full_path = root / relative_path
        if full_path.exists():
            try:
                example = json.loads(full_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                errors.append(f"Invalid example JSON: {relative_path}")
                continue

            ex_skill = example.get("skill")
            matching = [s for s in skills if s.get("slug") == ex_skill]
            if matching:
                required_keys = matching[0].get("required_top_level_keys", [])
                for key in required_keys:
                    if key not in example:
                        errors.append(
                            f"Example '{relative_path}' missing required key: {key}"
                        )

    for item in skills:
        slug = str(item.get("slug", ""))
        prompt_path = root / str(item.get("prompt_path", ""))
        if prompt_path.exists():
            prompt_text = prompt_path.read_text(encoding="utf-8")
            layer0_ref = str(item.get("layer0_path", ""))
            ref_ref = str(item.get("reference_path", ""))
            if layer0_ref and layer0_ref not in prompt_text:
                errors.append(
                    f"Prompt '{item['prompt_path']}' does not reference layer0 path: {layer0_ref}"
                )
            if ref_ref and ref_ref not in prompt_text:
                errors.append(
                    f"Prompt '{item['prompt_path']}' does not reference reference path: {ref_ref}"
                )

    gitignore_path = root / ".gitignore"
    if gitignore_path.exists():
        gitignore_lines = gitignore_path.read_text(encoding="utf-8").splitlines()
        for rule in GITIGNORE_RULES:
            if rule not in gitignore_lines:
                errors.append(f".gitignore missing rule: {rule}")

    if errors:
        print("Validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Validation passed:")
    print(f"- skills: {len(skills)}")
    print("- skill contract is valid and paths are consistent")
    print("- prompts / layer0 / references / templates are present")
    print("- prompt cross-references to layer0 and references are verified")
    print("- shared prompts (persona_builder, evolution) are present")
    print("- profiles layout and privacy ignore rules are in place")
    print("- agents metadata, icon assets, example outputs, and scripts are present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
