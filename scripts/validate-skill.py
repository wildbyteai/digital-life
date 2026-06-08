#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
import subprocess
import sys

from validation_rules import validate_distilled_life, validate_persona, validate_source_summary

SLUG_RE = re.compile(r"^[a-z0-9_-]+$")
CONTRACT_PATH = "profiles/contracts/skill-contract.json"

REQUIRED_CONTRACT_KEYS = {
    "slug",
    "display_name",
    "triggers",
    "prompt_path",
    "layer0_path",
    "reference_path",
    "template_path",
    "required_top_level_keys",
}

REQUIRED_TEMPLATE_FIELDS = {
    "slug": str,
    "updated_at": str,
    "confidence": str,
    "source_summary": dict,
    "version": int,
    "corrections": list,
    "persona": dict,
}

REQUIRED_PERSONA_LAYERS = {
    "layer0_rules",
    "layer1_identity",
    "layer2_expression",
    "layer3_decision_model",
    "layer4_boundaries",
}

REQUIRED_NAMING_KEYS = {"current_json", "current_md", "history_json", "history_md"}

REQUIRED_ROOT_FILES = [
    "README.md",
    "SKILL.md",
    "LICENSE",
    "VERSION",
    "CHANGELOG.md",
    ".gitignore",
    ".gitattributes",
    ".github/workflows/validate.yml",
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
    "examples/distilled_life_demo.json",
    "examples/distilled_life_demo.md",
    "scripts/profile-manager.py",
    "scripts/validate-skill.py",
]

EXAMPLE_JSON_FILES = [
    "examples/past_life_demo.json",
    "examples/cringe_archaeology_demo.json",
    "examples/ai_clone_demo.json",
    "examples/legacy_audit_demo.json",
    "examples/epitaph_demo.json",
    "examples/distilled_life_demo.json",
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
    "*.yml text eol=lf",
    "*.svg text eol=lf",
]


def repo_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).resolve().parent.parent


def package_version(root: Path | None = None) -> str:
    """Read the package version from VERSION."""
    version_path = (root or repo_root()) / "VERSION"
    try:
        return version_path.read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate-skill",
        description="Validate skill contract, templates, examples, and gitignore rules.",
    )
    parser.add_argument("root", nargs="?", default=None, help="Repository root path. Defaults to script parent.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {package_version()}")
    return parser


def _extract_skill_frontmatter_version(content: str) -> str | None:
    if not content.startswith("---"):
        return None
    for line in content.splitlines()[1:]:
        if line.strip() == "---":
            return None
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip()
    return None


def _extract_skill_allowed_tools(content: str) -> set[str]:
    """Read allowed-tools from SKILL.md frontmatter."""
    if not content.startswith("---"):
        return set()
    for line in content.splitlines()[1:]:
        if line.strip() == "---":
            return set()
        if line.startswith("allowed-tools:"):
            raw = line.split(":", 1)[1]
            return {item.strip() for item in raw.split(",") if item.strip()}
    return set()


def _contains_bare_python_command(content: str) -> bool:
    """Return True when docs use python for repo scripts instead of python3."""
    return re.search(r"(?<![\w.-])python\s+(?:scripts/|-m\s+(?:py_compile|unittest))", content) is not None


def _count_readme_skill_rows(content: str) -> int:
    return sum(1 for line in content.splitlines() if re.match(r"^\|\s*\d+\s*\|", line))


def _count_skill_trigger_rows(content: str) -> int:
    return sum(1 for line in content.splitlines() if re.match(r"^\|\s*\d+\s*\|", line))


def validate_doc_consistency(root: Path, skills: list[dict], errors: list[str]) -> None:
    """Validate docs, tool declarations, skill counts, and CI command examples stay aligned."""
    skill_count = len(skills)
    docs_to_check = [
        "README.md",
        "SKILL.md",
        "profiles/README.md",
        "prompts/evolution.md",
        ".github/workflows/validate.yml",
    ]
    for relative_path in docs_to_check:
        path = root / relative_path
        if path.exists() and _contains_bare_python_command(path.read_text(encoding="utf-8")):
            errors.append(f"{relative_path} contains bare python command; use python3")

    skill_path = root / "SKILL.md"
    skill_doc = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""
    allowed_tools = _extract_skill_allowed_tools(skill_doc)
    if skill_doc and "WebFetch" in skill_doc and "WebFetch" not in allowed_tools:
        errors.append("SKILL.md references WebFetch but allowed-tools does not include WebFetch")
    if skill_doc and "web_fetch" in skill_doc:
        errors.append("SKILL.md should use canonical WebFetch tool spelling, not web_fetch")
    if skill_doc and "browser" in skill_doc and "browser" not in allowed_tools:
        conditional_browser_phrases = (
            "仅在运行环境提供 browser 工具时",
            "取决于运行环境是否提供该工具",
        )
        if not any(phrase in skill_doc for phrase in conditional_browser_phrases):
            errors.append("SKILL.md references browser as an unconditional tool but allowed-tools does not include browser")

    readme_path = root / "README.md"
    if readme_path.exists():
        readme = readme_path.read_text(encoding="utf-8")
        if f"[{skill_count} 个工具]" not in readme:
            errors.append(f"README.md navigation should reference {skill_count} 个工具")
        if f"## {skill_count} 个数字人生工具" not in readme:
            errors.append(f"README.md skill heading should reference {skill_count} 个数字人生工具")
        readme_rows = _count_readme_skill_rows(readme)
        if readme_rows != skill_count:
            errors.append(f"README.md skill table row count mismatch: expected {skill_count}, got {readme_rows}")
        if "browser" in readme and "如果运行环境提供 browser 工具" not in readme:
            errors.append("README.md browser capability must be documented as conditional on runtime support")

    if skill_doc:
        trigger_rows = _count_skill_trigger_rows(skill_doc)
        if trigger_rows != skill_count:
            errors.append(f"SKILL.md trigger table row count mismatch: expected {skill_count}, got {trigger_rows}")

    workflow_path = root / ".github" / "workflows" / "validate.yml"
    if workflow_path.exists():
        workflow = workflow_path.read_text(encoding="utf-8")
        expected_commands = (
            "python3 -m py_compile scripts/*.py",
            "python3 scripts/validate-skill.py",
            "python3 scripts/profile-manager.py doctor",
            "python3 -m unittest discover -s scripts -p 'test_scripts.py'",
            "python3 scripts/profile-manager.py --version",
            "python3 scripts/validate-skill.py --version",
        )
        for command in expected_commands:
            if command not in workflow:
                errors.append(f".github/workflows/validate.yml missing command: {command}")


def validate_version_consistency(root: Path, errors: list[str]) -> str:
    version = package_version(root)
    if not version or version == "unknown":
        errors.append("VERSION is missing or empty")
        return version

    skill_path = root / "SKILL.md"
    if skill_path.exists():
        skill_version = _extract_skill_frontmatter_version(skill_path.read_text(encoding="utf-8"))
        if skill_version != version:
            errors.append(f"SKILL.md version mismatch: expected {version}, got {skill_version!r}")

    readme_path = root / "README.md"
    if readme_path.exists():
        readme = readme_path.read_text(encoding="utf-8")
        badge_version = version.replace("-", "--")
        if f"version-{badge_version}" not in readme:
            errors.append(f"README.md version badge missing or mismatched for {version}")
        if f"v{version}" not in readme:
            errors.append(f"README.md version section missing v{version}")

    changelog_path = root / "CHANGELOG.md"
    if changelog_path.exists():
        headings = [line for line in changelog_path.read_text(encoding="utf-8").splitlines() if line.startswith("## ")]
        if not headings:
            errors.append("CHANGELOG.md missing version heading")
        elif not headings[0].startswith(f"## {version} "):
            errors.append(f"CHANGELOG.md latest heading mismatch: expected {version}, got {headings[0]!r}")

    script_versions = {
        "scripts/profile-manager.py": [sys.executable, str(root / "scripts" / "profile-manager.py"), "--version"],
        "scripts/validate-skill.py": [sys.executable, str(root / "scripts" / "validate-skill.py"), "--version"],
    }
    for label, command in script_versions.items():
        try:
            output = subprocess.check_output(command, text=True).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            errors.append(f"{label} --version failed: {exc}")
            continue
        if version not in output:
            errors.append(f"{label} --version mismatch: expected {version}, got {output!r}")
    return version


def main() -> int:
    """Validate skill contract, templates, examples, and gitignore rules."""
    parser = build_parser()
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else repo_root()
    errors: list[str] = []

    validate_version_consistency(root, errors)

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
    elif not re.match(r"^\d+\.\d+\.\d+$", str(version)):
        errors.append(f"Contract 'version' must be semver format (e.g. 1.0.0), got: {version!r}")

    naming = contract.get("naming")
    if not isinstance(naming, dict):
        errors.append("Contract missing 'naming' object")
    else:
        for key in REQUIRED_NAMING_KEYS:
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

    validate_doc_consistency(root, skills, errors)

    for item in skills:
        if not isinstance(item, dict):
            errors.append("Contract skill item must be an object")
            continue

        missing_keys = sorted(k for k in REQUIRED_CONTRACT_KEYS if k not in item)
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

        # Validate layer0 file has rules section
        layer0_path = root / str(item["layer0_path"])
        if layer0_path.exists():
            layer0_content = layer0_path.read_text(encoding="utf-8")
            if "## " not in layer0_content:
                errors.append(f"Layer0 file missing section headers: {item['layer0_path']}")
            if len(layer0_content.strip()) < 100:
                errors.append(f"Layer0 file seems too short (< 100 chars): {item['layer0_path']}")
            # Check for bullet points indicating rules
            bullet_count = sum(1 for line in layer0_content.splitlines() if line.strip().startswith("- "))
            if bullet_count < 3:
                errors.append(f"Layer0 file has too few rules (< 3 bullet points): {item['layer0_path']}")

        template_path = root / str(item["template_path"])
        if template_path.exists():
            try:
                template = json.loads(template_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                errors.append(f"Invalid JSON template: {template_path.as_posix()}")
                continue

            if template.get("skill") != slug:
                errors.append(f"Template skill field mismatch: {template_path.as_posix()} -> {template.get('skill')}")

            # Validate template slug placeholder
            if "slug" in template and template["slug"] != "{slug}":
                errors.append(f"Template 'slug' should be '{{slug}}' placeholder: {template_path.as_posix()}")

            # Validate template updated_at placeholder
            if "updated_at" in template and template["updated_at"] != "{ISO8601}":
                errors.append(f"Template 'updated_at' should be '{{ISO8601}}' placeholder: {template_path.as_posix()}")

            for field, expected_type in REQUIRED_TEMPLATE_FIELDS.items():
                if field not in template:
                    errors.append(f"Template missing '{field}' field: {template_path.as_posix()}")
                elif not isinstance(template[field], expected_type):
                    errors.append(f"Template '{field}' must be a {expected_type.__name__}: {template_path.as_posix()}")

            # Validate version is positive
            if "version" in template and isinstance(template["version"], int) and template["version"] < 1:
                errors.append(f"Template 'version' must be >= 1: {template_path.as_posix()}")

            # Validate confidence placeholder
            if "confidence" in template:
                conf = template["confidence"]
                valid_placeholders = ("high", "medium", "low", "high|medium|low")
                if conf not in valid_placeholders:
                    errors.append(f"Template 'confidence' unexpected value: {conf!r}: {template_path.as_posix()}")

            if "persona" in template:
                validate_persona(
                    template["persona"],
                    f"Template {template_path.as_posix()}",
                    errors,
                    strict_nested=(slug == "distilled_life"),
                )

            has_question = "existential_question" in template
            has_questions = "existential_questions" in template
            if not has_question and not has_questions:
                errors.append(f"Template missing 'existential_question' or 'existential_questions': {template_path.as_posix()}")
            elif has_question and not isinstance(template["existential_question"], str):
                errors.append(f"Template 'existential_question' must be a string: {template_path.as_posix()}")
            elif has_questions and not isinstance(template["existential_questions"], list):
                errors.append(f"Template 'existential_questions' must be a list: {template_path.as_posix()}")

            # Validate corrections is empty list in template
            if "corrections" in template and isinstance(template["corrections"], list) and template["corrections"]:
                errors.append(f"Template 'corrections' should be empty list: {template_path.as_posix()}")

            if "source_summary" in template:
                validate_source_summary(
                    template,
                    f"Template {template_path.as_posix()}",
                    errors,
                    template_mode=True,
                )

            if slug == "distilled_life":
                validate_distilled_life(
                    template,
                    f"Template {template_path.as_posix()}",
                    errors,
                    template_mode=True,
                )

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
                    # Check skill field matches filename prefix
                    filename_prefix = Path(relative_path).stem.replace("_demo", "")
                    if skill_slug != filename_prefix:
                        errors.append(f"Example skill '{skill_slug}' doesn't match filename prefix '{filename_prefix}': {relative_path}")

                    # Validate slug format
                    slug = str(example["slug"])
                    if not SLUG_RE.match(slug):
                        errors.append(f"Example 'slug' invalid format: {slug!r}: {relative_path}")

                    skill_entry = next((s for s in skills if s.get("slug") == skill_slug), None)
                    if skill_entry:
                        for key in skill_entry.get("required_top_level_keys", []):
                            if key not in example:
                                errors.append(f"Example JSON missing required key '{key}': {relative_path}")

                    # Validate persona layers in example
                    if "persona" in example:
                        validate_persona(
                            example["persona"],
                            f"Example {relative_path}",
                            errors,
                            strict_nested=(skill_slug == "distilled_life"),
                        )

                    # Validate confidence value in example
                    if "confidence" in example:
                        if example["confidence"] not in ("high", "medium", "low"):
                            errors.append(f"Example 'confidence' invalid: {example['confidence']!r}: {relative_path}")

                    # Validate corrections field in example
                    if "corrections" in example and not isinstance(example["corrections"], list):
                        errors.append(f"Example 'corrections' must be list: {relative_path}")

                    # Validate version field in example
                    if "version" in example and not isinstance(example["version"], int):
                        errors.append(f"Example 'version' must be int: {relative_path}")

                    # Validate source_summary structure in example
                    if "source_summary" in example:
                        validate_source_summary(
                            example,
                            f"Example {relative_path}",
                            errors,
                            template_mode=False,
                        )

                    if skill_slug == "distilled_life":
                        validate_distilled_life(
                            example,
                            f"Example {relative_path}",
                            errors,
                            template_mode=False,
                        )

                    # Validate updated_at is valid ISO 8601 in example
                    if "updated_at" in example:
                        ua = str(example["updated_at"])
                        try:
                            datetime.fromisoformat(ua)
                        except (ValueError, TypeError):
                            errors.append(f"Example 'updated_at' is not valid ISO 8601: {ua!r}: {relative_path}")
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
