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
    "examples/README.md",
    "examples/past_life_demo.json",
    "examples/past_life_demo.md",
    "examples/cringe_archaeology_demo.json",
    "examples/cringe_archaeology_demo.md",
    "examples/ai_clone_demo.json",
    "examples/ai_clone_demo.md",
    "examples/legacy_audit_demo.json",
    "examples/legacy_audit_demo.md",
    "examples/epitaph_demo.json",
    "examples/epitaph_demo.md",
    "scripts/profile-manager.py",
    "scripts/validate-skill.py",
]

EXAMPLE_JSON_FILES = [
    "examples/past_life_demo.json",
    "examples/cringe_archaeology_demo.json",
    "examples/ai_clone_demo.json",
    "examples/legacy_audit_demo.json",
    "examples/epitaph_demo.json",
]

GITIGNORE_RULES = [
    "profiles/*.json",
    "profiles/*.md",
    "!profiles/README.md",
    "profiles/history/*",
    "!profiles/history/.gitkeep",
]

GITATTRIBUTES_RULES = [
    "* text=auto",
    "*.md text eol=lf",
    "*.json text eol=lf",
    "*.yaml text eol=lf",
    "*.svg text eol=lf",
]


def main() -> int:
    """Validate skill contract, templates, examples, and gitignore rules."""
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
            return 1

    if not isinstance(contract, dict):
        errors.append(f"Contract must be a JSON object: {CONTRACT_PATH}")
        return 1

    version = contract.get("version")
    if not version:
        errors.append("Contract missing 'version' field")
    elif not isinstance(version, str):
        errors.append(f"Contract 'version' must be a string, got: {type(version).__name__}")

    naming = contract.get("naming")
    if not isinstance(naming, dict):
        errors.append("Contract missing 'naming' object")
    else:
        required_naming_keys = {"current_json", "current_md", "history_json", "history_md"}
        for key in required_naming_keys:
            if key not in naming:
                errors.append(f"Contract naming missing key: {key}")

    for path_key in ("profile_root", "history_root", "templates_root"):
        value = contract.get(path_key)
        if not value:
            errors.append(f"Contract missing '{path_key}' field")
        elif not isinstance(value, str):
            errors.append(f"Contract '{path_key}' must be a string")
        elif not (root / value).is_dir():
            errors.append(f"Contract '{path_key}' directory does not exist: {value}")

    skills = contract.get("skills")
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

            if "slug" not in template:
                errors.append(f"Template missing 'slug' field: {template_path.as_posix()}")

            if "updated_at" not in template:
                errors.append(f"Template missing 'updated_at' field: {template_path.as_posix()}")

            if "confidence" not in template:
                errors.append(f"Template missing 'confidence' field: {template_path.as_posix()}")

            if "source_summary" not in template:
                errors.append(f"Template missing 'source_summary' field: {template_path.as_posix()}")
            elif not isinstance(template["source_summary"], dict):
                errors.append(f"Template 'source_summary' must be an object: {template_path.as_posix()}")

            if "version" not in template:
                errors.append(f"Template missing 'version' field: {template_path.as_posix()}")
            elif not isinstance(template["version"], int):
                errors.append(f"Template 'version' must be an integer: {template_path.as_posix()}")

            if "corrections" not in template:
                errors.append(f"Template missing 'corrections' field: {template_path.as_posix()}")
            elif not isinstance(template["corrections"], list):
                errors.append(f"Template 'corrections' must be a list: {template_path.as_posix()}")

            if "persona" not in template:
                errors.append(f"Template missing 'persona' field: {template_path.as_posix()}")
            elif not isinstance(template["persona"], dict):
                errors.append(f"Template 'persona' must be an object: {template_path.as_posix()}")
            else:
                persona = template["persona"]
                required_persona_layers = {
                    "layer0_rules",
                    "layer1_identity",
                    "layer2_expression",
                    "layer3_decision_model",
                    "layer4_boundaries",
                }
                for layer in required_persona_layers:
                    if layer not in persona:
                        errors.append(f"Template persona missing '{layer}': {template_path.as_posix()}")

            has_question = "existential_question" in template
            has_questions = "existential_questions" in template
            if not has_question and not has_questions:
                errors.append(f"Template missing 'existential_question' or 'existential_questions': {template_path.as_posix()}")
            elif has_question and not isinstance(template["existential_question"], str):
                errors.append(f"Template 'existential_question' must be a string: {template_path.as_posix()}")
            elif has_questions and not isinstance(template["existential_questions"], list):
                errors.append(f"Template 'existential_questions' must be a list: {template_path.as_posix()}")

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
                if not isinstance(example, dict):
                    errors.append(f"Example JSON must be an object: {relative_path}")
                elif "skill" not in example:
                    errors.append(f"Example JSON missing 'skill' field: {relative_path}")
                elif "slug" not in example:
                    errors.append(f"Example JSON missing 'slug' field: {relative_path}")
                else:
                    skill_slug = example["skill"]
                    skill_entry = next((s for s in skills if s.get("slug") == skill_slug), None)
                    if skill_entry:
                        for key in skill_entry.get("required_top_level_keys", []):
                            if key not in example:
                                errors.append(f"Example JSON missing required key '{key}': {relative_path}")
            except json.JSONDecodeError:
                errors.append(f"Invalid example JSON: {relative_path}")

    gitignore_path = root / ".gitignore"
    if gitignore_path.exists():
        gitignore_lines = gitignore_path.read_text(encoding="utf-8").splitlines()
        for rule in GITIGNORE_RULES:
            if rule not in gitignore_lines:
                errors.append(f".gitignore missing rule: {rule}")

    gitattributes_path = root / ".gitattributes"
    if gitattributes_path.exists():
        gitattributes_lines = gitattributes_path.read_text(encoding="utf-8").splitlines()
        for rule in GITATTRIBUTES_RULES:
            if rule not in gitattributes_lines:
                errors.append(f".gitattributes missing rule: {rule}")

    if errors:
        print("Validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Validation passed:")
    print(f"- skills: {len(skills)}")
    print("- skill contract is valid and paths are consistent")
    print("- prompts / layer0 / references / templates are present")
    print("- profiles layout and privacy ignore rules are in place")
    print("- agents metadata, icon assets, example outputs, and scripts are present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
