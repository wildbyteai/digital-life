#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


SKILL_MAP = [
    {"slug": "past_life", "reference": "past-life"},
    {"slug": "cringe_archaeology", "reference": "cringe-archaeology"},
    {"slug": "ai_clone", "reference": "ai-clone"},
    {"slug": "legacy_audit", "reference": "legacy-audit"},
    {"slug": "epitaph", "reference": "epitaph"},
]

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
    "examples/README.md",
    "examples/legacy_audit_demo.json",
    "examples/legacy_audit_demo.md",
    "examples/ai_clone_demo.json",
    "examples/ai_clone_demo.md",
]

EXAMPLE_JSON_FILES = [
    "examples/legacy_audit_demo.json",
    "examples/ai_clone_demo.json",
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

    for entry in SKILL_MAP:
        for relative_path in (
            f"layer0/{entry['slug']}.md",
            f"prompts/{entry['slug']}.md",
            f"profiles/templates/{entry['slug']}.json",
            f"references/{entry['reference']}.md",
        ):
            if not (root / relative_path).exists():
                errors.append(f"Missing file or directory: {relative_path}")

        template_path = root / f"profiles/templates/{entry['slug']}.json"
        if template_path.exists():
            try:
                template = json.loads(template_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                errors.append(f"Invalid JSON template: {template_path.as_posix()}")
            else:
                if template.get("skill") != entry["slug"]:
                    errors.append(
                        f"Template skill field mismatch: {template_path.as_posix()} -> {template.get('skill')}"
                    )

    for relative_path in EXAMPLE_JSON_FILES:
        full_path = root / relative_path
        if full_path.exists():
            try:
                json.loads(full_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                errors.append(f"Invalid example JSON: {relative_path}")

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
    print(f"- skills: {len(SKILL_MAP)}")
    print("- prompts / layer0 / references / templates are present")
    print("- profiles layout and privacy ignore rules are in place")
    print("- agents metadata, icon assets, and example outputs are present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
